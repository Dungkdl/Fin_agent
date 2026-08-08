"""Entity nghiệp vụ dùng chung. Hiện có Candle, là định dạng candle chuẩn mà crawl và quant cùng dùng.
    Định nghĩa Candle có thuộc tính gì"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    # Định danh (Identity)
    exchange: str               # Tên sàn giao dịch (vd: "binance")
    symbol: str                 # Mã cặp giao dịch (vd: "BTCUSDT")
    interval: str               # Khung thời gian của nến (vd: "15m", "1h", "1d")
    
    # Thời gian (Time)
    open_time: datetime         # Thời điểm bắt đầu cây nến (thường tính bằng milliseconds chuẩn UTC)
    close_time: datetime        # Thời điểm kết thúc cây nến (open_time + interval - 1ms)
    
    # Giá cả (Price - OHLC)
    open: float                 # Giá mở cửa
    high: float                 # Giá cao nhất trong phiên
    low: float                  # Giá thấp nhất trong phiên
    close: float                # Giá đóng cửa (giá cuối cùng của phiên)
    
    # Khối lượng và Thanh khoản (Volume)
    base_volume: float          # Khối lượng giao dịch của đồng Base (vd: số lượng BTC được mua/bán)
    quote_volume: float         # Khối lượng giao dịch của đồng Quote (vd: tổng số USDT đã chi ra)
    trade_count: int            # Tổng số lượng lệnh khớp (số lần giao dịch xảy ra)
    
    # Lực mua chủ động (Taker Buy) - Cho biết phe Mua hay phe Bán đang chủ động hơn
    taker_buy_base_volume: float    # Khối lượng đồng Base được mua bởi người chủ động khớp lệnh (Taker)
    taker_buy_quote_volume: float   # Khối lượng đồng Quote (USDT) được phe Mua chủ động chi ra
    
    # Trạng thái và Siêu dữ liệu (Metadata)
    is_closed: bool             # Nến đã đóng hoàn toàn hay chưa (True: nến lịch sử, False: nến đang chạy realtime)
    source: str                 # Nguồn gốc dữ liệu (vd: "binance_monthly_zip", "binance_rest_api", "binance_websocket")
    source_file: str | None = None  # Tên file gốc (nếu load từ file ZIP/CSV lịch sử)
    
    # Kiểm soát Chất lượng (Data Quality)
    quality_status: str = "unknown" # Trạng thái chất lượng (vd: "valid", "invalid", "missing")
    quality_flags: tuple[str, ...] = field(default_factory=tuple)  # Danh sách các mã lỗi nếu nến bị hỏng (vd: ["high_less_than_low", "negative_volume"])