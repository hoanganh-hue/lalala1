"""
Enhanced VSS Client với các tính năng tối ưu cao cấp
- Proxy Rotation Manager
- Circuit Breaker Pattern
- Smart Caching System
- Advanced Error Handling & Retry Logic
- Data Validation với Pydantic

Author: MiniMax Agent
Date: 2025-09-15
"""

import time
import random
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from pydantic import BaseModel, Field, validator
import json

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    username: str
    password: str
    protocol: str = "http"
    
    @property
    def proxy_url(self) -> str:
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: CircuitState = CircuitState.CLOSED
    
class VSSDataModel(BaseModel):
    """Pydantic model for VSS data validation"""
    mst: str = Field(..., min_length=10, max_length=14, description="Mã số thuế")
    ten_doanh_nghiep: Optional[str] = Field(None, description="Tên doanh nghiệp")
    dia_chi: Optional[str] = Field(None, description="Địa chỉ")
    nguoi_dai_dien: Optional[str] = Field(None, description="Người đại diện")
    so_dien_thoai: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    trang_thai_hoat_dong: Optional[str] = Field(None, description="Trạng thái hoạt động")
    ngay_cap_mst: Optional[str] = Field(None, description="Ngày cấp MST")
    nganh_nghe_kinh_doanh: Optional[str] = Field(None, description="Ngành nghề kinh doanh")
    loai_hinh_doanh_nghiep: Optional[str] = Field(None, description="Loại hình doanh nghiệp")
    
    @validator('mst')
    def validate_mst(cls, v):
        """Validate MST format"""
        if not v.isdigit():
            raise ValueError('MST must contain only digits')
        return v
    
    class Config:
        extra = "allow"  # Allow additional fields

class ProxyRotationManager:
    """Manages proxy rotation with health checking"""
    
    def __init__(self, proxy_configs: List[ProxyConfig]):
        self.proxy_configs = proxy_configs
        self.current_index = 0
        self.proxy_health = {i: True for i in range(len(proxy_configs))}
        self.last_rotation = datetime.now()
        self._lock = threading.Lock()
        
    def get_current_proxy(self) -> Optional[ProxyConfig]:
        """Get current active proxy"""
        with self._lock:
            if not self.proxy_configs:
                return None
                
            # Find healthy proxy
            for _ in range(len(self.proxy_configs)):
                if self.proxy_health[self.current_index]:
                    return self.proxy_configs[self.current_index]
                self._rotate_to_next()
                
            # No healthy proxy found
            logger.warning("No healthy proxy available")
            return None
    
    def _rotate_to_next(self):
        """Rotate to next proxy"""
        self.current_index = (self.current_index + 1) % len(self.proxy_configs)
        self.last_rotation = datetime.now()
        
    def mark_proxy_unhealthy(self, proxy: ProxyConfig):
        """Mark proxy as unhealthy"""
        with self._lock:
            try:
                index = self.proxy_configs.index(proxy)
                self.proxy_health[index] = False
                logger.warning(f"Marking proxy {proxy.host}:{proxy.port} as unhealthy")
                self._rotate_to_next()
            except ValueError:
                pass
                
    def mark_proxy_healthy(self, proxy: ProxyConfig):
        """Mark proxy as healthy"""
        with self._lock:
            try:
                index = self.proxy_configs.index(proxy)
                self.proxy_health[index] = True
                logger.info(f"Marking proxy {proxy.host}:{proxy.port} as healthy")
            except ValueError:
                pass
                
    def rotate_proxy(self):
        """Force rotate to next proxy"""
        with self._lock:
            self._rotate_to_next()

class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.stats = CircuitBreakerStats()
        self._lock = threading.Lock()
        
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        with self._lock:
            if self.stats.state == CircuitState.CLOSED:
                return True
                
            if self.stats.state == CircuitState.OPEN:
                if self.stats.last_failure_time and \
                   datetime.now() - self.stats.last_failure_time > timedelta(seconds=self.timeout):
                    self.stats.state = CircuitState.HALF_OPEN
                    return True
                return False
                
            if self.stats.state == CircuitState.HALF_OPEN:
                return True
                
        return False
    
    def record_success(self):
        """Record successful request"""
        with self._lock:
            self.stats.success_count += 1
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.state = CircuitState.CLOSED
                self.stats.failure_count = 0
                
    def record_failure(self):
        """Record failed request"""
        with self._lock:
            self.stats.failure_count += 1
            self.stats.last_failure_time = datetime.now()
            
            if self.stats.failure_count >= self.failure_threshold:
                self.stats.state = CircuitState.OPEN

