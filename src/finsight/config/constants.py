"""Hằng số cấp sản phẩm: interval hỗ trợ, model task, required/candidate symbols, stablecoin và leveraged token markers."""

SUPPORTED_CHART_INTERVALS = ("1m", "5m", "15m", "1h", "4h", "1d", "1w")
SUPPORTED_PREDICTION_INTERVALS = ("15m", "1h", "1d")

MODEL_TASKS = {
    "15m": {
        "forecast_horizon": "1h",
        "forecast_steps": 4,
        "model_name": "crypto_quant_15m_1h",
    },
    "1h": {
        "forecast_horizon": "4h",
        "forecast_steps": 4,
        "model_name": "crypto_quant_1h_4h",
    },
    "1d": {
        "forecast_horizon": "5d",
        "forecast_steps": 5,
        "model_name": "crypto_quant_1d_5d",
    },
}

REQUIRED_SYMBOLS = ("BTCUSDT", "ETHUSDT")
CANDIDATE_SYMBOLS = (
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "LINKUSDT",
)

STABLECOIN_ASSETS = {
    "USDT",
    "USDC",
    "FDUSD",
    "TUSD",
    "BUSD",
    "DAI",
    "USDP",
    "USD1",
    "RLUSD",
    "EUR",
    "AEUR",
}

LEVERAGED_TOKEN_MARKERS = (
    "UP",
    "DOWN",
    "BULL",
    "BEAR",
    "3L",
    "3S",
    "4L",
    "4S",
    "5L",
    "5S",
)

