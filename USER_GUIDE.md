# 📖 VSS Integration System - User Guide

## Tổng quan

VSS Integration System là hệ thống tích hợp dữ liệu doanh nghiệp và bảo hiểm xã hội (VSS) toàn diện, giúp xử lý và phân tích thông tin từ mã số thuế (MST).

## 🚀 Bắt đầu nhanh

### Cài đặt và chạy

```bash
# 1. Clone repository
git clone https://github.com/your-org/vss-integration-system.git
cd vss-integration-system

# 2. Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc venv\Scripts\activate  # Windows

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Chạy web interface
python web_server.py

# Truy cập: http://localhost:5000
```

### Hoặc sử dụng Docker

```bash
# Build và chạy với Docker
docker-compose up -d

# Truy cập: http://localhost:5000
```

## 🎯 Sử dụng Web Interface

### 1. Trang chủ

- Giao diện web thân thiện với form nhập MST
- Hỗ trợ xử lý đơn lẻ hoặc batch
- Hiển thị thống kê real-time

### 2. Xử lý MST đơn lẻ

1. **Nhập MST**: Nhập mã số thuế (10-13 chữ số)
2. **Chọn định dạng**: Summary, Detailed, hoặc Full
3. **Nhấn "Xử lý MST"**
4. **Xem kết quả**: Thông tin doanh nghiệp và dữ liệu VSS

### 3. Xử lý hàng loạt

```bash
# Sử dụng command line cho batch processing
python main.py --file mst_list.txt --workers 4 --output results.json
```

## 🔧 Sử dụng Command Line

### Cú pháp cơ bản

```bash
python main.py [options]
```

### Options quan trọng

| Option | Mô tả | Ví dụ |
|--------|-------|-------|
| `--mst MST` | Xử lý MST đơn lẻ | `--mst 110198560` |
| `--file FILE` | Xử lý từ file | `--file msts.txt` |
| `--workers N` | Số worker threads | `--workers 4` |
| `--output FILE` | File output | `--output results.json` |
| `--format FORMAT` | Định dạng output | `--format detailed` |
| `--no-real-apis` | Chỉ dùng dữ liệu giả lập | `--no-real-apis` |

### Ví dụ sử dụng

```bash
# Xử lý MST đơn lẻ
python main.py --mst 110198560

# Xử lý batch với 4 workers
python main.py --file mst_list.txt --workers 4

# Xuất kết quả chi tiết
python main.py --mst 110198560 --format detailed --output result.json

# Test với dữ liệu giả lập
python main.py --mst 110198560 --no-real-apis
```

## 📡 Sử dụng REST API

### Khởi động API server

```bash
python api_docs.py
# Truy cập docs: http://localhost:5001/docs
```

### Endpoints chính

#### POST /api/v1/process
Xử lý thông tin MST

```bash
curl -X POST http://localhost:5001/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"mst": "110198560", "format": "summary"}'
```

**Response:**
```json
{
  "mst": "110198560",
  "success": true,
  "processing_time": 1.23,
  "confidence_score": 0.95,
  "data_quality": "HIGH",
  "source": "real_api",
  "timestamp": "2024-01-01T10:00:00"
}
```

#### POST /api/v1/batch
Xử lý hàng loạt MST

```bash
curl -X POST http://localhost:5001/api/v1/batch \
  -H "Content-Type: application/json" \
  -d '{"msts": ["110198560", "110197454"], "format": "summary"}'
```

#### GET /api/v1/stats
Lấy thống kê hệ thống

```bash
curl http://localhost:5001/api/v1/stats
```

#### GET /api/v1/health
Kiểm tra tình trạng hệ thống

```bash
curl http://localhost:5001/api/v1/health
```

## 🐍 Sử dụng Python API

### Import và khởi tạo

```python
from src.processors.vss_processor import VSSIntegrationProcessor

# Khởi tạo processor
processor = VSSIntegrationProcessor(max_workers=4, use_real_apis=True)
```

### Xử lý MST đơn lẻ

```python
result = processor.process_single_mst("110198560")

print(f"MST: {result.mst}")
print(f"Thành công: {result.success}")
print(f"Điểm tin cậy: {result.confidence_score}")
print(f"Chất lượng dữ liệu: {result.data_quality}")
print(f"Thời gian xử lý: {result.processing_time}s")
```

### Xử lý hàng loạt

```python
msts = ["110198560", "110197454", "110198088"]
results = processor.process_batch(msts)

for result in results:
    if result.success:
        print(f"✅ {result.mst}: {result.confidence_score}")
    else:
        print(f"❌ {result.mst}: {result.error}")
```

### Lấy thống kê

```python
metrics = processor.get_metrics()
print(f"Đã xử lý: {metrics.total_processed}")
print(f"Thành công: {metrics.successful}")
print(f"Tỷ lệ thành công: {metrics.success_rate}%")
```

## 📊 Hiểu kết quả

### ProcessingResult

