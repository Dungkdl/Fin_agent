"""Exception chung của FinSight để sau này API/service xử lý lỗi nhất quán."""

class FinSightError(Exception):
    """Base exception for FinSight Agent."""


class ConfigurationError(FinSightError):
    """Raised when runtime configuration is invalid."""


class ProviderError(FinSightError):
    """Raised when a market-data provider request fails."""