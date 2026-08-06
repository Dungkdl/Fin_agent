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


class ExpertDirection(StrEnum):
    BULLISH = "bullish"
    SIDEWAYS = "sideways"
    BEARISH = "bearish"
    NO_ACTION = "no_action"
    UNKNOWN = "unknown"


class ExpertEvidence(BaseModel):
    source: str
    title: str | None = None
    description: str | None = None
    url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class ExpertOutput(BaseModel):
    expert_name: ExpertName
    asset_type: str
    symbol: str
    interval: str | None = None
    forecast_horizon: str | None = None
    available: bool
    predicted_class: ExpertDirection = ExpertDirection.UNKNOWN
    confidence: float | None = None
    uncertainty: float | None = None
    freshness: float | None = None
    probabilities: ExpertProbabilities | None = None
    expected_return: float | None = None
    expected_volatility: float | None = None
    model_version: str | None = None
    evidence: list[ExpertEvidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence", "uncertainty", "freshness")
    @classmethod
    def optional_score_in_range(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("score must be in [0, 1]")
        return value