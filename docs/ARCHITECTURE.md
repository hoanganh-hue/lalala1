# 🏗️ VSS Integration System - Architecture

## Tổng quan kiến trúc

VSS Integration System được thiết kế theo mô hình **modular architecture** với các thành phần độc lập, dễ bảo trì và mở rộng.

## 🎯 Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface  │  Web Interface  │  REST API  │  Python API │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                     │
├─────────────────────────────────────────────────────────────┤
│  VSS Processor  │  Data Generator  │  Metrics  │  Validation │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Enterprise API  │  VSS API  │  Cache  │  File Storage     │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Logging  │  Config  │  Monitoring  │  Error Handling     │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Module Structure

### 1. Core Modules (`src/core/`)

#### `data_models.py`
- **Mục đích**: Định nghĩa các cấu trúc dữ liệu chuẩn
- **Thành phần chính**:
  - `ProcessingResult`: Kết quả xử lý MST
  - `EnterpriseData`: Thông tin doanh nghiệp
  - `EmployeeData`: Thông tin nhân viên
  - `ContributionData`: Dữ liệu đóng góp BHXH
  - `ProcessingMetrics`: Metrics hiệu suất

#### `data_generator.py`
- **Mục đích**: Tạo dữ liệu thực tế cho testing
- **Tính năng**:
  - Generate enterprise data
  - Generate employee data
  - Generate contribution data
  - Calculate compliance scores

### 2. API Layer (`src/api/`)

#### `base_client.py`
- **Mục đích**: Base class cho tất cả API clients
- **Tính năng**:
  - Rate limiting
  - Circuit breaker
  - Retry logic
  - Connection pooling

#### `enterprise_client.py`
- **Mục đích**: Client cho Enterprise API
- **Endpoint**: `thongtindoanhnghiep.co`

#### `vss_client.py`
- **Mục đích**: Client cho VSS API
- **Endpoint**: `vssapp.teca.vn:8088`

### 3. Processing Layer (`src/processors/`)

#### `vss_processor.py`
- **Mục đích**: Main processor cho VSS integration
- **Tính năng**:
  - Single MST processing
  - Batch processing
  - Parallel execution
  - Metrics tracking

### 4. Configuration (`src/config/`)

#### `settings.py`
- **Mục đích**: Centralized configuration management
- **Tính năng**:
  - Load from JSON files
  - Environment variable support
  - Default values fallback

#### `default_config.py`
- **Mục đích**: Default configuration values
- **Cấu trúc**: Nested dictionary với tất cả settings

### 5. Utilities (`src/utils/`)

#### `logger.py`
- **Mục đích**: Centralized logging system
- **Tính năng**:
  - Multiple log levels
  - File rotation
  - Module-specific loggers

## 🔄 Data Flow

### 1. Single MST Processing
```
MST Input → Validation → API Calls → Data Generation → Result Assembly → Output
```

### 2. Batch Processing
```
MST List → Task Distribution → Parallel Processing → Result Aggregation → Summary
```

### 3. Web Request Flow
```
HTTP Request → Flask Router → VSS Processor → JSON Response → Client
```

## 🛡️ Error Handling Strategy

### 1. Circuit Breaker Pattern
- **Mục đích**: Bảo vệ hệ thống khỏi cascade failures
- **Implementation**: `CircuitBreaker` class trong `base_client.py`

### 2. Retry Logic
- **Mục đích**: Xử lý lỗi tạm thời
- **Strategy**: Exponential backoff với jitter

### 3. Graceful Degradation
- **Mục đích**: Hệ thống vẫn hoạt động khi API external fail
- **Implementation**: Fallback to generated data

## 📊 Performance Optimizations

### 1. Connection Pooling
- **Implementation**: `requests.Session` với `HTTPAdapter`
- **Benefit**: Reuse connections, giảm overhead

### 2. Rate Limiting
- **Implementation**: Token bucket algorithm
- **Benefit**: Tránh bị API rate limit

### 3. Caching
- **Implementation**: In-memory cache với TTL
- **Benefit**: Giảm API calls, tăng tốc độ

### 4. Parallel Processing
- **Implementation**: `ThreadPoolExecutor`
- **Benefit**: Xử lý nhiều MST đồng thời

## 🔧 Configuration Management

### 1. Hierarchical Configuration
```
Environment Variables > Config File > Default Values
```

### 2. Configuration Sections
- **API**: URLs, timeouts, retries
- **Processing**: Workers, batch size, rate limits
- **Logging**: Levels, files, rotation
- **Security**: Proxies, headers, authentication

## 📈 Monitoring & Observability

### 1. Metrics Collection
- **Processing metrics**: Success rate, processing time
- **System metrics**: Memory usage, CPU usage
- **Business metrics**: Data quality, confidence scores

### 2. Logging Strategy
- **Structured logging**: JSON format cho easy parsing
- **Log levels**: DEBUG, INFO, WARNING, ERROR
- **Log rotation**: Size-based và time-based

### 3. Health Checks
- **API endpoints**: `/health` cho system status
- **Dependency checks**: Database, external APIs
- **Performance indicators**: Response times, error rates

## 🚀 Deployment Architecture

### 1. Single Instance
```
┌─────────────────┐
│   Web Server    │
│   (Flask)       │
├─────────────────┤
│   VSS Processor │
│   (Python)      │
├─────────────────┤
│   File Storage  │
│   (Local)       │
└─────────────────┘
```

### 2. Multi-Instance (Future)
```
┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server 1  │
│   (Nginx)       │────│   (Flask)       │
└─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Web Server 2  │
                       │   (Flask)       │
                       └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Shared Storage│
                       │   (Database)    │
                       └─────────────────┘
```

## 🔒 Security Considerations

### 1. API Security
- **Rate limiting**: Prevent abuse
- **Input validation**: Sanitize MST inputs
- **Error handling**: Don't expose sensitive info

### 2. Data Protection
- **No sensitive data logging**: Avoid logging MSTs in plain text
- **Secure file storage**: Proper permissions
- **Data retention**: Automatic cleanup

### 3. Network Security
- **HTTPS only**: For production
- **Proxy support**: For corporate environments
- **Timeout handling**: Prevent hanging connections

## 📋 Best Practices

### 1. Code Organization
- **Single responsibility**: Mỗi module có một mục đích rõ ràng
- **Dependency injection**: Dễ test và maintain
- **Interface segregation**: Small, focused interfaces

### 2. Error Handling
- **Fail fast**: Detect errors early
- **Graceful degradation**: System continues working
- **Comprehensive logging**: For debugging

### 3. Performance
- **Lazy loading**: Load data when needed
- **Caching**: Reduce redundant operations
- **Resource management**: Proper cleanup

### 4. Testing
- **Unit tests**: Test individual components
- **Integration tests**: Test component interactions
- **Performance tests**: Test under load

---

*Architecture document v2.0.0 - VSS Integration System*
