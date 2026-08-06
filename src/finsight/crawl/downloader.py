"""Downloader cho Binance Public Data ZIP. File này tải ZIP/CHECKSUM, verify SHA-256 và giải nén an toàn."""

import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from finsight.config.crawl_config import BulkDownloadConfig
from finsight.crawl.binance.public_data_client import BinancePublicDataFile


@dataclass(frozen=True)
class DownloadResult:
    url: str
    path: Path
    checksum_path: Path
    downloaded: bool
    checksum_valid: bool


class ChecksumVerifier:
    def sha256_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def parse_checksum_text(self, text: str) -> str:
        first_token = text.strip().split()[0]
        if len(first_token) != 64:
            raise ValueError("Checksum file does not start with a SHA-256 digest")
        return first_token.lower()

    def verify(self, path: Path, checksum_text: str) -> bool:
        return self.sha256_file(path) == self.parse_checksum_text(checksum_text)


class SafeZipExtractor:
    def extract(self, zip_path: Path, destination: Path) -> list[Path]:
        destination.mkdir(parents=True, exist_ok=True)
        extracted: list[Path] = []
        destination_root = destination.resolve()

        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                target_path = (destination / member.filename).resolve()
                if destination_root != target_path and destination_root not in target_path.parents:
                    raise ValueError(f"Unsafe ZIP member path: {member.filename}")
                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target_path.open("wb") as target:
                    target.write(source.read())
                extracted.append(target_path)

        return extracted


class BulkDownloader:
    def __init__(
        self,
        config: BulkDownloadConfig = BulkDownloadConfig(),
        checksum_verifier: ChecksumVerifier | None = None,
    ) -> None:
        self.config = config
        self.checksum_verifier = checksum_verifier or ChecksumVerifier()

    def local_paths(self, file: BinancePublicDataFile) -> tuple[Path, Path]:
        partition = (
            self.config.bronze_root
            / f"symbol={file.symbol}"
            / f"interval={file.interval}"
            / f"year={file.year:04d}"
            / f"month={file.month:02d}"
        )
        zip_path = partition / file.filename
        checksum_path = partition / f"{file.filename}.CHECKSUM"
        return zip_path, checksum_path

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _download_text(self, client: httpx.AsyncClient, url: str) -> str:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _download_bytes(self, client: httpx.AsyncClient, url: str) -> bytes:
        response = await client.get(url)
        response.raise_for_status()
        return response.content

    async def download(self, file: BinancePublicDataFile, dry_run: bool = False) -> DownloadResult:
        zip_path, checksum_path = self.local_paths(file)
        if dry_run:
            return DownloadResult(file.url, zip_path, checksum_path, downloaded=False, checksum_valid=False)

        zip_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            checksum_text = await self._download_text(client, file.checksum_url)
            if zip_path.exists() and self.checksum_verifier.verify(zip_path, checksum_text):
                checksum_path.write_text(checksum_text, encoding="utf-8")
                return DownloadResult(file.url, zip_path, checksum_path, downloaded=False, checksum_valid=True)

            zip_path.write_bytes(await self._download_bytes(client, file.url))
            checksum_path.write_text(checksum_text, encoding="utf-8")
            checksum_valid = self.checksum_verifier.verify(zip_path, checksum_text)
            if not checksum_valid:
                zip_path.unlink(missing_ok=True)
                raise ValueError(f"Checksum verification failed for {file.url}")

        return DownloadResult(file.url, zip_path, checksum_path, downloaded=True, checksum_valid=True)


_checksum_verifier = ChecksumVerifier()
_zip_extractor = SafeZipExtractor()


def sha256_file(path: Path) -> str:
    return _checksum_verifier.sha256_file(path)


def parse_checksum_text(text: str) -> str:
    return _checksum_verifier.parse_checksum_text(text)


def verify_sha256(path: Path, checksum_text: str) -> bool:
    return _checksum_verifier.verify(path, checksum_text)


def safe_extract_zip(zip_path: Path, destination: Path) -> list[Path]:
    return _zip_extractor.extract(zip_path, destination)