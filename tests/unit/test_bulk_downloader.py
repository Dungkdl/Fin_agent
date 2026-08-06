import hashlib
import shutil
import uuid
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from finsight.crawl.downloader import parse_checksum_text, safe_extract_zip, verify_sha256


@contextmanager
def workspace_tmp() -> Iterator[Path]:
    path = Path("tmp") / f"test-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_checksum_verification() -> None:
    with workspace_tmp() as tmp_path:
        path = tmp_path / "sample.zip"
        path.write_bytes(b"hello")
        digest = hashlib.sha256(b"hello").hexdigest()

        assert parse_checksum_text(f"{digest}  sample.zip") == digest
        assert verify_sha256(path, f"{digest}  sample.zip") is True


def test_safe_extract_zip() -> None:
    with workspace_tmp() as tmp_path:
        zip_path = tmp_path / "safe.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("BTCUSDT-15m.csv", "1,2,3")

        extracted = safe_extract_zip(zip_path, tmp_path / "out")

        assert len(extracted) == 1
        assert extracted[0].name == "BTCUSDT-15m.csv"
        assert extracted[0].read_text(encoding="utf-8") == "1,2,3"


def test_safe_extract_zip_rejects_zip_slip() -> None:
    with workspace_tmp() as tmp_path:
        zip_path = tmp_path / "bad.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("../escape.csv", "bad")

        with pytest.raises(ValueError, match="Unsafe ZIP member path"):
            safe_extract_zip(zip_path, tmp_path / "out")