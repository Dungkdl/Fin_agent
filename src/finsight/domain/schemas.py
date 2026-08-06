"""Schema dùng chung giữa service/API, hiện có ErrorResponse."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str