| Field | Mô tả | Ví dụ |
|-------|-------|-------|
| `mst` | Mã số thuế | "110198560" |
| `success` | Trạng thái xử lý | true/false |
| `processing_time` | Thời gian xử lý (giây) | 1.23 |
| `confidence_score` | Điểm tin cậy (0-1) | 0.95 |
| `data_quality` | Chất lượng dữ liệu | "HIGH", "MEDIUM", "LOW" |
| `source` | Nguồn dữ liệu | "real_api", "mixed", "generated" |
| `error` | Thông báo lỗi (nếu có) | null |

### Confidence Score

- **0.8 - 1.0**: Dữ liệu chất lượng cao từ API thực
- **0.5 - 0.8**: Dữ liệu hỗn hợp (API + generated)
- **0.0 - 0.5**: Dữ liệu giả lập

### Data Quality

- **HIGH**: Dữ liệu đầy đủ từ API thực
- **MEDIUM**: Dữ liệu từ API thực + generated
- **LOW**: Chủ yếu là dữ liệu generated

## ⚙️ Cấu hình nâng cao

### File cấu hình

Tạo `config/settings.json`:

```json
{
  "api": {
    "enterprise_url": "https://thongtindoanhnghiep.co/api/company",
    "vss_url": "http://vssapp.teca.vn:8088",
    "use_mock_vss": true,
    "timeout": 45,
    "max_retries": 5
  },
  "processing": {
    "max_workers": 4,
    "batch_size": 50,
    "rate_limit": {
      "max_requests_per_minute": 30,
      "window_seconds": 60
    }
  },
  "logging": {
    "level": "INFO",
    "file": "logs/vss_integration.log"
  }
}
```

### Environment Variables

```bash
export VSS_MAX_WORKERS=8
export VSS_LOG_LEVEL=DEBUG
export VSS_ENTERPRISE_API_URL="https://custom-api.com/company"
```

## 🔍 Troubleshooting

### Lỗi thường gặp

#### 1. Connection timeout
```
Lỗi: Connection timeout
Giải pháp:
- Kiểm tra kết nối internet
- Tăng timeout trong config
- Sử dụng --no-real-apis để test
```

#### 2. Invalid MST format
```
Lỗi: Invalid MST format
Giải pháp:
- MST phải có 10-13 chữ số
- Kiểm tra không có ký tự đặc biệt
```

#### 3. Rate limit exceeded
```
Lỗi: Rate limit exceeded
Giải pháp:
- Giảm số workers
- Tăng delay giữa requests
- Kiểm tra rate limit config
```

#### 4. Memory error
```
Lỗi: Memory error
Giải pháp:
- Giảm batch_size
- Giảm max_workers
- Tăng RAM hệ thống
```

### Debug mode

```bash
# Bật debug logging
export VSS_LOG_LEVEL=DEBUG
python main.py --mst 110198560

# Kiểm tra logs
tail -f logs/vss_integration.log
```

### Performance tuning

```bash
# Tăng workers cho máy mạnh
python main.py --file msts.txt --workers 8

# Giảm workers cho máy yếu
python main.py --file msts.txt --workers 2

# Monitor hiệu suất
python main.py --file msts.txt --output results.json
```

## 📈 Best Practices

### 1. Batch Processing

```python
# Tốt: Xử lý batch với multiple workers
processor = VSSIntegrationProcessor(max_workers=4)
results = processor.process_batch(large_mst_list)

# Không tốt: Xử lý từng MST một
for mst in large_mst_list:
    result = processor.process_single_mst(mst)
```

### 2. Error Handling

```python
# Tốt: Xử lý lỗi gracefully
results = processor.process_batch(msts)
successful = [r for r in results if r.success]
failed = [r for r in results if not r.success]

# Không tốt: Không kiểm tra lỗi
results = processor.process_batch(msts)
# Giả sử tất cả đều thành công
```

### 3. Resource Management

```python
# Tốt: Sử dụng context manager
with VSSIntegrationProcessor(max_workers=4) as processor:
    results = processor.process_batch(msts)

# Không tốt: Quên cleanup
processor = VSSIntegrationProcessor(max_workers=4)
results = processor.process_batch(msts)
# Không gọi cleanup
```

## 📞 Support

### Documentation

- **README.md**: Tổng quan và cài đặt
- **ARCHITECTURE.md**: Kiến trúc hệ thống
- **DEPLOYMENT_GUIDE.md**: Hướng dẫn triển khai
- **API Documentation**: http://localhost:5001/docs

### Issues và Support

- **GitHub Issues**: Báo cáo bugs và yêu cầu tính năng
- **Documentation**: Wiki và guides
- **Community**: Discussions và forums

### System Requirements

- **Python**: 3.8+
- **RAM**: 4GB+ cho batch processing
- **Disk**: 10GB+ cho logs và data
- **Network**: Stable internet connection

---

*User Guide v2.0.0 - VSS Integration System*