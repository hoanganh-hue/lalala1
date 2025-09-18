# 📊 Excel Workflow - VSS Integration System

Hướng dẫn sử dụng tính năng xử lý Excel trong hệ thống VSS Integration.

## 🎯 Tổng Quan

Hệ thống hỗ trợ xử lý file Excel chứa mã số thuế (MST) và xuất kết quả ra các file Excel được tổng hợp và chuẩn hóa.

### ✨ Tính Năng Chính

- ✅ **Đọc file Excel** chứa danh sách MST
- ✅ **Xử lý tự động** qua hệ thống VSS Integration
- ✅ **Xuất báo cáo Excel** với nhiều sheet
- ✅ **Validation** file đầu vào
- ✅ **Template** mẫu cho người dùng
- ✅ **CLI** dễ sử dụng

## 📁 Cấu Trúc Thư Mục

```
vss_integration_system/
├── data/
│   ├── input/              # File Excel đầu vào
│   │   └── sample_mst_input.xlsx
│   ├── output/             # File Excel kết quả
│   │   ├── vss_summary_report_YYYYMMDD_HHMMSS.xlsx
│   │   └── vss_detailed_report_YYYYMMDD_HHMMSS.xlsx
│   └── templates/          # Template mẫu
│       └── mst_input_template.xlsx
├── src/
│   └── utils/
│       └── excel_processor.py
└── excel_processor_cli.py
```

## 🚀 Cách Sử Dụng

### 1. Command Line Interface (CLI)

#### Tạo template mẫu
```bash
python excel_processor_cli.py template
```

#### Validate file Excel
```bash
python excel_processor_cli.py validate data/input/your_file.xlsx
```

#### Xử lý file Excel
```bash
python excel_processor_cli.py process data/input/your_file.xlsx --output-dir data/output --workers 4
```

#### Chạy demo
```bash
python excel_processor_cli.py demo
```

### 2. Python API

```python
from src.processors.excel_integration_processor import ExcelIntegrationProcessor

# Khởi tạo processor
processor = ExcelIntegrationProcessor(max_workers=4, use_real_apis=True)

# Xử lý file Excel
summary = processor.process_excel_file(
    input_file="data/input/your_file.xlsx",
    output_dir="data/output"
)

# Tạo template
processor.create_input_template("data/templates/my_template.xlsx")

# Validate file
validation = processor.validate_input_file("data/input/your_file.xlsx")
```

## 📋 Format File Excel Đầu Vào

### Cấu trúc cột được hỗ trợ:

| Tên cột | Mô tả | Ví dụ |
|---------|-------|-------|
| `Dãy số 10 chữ số` | Mã số thuế (10 chữ số) | `110198560` |
| `MST` | Mã số thuế | `110198560` |
| `Mã số thuế` | Mã số thuế | `110198560` |
| `Tax Code` | Mã số thuế (tiếng Anh) | `110198560` |
| `Tax ID` | Mã số thuế | `110198560` |

### Ví dụ file Excel:

| Dãy số 10 chữ số | Ghi chú |
|------------------|---------|
| 110198560 | Công ty A |
| 110197454 | Công ty B |
| 110198088 | Công ty C |

## 📊 File Excel Kết Quả

### 1. Summary Report (`vss_summary_report_*.xlsx`)

**Sheet: Summary**
- Tổng quan kết quả xử lý
- Thống kê thành công/thất bại
- Chất lượng dữ liệu
- Nguồn dữ liệu

**Sheet: Detailed Results**
- Chi tiết từng MST
- Confidence score
- Processing time
- Error messages

**Sheet: Statistics**
- Phân bố chất lượng dữ liệu
- Phân bố nguồn dữ liệu
- Thống kê thời gian xử lý

### 2. Detailed Report (`vss_detailed_report_*.xlsx`)

**Sheet: Enterprise Data**
- Thông tin doanh nghiệp
- Địa chỉ, liên hệ
- Loại hình kinh doanh
- Compliance score

**Sheet: Employee Data**
- Thông tin nhân viên
- Lương, chức vụ
- Số bảo hiểm
- Ngày bắt đầu

**Sheet: Contribution Data**
- Dữ liệu đóng bảo hiểm
- Số tiền đóng
- Ngày đóng
- Trạng thái

## ⚙️ Cấu Hình

### Tham số xử lý:

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `max_workers` | Số worker threads | 4 |
| `use_real_apis` | Sử dụng API thực | True |
| `output_dir` | Thư mục xuất kết quả | `data/output` |

### Cấu hình trong `settings.json`:

```json
{
  "processing": {
    "max_workers": 4,
    "batch_size": 50
  },
  "data": {
    "input_dir": "data/input",
    "output_dir": "data/output"
  }
}
```

## 🔍 Validation

Hệ thống tự động validate file Excel:

- ✅ **Kiểm tra tồn tại** file
- ✅ **Tìm cột MST** phù hợp
- ✅ **Validate format** MST (10 chữ số)
- ✅ **Đếm số lượng** MST hợp lệ
- ✅ **Báo lỗi chi tiết** nếu có vấn đề

## 📈 Performance

### Thống kê xử lý:

- **Tốc độ**: ~0.03 MST/giây (với real APIs)
- **Success rate**: 100% (trong test)
- **Confidence**: >0.9 (chất lượng cao)
- **Memory usage**: Tối ưu với batch processing

### Tối ưu hóa:

- **Parallel processing** với multiple workers
- **Connection pooling** cho API calls
- **Retry mechanism** với exponential backoff
- **Circuit breaker** để tránh cascade failures

## 🛠️ Troubleshooting

### Lỗi thường gặp:

1. **"No MST column found"**
   - Kiểm tra tên cột trong file Excel
   - Sử dụng template mẫu

2. **"No valid MSTs found"**
   - Kiểm tra format MST (phải là 10 chữ số)
   - Loại bỏ dòng trống

3. **"Excel file not found"**
   - Kiểm tra đường dẫn file
   - Đảm bảo file tồn tại

4. **"Permission denied"**
   - Kiểm tra quyền ghi thư mục output
   - Đóng file Excel đang mở

### Debug mode:

```bash
# Chạy với logging chi tiết
export VSS_LOG_LEVEL=DEBUG
python excel_processor_cli.py process your_file.xlsx
```

## 📚 Ví Dụ Sử Dụng

### Ví dụ 1: Xử lý file đơn giản

```bash
# 1. Tạo template
python excel_processor_cli.py template

# 2. Điền MST vào template
# 3. Xử lý file
python excel_processor_cli.py process data/templates/mst_input_template.xlsx

# 4. Kiểm tra kết quả trong data/output/
```

### Ví dụ 2: Xử lý file lớn

```bash
# Xử lý với nhiều workers
python excel_processor_cli.py process large_file.xlsx --workers 8 --output-dir results/
```

### Ví dụ 3: Sử dụng generated data

```bash
# Không sử dụng real APIs (nhanh hơn)
python excel_processor_cli.py process your_file.xlsx --no-real-apis
```

## 🎯 Best Practices

1. **Sử dụng template** để đảm bảo format đúng
2. **Validate file** trước khi xử lý
3. **Chọn số workers** phù hợp với hệ thống
4. **Backup dữ liệu** trước khi xử lý
5. **Monitor logs** để phát hiện lỗi sớm

## 📞 Hỗ Trợ

- **Logs**: Kiểm tra `logs/vss_integration.log`
- **Debug**: Sử dụng `--debug` flag
- **Issues**: Báo cáo lỗi với file log đầy đủ

---

**VSS Integration System v2.0.0** - Excel Workflow Module
