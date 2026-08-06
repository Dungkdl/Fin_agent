# Quant Expert

Phase 3 sẽ triển khai Quant Expert ở đây.

Dự kiến cấu trúc đơn giản:

```text
features.py   # tạo feature từ Candle/Silver data
labels.py     # tạo nhãn bullish/sideways/bearish
dataset.py    # tạo gold training samples
models.py     # wrapper model/baseline
train.py      # training pipeline
predict.py    # inference pipeline
service.py    # service gọi từ API/Fusion
schemas.py    # schema riêng nếu cần
```

Quant không nên đọc raw Binance ZIP trực tiếp. Quant nên dùng dữ liệu đã chuẩn hóa từ `crawl/` và `database/`.