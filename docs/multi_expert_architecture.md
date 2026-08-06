# Multi Expert Architecture

Repo đã chuẩn bị để bổ sung nhiều expert mà không làm rối Quant.

## Cấu Trúc

```text
src/finsight/
├── cli/
├── config/
├── crawl/
├── database/
├── domain/
│   └── expert.py          # schema chung cho mọi expert
└── experts/
    ├── quant/             # Quant Expert
    ├── news/              # News Expert
    ├── fundamental/       # Fundamental Expert
    └── fusion/            # Fusion/Gating Expert
```

## Nguyên Tắc

Mỗi expert có thể có logic riêng, nhưng output phải dùng schema chung:

```text
src/finsight/domain/expert.py
```

Schema quan trọng:

- `ExpertName`
- `ExpertDirection`
- `ExpertEvidence`
- `ExpertProbabilities`
- `ExpertOutput`

Nhờ vậy API/Fusion có thể nhận output từ nhiều expert mà không cần biết bên trong từng expert viết thế nào.

## Khi Thêm Expert Mới

Ví dụ thêm News Expert:

```text
src/finsight/experts/news/
```

Nên có:

```text
schemas.py    # schema riêng nếu cần
features.py   # feature/sentiment/evidence
service.py    # hàm chính gọi expert
```

Nếu News cần crawl dữ liệu riêng, thêm vào:

```text
src/finsight/crawl/news/
```

Nếu News cần lưu dữ liệu riêng, thêm vào:

```text
src/finsight/database/news_storage.py
```

Nhưng output cuối vẫn nên là:

```python
ExpertOutput(expert_name="news", ...)
```

## Luồng Sau Này

```text
API hoặc CLI
  ↓
QuantExpertService
NewsExpertService
FundamentalExpertService
  ↓
FusionExpertService
  ↓
ExpertOutput cuối cùng
```

## Vì Sao Không Để Tất Cả Trong quant

Vì Quant chỉ là một expert. Nếu sau này thêm News/Fundamental/Fusion mà để ngang hàng lung tung, repo sẽ khó đọc.

Cách hiện tại rõ hơn:

```text
experts/quant
experts/news
experts/fundamental
experts/fusion
```