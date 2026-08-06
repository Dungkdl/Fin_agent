"""Entrypoint FastAPI. Hiện có health check tối thiểu; API Quant đầy đủ sẽ được triển khai ở phase sau."""

try:
    from fastapi import FastAPI
except ImportError as exc:  # pragma: no cover - FastAPI is introduced in the API phase.
    raise RuntimeError("Install FastAPI before running the API app") from exc

app = FastAPI(title="FinSight Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}