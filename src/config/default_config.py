"""
Default configuration values for VSS Integration System
Enhanced with advanced optimization features

Author: MiniMax Agent  
Date: 2025-09-15
"""

class Config:
    """Configuration management class"""
    
    @staticmethod
    def get_default_config():
        return DEFAULT_CONFIG
    
    @staticmethod
    def get_proxy_configs():
        """Get proxy configurations for Enhanced VSS Client"""
        return [
            {
                "host": "ip.mproxy.vn",
                "port": 12301,
                "username": "beba111",
                "password": "tDV5tkMchYUBMD",
                "protocol": "http"
            }
        ]

DEFAULT_CONFIG = {
    "api": {
        # PRIMARY DATA SOURCE - Working Enterprise API
        "enterprise_url": "https://thongtindoanhnghiep.co/api/company",
        "enterprise_priority": 1,  # Highest priority
        "enterprise_enabled": True,
        
        # SECONDARY DATA SOURCE - VSS API via Proxy
        "vss_url": "http://vssapp.teca.vn:8088",
        "vss_priority": 2,  # Lower priority
        "vss_enabled": True,
        "use_mock_vss": False,
        
        # API ROUTING STRATEGY
        "api_strategy": "fallback",  # Options: "enterprise_only", "vss_only", "fallback", "parallel"
        "fallback_timeout": 10,  # Seconds to wait before trying fallback
        "health_check_interval": 300,  # Health check every 5 minutes
        
        # CONNECTION SETTINGS
        "timeout": 45,
        "connection_timeout": 15,
        "max_retries": 5,
        "retry_delay": 2.0,
        "backoff_factor": 2.0,
        "jitter": True,
        
        # API SPECIFIC SETTINGS
        "enterprise_timeout": 30,  # Faster timeout for working API
        "vss_timeout": 60,  # Longer timeout for potentially problematic API
    },
    "processing": {
        "max_workers": 2,
        "batch_size": 25,
        "rate_limit": {
            "max_requests_per_minute": 30,
            "window_seconds": 60
        }
    },
    "cache": {
        "enabled": True,
        "ttl": 300,  # 5 minutes
        "max_size": 1000
    },
    "circuit_breaker": {
        "failure_threshold": 10,
        "recovery_timeout": 30,
        "half_open_max_calls": 3
    },
    "logging": {
        "level": "INFO",
        "file": "logs/vss_integration.log",
        "max_size": "10MB",
        "backup_count": 5,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "data": {
        "input_dir": "data/input",
        "output_dir": "data/output",
        "reports_dir": "reports",
        "backup_dir": "data/backup"
    },
    "monitoring": {
        "enabled": True,
        "metrics_interval": 30,  # seconds
        "health_check_interval": 60,  # seconds
        "alert_thresholds": {
            "error_rate": 0.1,  # 10%
            "response_time": 5.0,  # seconds
            "memory_usage": 0.8  # 80%
        }
    },
    "security": {
        "enable_proxy": True,  # Enable proxy for VSS API by default
        "proxy_config": {
            "http": "http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301",
            "https": "http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301"
        },
        "proxy_rotation": {
            "enabled": True,
            "rotation_interval": 3600,  # Rotate proxy every hour
            "backup_proxies": []  # Add backup proxy configs here
        },
        "vss_specific_proxy": {
            "enabled": True,
            "only_for_vss": True,  # Only use proxy for VSS API calls
            "reset_endpoint": "https://mproxy.vn/capi/41ew9h9jIC3rLK3BAuihhU22JF8STiL_sGwzdC5b4no/key/tDV5tkMchYUBMD/resetIp",
            "pac_file": "http://ip.mproxy.vn/12301.pac"
        },
        "user_agent": "VSS-Integration-System/2.0.0",
        "headers": {
            "Accept": "application/json,text/html,application/xhtml+xml,*/*;q=0.9",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        }
    },
    
    # ===== ENHANCED OPTIMIZATION CONFIGURATIONS =====
    
    # Enhanced VSS Client Configuration
    "enhanced_vss": {
        "enabled": True,
        "proxy_configs": [
            {
                "host": "ip.mproxy.vn",
                "port": 12301,
                "username": "beba111",
                "password": "tDV5tkMchYUBMD",
                "protocol": "http"
            }
        ],
        "cache": {
            "enabled": True,
            "ttl_seconds": 300  # 5 minutes
        },
        "circuit_breaker": {
            "failure_threshold": 5,
            "timeout_seconds": 60
        },
        "request_settings": {
            "timeout": 30,
            "max_retries": 3
        }
    },
    
    # Optimized Processor Configuration
    "optimized_processor": {
        "api_strategy": "ENTERPRISE_FIRST",  # ENTERPRISE_FIRST, VSS_ONLY, PARALLEL, AUTO
        "max_concurrent_requests": 10,
        "enable_caching": True,
        "enable_monitoring": True,
        "monitoring_interval": 60,  # seconds
        "performance_optimization": {
            "auto_adjust_strategy": True,
            "auto_adjust_concurrency": True,
            "success_rate_threshold": 80,  # Minimum acceptable success rate %
            "response_time_threshold": 5.0  # Maximum acceptable response time (seconds)
        }
    },
    
    # Enterprise API Configuration
    "enterprise_api": {
        "url": "https://thongtindoanhnghiep.co/api/company",
        "api_key": "",  # Add your API key here
        "timeout": 30,
        "enabled": True,
        "health_check_url": "https://thongtindoanhnghiep.co/api/health",
        "rate_limit": {
            "requests_per_minute": 60,
            "burst_limit": 10
        }
    },
    
    # Data Validation Configuration
    "data_validation": {
        "enabled": True,
        "strict_validation": False,  # Set to True for strict Pydantic validation
        "required_fields": [
            "mst",
            "ten_doanh_nghiep"
        ],
        "field_mapping": {
            "company_name": "ten_doanh_nghiep",
            "address": "dia_chi",
            "representative": "nguoi_dai_dien",
            "phone": "so_dien_thoai",
            "email": "email",
            "status": "trang_thai_hoat_dong",
            "issue_date": "ngay_cap_mst",
            "business_type": "nganh_nghe_kinh_doanh",
            "organization_type": "loai_hinh_doanh_nghiep"
        }
    },
    
    # Performance Benchmarking Configuration
    "benchmarking": {
        "enabled": True,
        "test_mst_codes": [
            "0123456789",
            "0123456788", 
            "0123456787",
            "0123456786",
            "0123456785"
        ],
        "benchmark_duration": 300,  # 5 minutes
        "concurrent_users": [1, 2, 5, 10],
        "metrics_collection": {
            "response_time": True,
            "throughput": True,
            "success_rate": True,
            "error_distribution": True,
            "resource_usage": True
        }
    },
    
    # Advanced Monitoring & Alerting
    "advanced_monitoring": {
        "enabled": True,
        "metrics_export": {
            "enabled": True,
            "format": "json",  # json, csv, prometheus
            "export_interval": 300,  # 5 minutes
            "retention_days": 30
        },
        "alerting": {
            "enabled": False,  # Set to True to enable alerting
            "channels": {
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                }
            },
            "thresholds": {
                "success_rate_critical": 70,  # %
                "success_rate_warning": 85,   # %
                "response_time_critical": 10.0,  # seconds
                "response_time_warning": 5.0,    # seconds
                "queue_size_critical": 100,
                "queue_size_warning": 50
            }
        }
    },
    
    # System Optimization Settings
    "system_optimization": {
        "memory_management": {
            "cache_cleanup_interval": 1800,  # 30 minutes
            "max_memory_usage": 512,  # MB
            "garbage_collection_threshold": 400  # MB
        },
        "connection_pooling": {
            "max_pool_size": 20,
            "pool_timeout": 30,
            "pool_recycle": 3600  # 1 hour
        },
        "async_processing": {
            "enabled": True,
            "max_async_workers": 5,
            "async_timeout": 60
        }
    }
}
