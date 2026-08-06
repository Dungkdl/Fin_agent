"""Schema chung cho mọi expert.

Mục tiêu của file này là ép Quant, News, Fundamental và Fusion trả output cùng một kiểu.
Nhờ vậy API hoặc Fusion service không cần biết chi tiết nội bộ của từng expert.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ExpertName(StrEnum):
    QUANT = "quant"
    NEWS = "news"
    FUNDAMENTAL = "fundamental"
    FUSION = "fusion"

# Class này định nghĩa các kết luận mà một expert có thể đưa ra
class ExpertDirection(StrEnum):
    BULLISH = "bullish"             # Xu hướng tăng
    SIDEWAYS = "sideways"           # Đi ngang hoặc trung tính
    BEARISH = "bearish"             # Xu hướng giảm
    NO_ACTION = "no_action"         # Không nên hành động
    UNKNOWN = "unknown"             # Chưa xác định được

# Class này biểu diễn một bằng chứng hoặc nguồn dữ liệu được expert sử dụng
class ExpertEvidence(BaseModel):
    source: str
    title: str | None = None
    description: str | None = None
    url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

# Class này chứa xác suất của ba lớp dự báo.
class ExpertProbabilities(BaseModel):
    bullish: float
    sideways: float
    bearish: float

    @field_validator("bullish", "sideways", "bearish")
    @classmethod
    def probability_in_range(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("probability must be in [0, 1]")
        return value

    def total(self) -> float:
        return self.bullish + self.sideways + self.bearish

# Class này định nghĩa toàn bộ thông tin mà một expert có thể trả về
class ExpertOutput(BaseModel):
    expert_name: ExpertName
    asset_type: str
    symbol: str
    interval: str | None = None         # Khung dữ liệu đầu vào 
    forecast_horizon: str | None = None     # Khung dữ liệu dự báo  
    available: bool                            # expert có cung cấp được kết quả không
    predicted_class: ExpertDirection = ExpertDirection.UNKNOWN  
    confidence: float | None = None             # Mức độ tin cậy 
    uncertainty: float | None = None            # Mức độ k chắc chắn 
    freshness: float | None = None              # Thể hiện mức độ mới của dữ liệu 
    probabilities: ExpertProbabilities | None = None  # Xác suất của từng kết luận 
    expected_return: float | None = None            # Lợi suất kỳ vọng
    expected_volatility: float | None = None        # Độ biến động kỳ vọng trong khoảng dự báo. 
    model_version: str | None = None
    evidence: list[ExpertEvidence] = Field(default_factory=list)   # Bằng chứng 
    warnings: list[str] = Field(default_factory=list)               # Cảnh báo 
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence", "uncertainty", "freshness")
    @classmethod
    def optional_score_in_range(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("score must be in [0, 1]")
        return value