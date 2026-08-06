# Experts

Tất cả expert phân tích sẽ nằm trong folder này.

```text
experts/
├── quant/        # tín hiệu định lượng từ OHLCV/features/model
├── news/         # tín hiệu tin tức/sentiment/evidence
├── fundamental/  # tín hiệu cơ bản/on-chain/macro
└── fusion/       # kết hợp nhiều expert thành kết quả cuối
```

Mỗi expert nên trả về schema chung trong `domain/expert.py` để API/Fusion đọc được thống nhất.