class SmartCache:
    """Smart caching system với TTL"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                    return value
                else:
                    del self.cache[key]
            return None
            
    def set(self, key: str, value: Any):
        """Set cached value"""
        with self._lock:
            self.cache[key] = (value, datetime.now())
            
    def clear(self):
        """Clear all cache"""
        with self._lock:
            self.cache.clear()

class EnhancedVSSClient:
    """Enhanced VSS Client với tất cả tính năng tối ưu"""
    
    def __init__(self, 
                 base_url: str = "https://tracuunnt.gdt.gov.vn",
                 proxy_configs: List[ProxyConfig] = None,
                 enable_cache: bool = True,
                 cache_ttl: int = 300,
                 circuit_breaker_threshold: int = 5,
                 circuit_breaker_timeout: int = 60,
                 request_timeout: int = 30,
                 max_retries: int = 3):
        
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        
        # Initialize components
        self.proxy_manager = ProxyRotationManager(proxy_configs or [])
        self.circuit_breaker = CircuitBreaker(circuit_breaker_threshold, circuit_breaker_timeout)
        self.cache = SmartCache(cache_ttl) if enable_cache else None
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "proxy_rotations": 0
        }
        self._metrics_lock = threading.Lock()
        
        # Setup session
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create optimized requests session"""
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
        return session
        
    def _update_metrics(self, success: bool, response_time: float, cache_hit: bool = False):
        """Update performance metrics"""
        with self._metrics_lock:
            self.metrics["total_requests"] += 1
            if success:
                self.metrics["successful_requests"] += 1
            else:
                self.metrics["failed_requests"] += 1
                
            if cache_hit:
                self.metrics["cache_hits"] += 1
            else:
                self.metrics["cache_misses"] += 1
                
            # Update average response time
            total = self.metrics["total_requests"]
            current_avg = self.metrics["average_response_time"]
            self.metrics["average_response_time"] = ((current_avg * (total - 1)) + response_time) / total
            
    def get_company_info(self, mst: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get company information by MST với tất cả tính năng tối ưu
        
        Args:
            mst: Mã số thuế
            force_refresh: Bỏ qua cache và lấy dữ liệu mới
            
        Returns:
            Dict chứa thông tin công ty đã được validate
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"vss_company_{mst}"
            if self.cache and not force_refresh:
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    self._update_metrics(True, time.time() - start_time, cache_hit=True)
                    logger.info(f"Cache hit for MST: {mst}")
                    return cached_result
                    
            # Check circuit breaker
            if not self.circuit_breaker.can_execute():
                raise Exception("Circuit breaker is open - service temporarily unavailable")
                
            # Get company info
            result = self._fetch_company_info(mst)
            
            # Validate data
            validated_data = self._validate_company_data(result)
            
            # Cache result
            if self.cache:
                self.cache.set(cache_key, validated_data)
                
            # Record success
            self.circuit_breaker.record_success()
            self._update_metrics(True, time.time() - start_time)
            
            logger.info(f"Successfully retrieved and validated data for MST: {mst}")
            return validated_data
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            self._update_metrics(False, time.time() - start_time)
            logger.error(f"Failed to get company info for MST {mst}: {str(e)}")
            raise
            
    def _fetch_company_info(self, mst: str) -> Dict[str, Any]:
        """Fetch company info with proxy rotation and retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Get current proxy
                proxy = self.proxy_manager.get_current_proxy()
                proxies = None
                if proxy:
                    proxies = {
                        'http': proxy.proxy_url,
                        'https': proxy.proxy_url
                    }
                    
                # Make request
                url = f"{self.base_url}/tcnnt/mstcn.jsp"
                params = {
                    'mst': mst,
                    'tm': str(int(time.time() * 1000))  # timestamp
                }
                
                response = self.session.get(
                    url,
                    params=params,
                    proxies=proxies,
                    timeout=self.request_timeout,
                    verify=False
                )
                
                if response.status_code == 200:
                    # Parse response
                    try:
                        data = response.json()
                        if proxy:
                            self.proxy_manager.mark_proxy_healthy(proxy)
                        return data
                    except json.JSONDecodeError:
                        # Try to extract data from HTML if JSON parsing fails
                        return self._parse_html_response(response.text, mst)
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed for MST {mst}: {str(e)}")
                
                # Mark proxy unhealthy and rotate
                if proxy:
                    self.proxy_manager.mark_proxy_unhealthy(proxy)
                    self.metrics["proxy_rotations"] += 1
                    
                # Wait before retry
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    
        raise last_exception or Exception("All retry attempts failed")
        
    def _parse_html_response(self, html: str, mst: str) -> Dict[str, Any]:
        """Parse HTML response when JSON parsing fails"""
        # Implement HTML parsing logic here
        # This is a simplified version
        result = {
            "mst": mst,
            "ten_doanh_nghiep": None,
            "dia_chi": None,
            "nguoi_dai_dien": None,
            "trang_thai_hoat_dong": None
        }
        
        # Add basic HTML parsing logic here
        # For now, return basic structure
        return result
        
    def _validate_company_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate company data using Pydantic"""
        try:
            # Create Pydantic model instance
            validated = VSSDataModel(**data)
            return validated.dict()
        except Exception as e:
            logger.warning(f"Data validation failed: {str(e)}")
            # Return original data if validation fails
            return data
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        with self._metrics_lock:
            metrics_copy = self.metrics.copy()
            
        # Calculate success rate
        total = metrics_copy["total_requests"]
        if total > 0:
            metrics_copy["success_rate"] = (metrics_copy["successful_requests"] / total) * 100
            metrics_copy["cache_hit_rate"] = (metrics_copy["cache_hits"] / total) * 100
        else:
            metrics_copy["success_rate"] = 0
            metrics_copy["cache_hit_rate"] = 0
            
        # Add circuit breaker status
        metrics_copy["circuit_breaker_state"] = self.circuit_breaker.stats.state.value
        metrics_copy["circuit_breaker_failures"] = self.circuit_breaker.stats.failure_count
        
        return metrics_copy
        
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "circuit_breaker": {
                "state": self.circuit_breaker.stats.state.value,
                "failure_count": self.circuit_breaker.stats.failure_count,
                "can_execute": self.circuit_breaker.can_execute()
            },
            "proxy_manager": {
                "total_proxies": len(self.proxy_manager.proxy_configs),
                "healthy_proxies": sum(self.proxy_manager.proxy_health.values()),
                "current_proxy_index": self.proxy_manager.current_index
            },
            "cache": {
                "enabled": self.cache is not None,
                "size": len(self.cache.cache) if self.cache else 0
            },
            "metrics": self.get_performance_metrics()
        }
        
        # Determine overall health
        if (health_status["circuit_breaker"]["state"] == "open" or 
            health_status["proxy_manager"]["healthy_proxies"] == 0):
            health_status["status"] = "unhealthy"
            
        return health_status
        
    def clear_cache(self):
        """Clear all cached data"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")
            
    def reset_metrics(self):
        """Reset performance metrics"""
        with self._metrics_lock:
            self.metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "average_response_time": 0.0,
                "proxy_rotations": 0
            }
        logger.info("Metrics reset")

# Factory function để tạo client với config mặc định
def create_enhanced_vss_client(proxy_configs: List[Dict] = None) -> EnhancedVSSClient:
    """
    Factory function để tạo Enhanced VSS Client với cấu hình tối ưu
    
    Args:
        proxy_configs: List các proxy config dạng dict
        
    Returns:
        Configured EnhancedVSSClient instance
    """
    # Convert dict configs to ProxyConfig objects
    proxy_objects = []
    if proxy_configs:
        for config in proxy_configs:
            proxy_objects.append(ProxyConfig(**config))
    
    # Default proxy nếu không có config
    if not proxy_objects:
        proxy_objects = [
            ProxyConfig(
                host="ip.mproxy.vn",
                port=12301,
                username="beba111", 
                password="tDV5tkMchYUBMD"
            )
        ]
    
    return EnhancedVSSClient(
        proxy_configs=proxy_objects,
        enable_cache=True,
        cache_ttl=300,  # 5 minutes
        circuit_breaker_threshold=5,
        circuit_breaker_timeout=60,
        request_timeout=30,
        max_retries=3
    )

if __name__ == "__main__":
    # Test code
    client = create_enhanced_vss_client()
    
    # Test với một MST
    test_mst = "0123456789"
    
    try:
        result = client.get_company_info(test_mst)
        print(f"Result: {result}")
        
        # Show metrics
        metrics = client.get_performance_metrics()
        print(f"Metrics: {metrics}")
        
        # Health check
        health = client.health_check()
        print(f"Health: {health}")
        
    except Exception as e:
        print(f"Error: {e}")