# 🚀 VSS Integration System V3.1 - Deployment Guide

**Hướng dẫn triển khai toàn diện cho môi trường Production**

---

## 📋 Mục Lục

1. [Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
2. [Cài Đặt Nhanh](#-cài-đặt-nhanh)
3. [Triển Khai Production](#-triển-khai-production)
4. [Cấu Hình Chi Tiết](#-cấu-hình-chi-tiết)
5. [Docker Deployment](#-docker-deployment)
6. [Monitoring & Logging](#-monitoring--logging)
7. [Troubleshooting](#-troubleshooting)
8. [Maintenance](#-maintenance)

---

## 🖥️ Yêu Cầu Hệ Thống

### 💻 Minimum Requirements

| Component | Requirement | Recommended |
|-----------|-------------|-------------|
| **OS** | Linux/Windows/macOS | Ubuntu 20.04+ |
| **Python** | 3.8+ | Python 3.11+ |
| **RAM** | 2GB | 8GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 1GB | 10GB+ |
| **Network** | Stable internet | High-speed connection |

### 📦 Dependencies

```bash
# Core dependencies
Python 3.8+
pip 21.0+
virtualenv (recommended)

# Optional (for advanced features)
Docker 20.0+ (for containerization)
Redis 6.0+ (for caching)
PostgreSQL 12+ (for data storage)
```

---

## ⚡ Cài Đặt Nhanh

### 🔥 One-Command Installation

```bash
# Download and setup
curl -sSL https://raw.githubusercontent.com/your-repo/vss-system/main/install.sh | bash

# Or manual installation
git clone <repository-url>
cd vss_complete_system
pip install -r requirements_v3.txt
```

### ✅ Verification

```bash
# Test installation
python main.py --version
# Expected: VSS Integration System V3.1 3.1.0

# Test with sample MST
python main.py --mst 5200958920
# Expected: Complete processing with VSS data extraction
```

---

## 🏭 Triển Khai Production

### 📋 Pre-deployment Checklist

```bash
# 1. System preparation
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y

# 2. Create deployment user
sudo useradd -m -s /bin/bash vss-system
sudo usermod -aG sudo vss-system

# 3. Setup directory structure
sudo mkdir -p /opt/vss-system
sudo chown vss-system:vss-system /opt/vss-system
```

### 🚀 Production Setup

```bash
# Switch to deployment user
sudo su - vss-system

# 1. Clone repository
cd /opt/vss-system
git clone <repository-url> .

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements_v3.txt

# 4. Setup configuration
cp config/settings.json.example config/settings.json
nano config/settings.json  # Edit configuration

# 5. Test installation
python main.py --version
python main.py --mst 5200958920  # Test with real MST
```

### 🔒 Security Configuration

```bash
# 1. Create service user (no shell)
sudo useradd -r -s /bin/false vss-service

# 2. Set proper permissions
sudo chown -R vss-service:vss-service /opt/vss-system
sudo chmod 750 /opt/vss-system
sudo chmod 640 /opt/vss-system/config/settings.json

# 3. Setup environment file
sudo nano /opt/vss-system/.env
```

**Environment File (.env):**
```bash
# API Configuration
VSS_API_KEY=your-secret-api-key
VSS_SECRET_KEY=your-secret-key

# Performance Settings
VSS_MAX_WORKERS=8
VSS_REQUEST_TIMEOUT=30
VSS_CACHE_TTL=3600

# Logging
VSS_LOG_LEVEL=INFO
VSS_LOG_FILE=/var/log/vss-system/app.log

# Database (optional)
VSS_DB_URL=postgresql://user:pass@localhost:5432/vss_db

# Redis (optional)
VSS_REDIS_URL=redis://localhost:6379/0
```

---

## ⚙️ Cấu Hình Chi Tiết

### 📄 Main Configuration (config/settings.json)

```json
{
  "api": {
    "enterprise_base_url": "https://api.doanhnghiep.gov.vn",
    "vss_base_url": "https://baohiemxahoi.gov.vn/api/v1",
    "timeout": 30,
    "max_retries": 3,
    "rate_limit": 10
  },
  "processing": {
    "max_workers": 8,
    "batch_size": 100,
    "enable_caching": true,
    "cache_ttl": 3600
  },
  "data_quality": {
    "min_completeness_score": 75.0,
    "min_accuracy_score": 85.0,
    "enable_validation": true
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/vss-system/app.log",
    "max_size": "100MB",
    "backup_count": 5
  }
}
```

### 🔧 Advanced Configuration

#### Performance Tuning
```json
{
  "performance": {
    "connection_pool_size": 20,
    "connection_pool_maxsize": 20,
    "dns_cache_ttl": 300,
    "tcp_keepalive": true,
    "enable_compression": true
  }
}
```

#### Error Handling
```json
{
  "error_handling": {
    "circuit_breaker_threshold": 5,
    "circuit_breaker_timeout": 60,
    "exponential_backoff_multiplier": 2,
    "max_retry_delay": 300
  }
}
```

---

## 🐳 Docker Deployment

### 📦 Docker Setup

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -s /bin/bash appuser

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements_v3.txt .
RUN pip install --no-cache-dir -r requirements_v3.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "main.py", "--help"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  vss-system:
    build: .
    container_name: vss-system
    restart: unless-stopped
    environment:
      - VSS_LOG_LEVEL=INFO
      - VSS_MAX_WORKERS=8
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./config:/app/config
    ports:
      - "8080:8080"
    networks:
      - vss-network
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    container_name: vss-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - vss-network

  postgres:
    image: postgres:15-alpine
    container_name: vss-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: vss_db
      POSTGRES_USER: vss_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - vss-network

volumes:
  redis_data:
  postgres_data:

networks:
  vss-network:
    driver: bridge
```

### 🚀 Docker Deployment Commands

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f vss-system

# Scale application
docker-compose up -d --scale vss-system=3

# Update application
docker-compose pull
docker-compose up -d --force-recreate

# Backup data
docker-compose exec postgres pg_dump -U vss_user vss_db > backup.sql
```

---

## 📊 Monitoring & Logging

### 📈 System Monitoring Setup

**1. Log Directory Setup:**
```bash
# Create log directories
sudo mkdir -p /var/log/vss-system
sudo chown vss-service:vss-service /var/log/vss-system
sudo chmod 755 /var/log/vss-system

# Setup log rotation
sudo nano /etc/logrotate.d/vss-system
```

**Log Rotation Config:**
```
/var/log/vss-system/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 vss-service vss-service
    postrotate
        systemctl reload vss-system || true
    endscript
}
```

**2. Systemd Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/vss-system.service
```

**Service Configuration:**
```ini
[Unit]
Description=VSS Integration System V3.1
After=network.target

[Service]
Type=simple
User=vss-service
Group=vss-service
WorkingDirectory=/opt/vss-system
Environment=PATH=/opt/vss-system/venv/bin
ExecStart=/opt/vss-system/venv/bin/python main.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=on-failure
RestartSec=5

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/opt/vss-system /var/log/vss-system

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start Service:**
```bash
# Enable service
sudo systemctl daemon-reload
sudo systemctl enable vss-system
sudo systemctl start vss-system

# Check status
sudo systemctl status vss-system

# View logs
sudo journalctl -u vss-system -f
```

### 📊 Performance Monitoring

**1. Basic Monitoring Script:**
```bash
#!/bin/bash
# /opt/vss-system/scripts/monitor.sh

# Check service status
if ! systemctl is-active --quiet vss-system; then
    echo "$(date): VSS System is not running" >> /var/log/vss-system/monitor.log
    systemctl restart vss-system
fi

# Check disk space
DISK_USAGE=$(df /opt/vss-system | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is ${DISK_USAGE}%" >> /var/log/vss-system/monitor.log
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo "$(date): Memory usage is ${MEM_USAGE}%" >> /var/log/vss-system/monitor.log
fi
```

**2. Crontab Setup:**
```bash
# Add monitoring script to crontab
sudo crontab -e

# Add this line:
*/5 * * * * /opt/vss-system/scripts/monitor.sh
```

---

## 🛠️ Troubleshooting

### ❌ Common Issues

#### 1. Import Module Errors
```bash
# Symptoms: ModuleNotFoundError
# Solution:
export PYTHONPATH=/opt/vss-system/src:$PYTHONPATH
# Or add to ~/.bashrc for permanent fix
```

#### 2. Permission Denied Errors
```bash
# Fix file permissions
sudo chown -R vss-service:vss-service /opt/vss-system
sudo chmod -R 755 /opt/vss-system
sudo chmod 600 /opt/vss-system/.env
```

#### 3. API Connection Issues
```bash
# Test network connectivity
curl -I https://baohiemxahoi.gov.vn

# Check DNS resolution
nslookup baohiemxahoi.gov.vn

# Test with specific MST
python main.py --mst 5200958920 --debug
```

#### 4. Memory Issues
```bash
# Check memory usage
free -h
top -p $(pgrep -f "python main.py")

# Optimize memory settings in config
{
  "processing": {
    "max_workers": 4,  # Reduce workers
    "batch_size": 50   # Smaller batches
  }
}
```

### 🔍 Debug Mode

```bash
# Enable debug logging
export VSS_LOG_LEVEL=DEBUG

# Run with verbose output
python main.py --mst 5200958920 --debug --verbose

# Check specific component
python -c "
from src.processors.complete_vss_integration_processor import CompleteVSSIntegrationProcessor
processor = CompleteVSSIntegrationProcessor()
print('Processor initialized successfully')
"
```

### 📋 Health Check Script

```bash
#!/bin/bash
# /opt/vss-system/scripts/health_check.sh

echo "=== VSS System Health Check ==="
echo "Date: $(date)"
echo

# Check service status
echo "1. Service Status:"
systemctl is-active vss-system || echo "❌ Service not running"
echo

# Check Python dependencies
echo "2. Dependencies:"
/opt/vss-system/venv/bin/python -c "
import sys
required = ['pydantic', 'aiohttp', 'asyncio']
for module in required:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
"
echo

# Check configuration
echo "3. Configuration:"
if [ -f "/opt/vss-system/config/settings.json" ]; then
    echo "✅ Config file exists"
else
    echo "❌ Config file missing"
fi

# Test basic functionality
echo "4. Basic Functionality:"
/opt/vss-system/venv/bin/python main.py --version || echo "❌ Version check failed"

echo
echo "=== Health Check Complete ==="
```

---

## 🔧 Maintenance

### 📅 Regular Maintenance Tasks

#### Daily Tasks
```bash
# Check system status
sudo systemctl status vss-system

# Monitor logs for errors
sudo tail -f /var/log/vss-system/app.log | grep ERROR

# Check disk usage
df -h /opt/vss-system
```

#### Weekly Tasks
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Backup configuration
cp /opt/vss-system/config/settings.json /opt/vss-system/backups/settings_$(date +%Y%m%d).json

# Clean old logs
find /var/log/vss-system -name "*.log.*" -mtime +30 -delete
```

#### Monthly Tasks
```bash
# Update Python dependencies
cd /opt/vss-system
source venv/bin/activate
pip list --outdated
pip install --upgrade <package-name>

# Performance analysis
python scripts/performance_report.py

# Security audit
pip audit
```

### 🔄 Update Procedure

```bash
# 1. Backup current version
sudo systemctl stop vss-system
cp -r /opt/vss-system /opt/vss-system.backup.$(date +%Y%m%d)

# 2. Update code
cd /opt/vss-system
git fetch origin
git checkout v3.1.1  # New version

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements_v3.txt

# 4. Test update
python main.py --version
python main.py --mst 5200958920  # Test functionality

# 5. Restart service
sudo systemctl start vss-system
sudo systemctl status vss-system
```

### 📊 Performance Optimization

#### 1. Database Optimization (if using)
```sql
-- Create indexes for better performance
CREATE INDEX idx_mst_code ON processing_results(mst_code);
CREATE INDEX idx_processing_date ON processing_results(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM processing_results WHERE mst_code = '5200958920';
```

#### 2. Cache Configuration
```json
{
  "cache": {
    "backend": "redis",
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "ttl": 3600,
    "max_connections": 10
  }
}
```

#### 3. Network Optimization
```json
{
  "network": {
    "connection_timeout": 10,
    "read_timeout": 30,
    "pool_connections": 20,
    "pool_maxsize": 20,
    "max_retries": 3
  }
}
```

---

## 📞 Support & Contact

### 🆘 Getting Help

1. **Check Documentation**: Review this guide thoroughly
2. **Check Logs**: Look at application and system logs
3. **Run Health Check**: Use provided health check script
4. **Test Connectivity**: Verify network and API access

### 📧 Support Channels

- **GitHub Issues**: For bugs and feature requests
- **Email Support**: support@vss-system.com
- **Documentation**: https://docs.vss-system.com

### 📋 Support Information Template

When requesting support, please provide:

```
System Information:
- OS: (e.g., Ubuntu 20.04)
- Python Version: (python --version)
- VSS System Version: (python main.py --version)
- Installation Method: (pip, docker, manual)

Problem Description:
- What were you trying to do?
- What happened instead?
- Error messages (full stack trace)

Environment:
- Configuration file content (sensitive data removed)
- Recent log entries
- System resource usage (CPU, memory, disk)
```

---

**🎊 VSS Integration System V3.1 - Production Deployment Complete!**

*Last updated: 2025-09-19 | Version: 3.1.0*
