"""
Base API client with common functionality
"""
import requests
import time
import threading
import random
from typing import Dict, Any, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout, RequestException
from ..config.settings import config
from ..utils.logger import setup_module_logger


class BaseAPIClient:
    """Base API client with common functionality"""
    
    def __init__(self, base_url: str, client_name: str = "base"):
        self.base_url = base_url.rstrip('/')
        self.client_name = client_name
        self.logger = setup_module_logger(f"api.{client_name}")
        
        # Get configuration
        api_config = config.get_api_config()
        self.timeout = api_config.get('timeout', 30)
        self.connection_timeout = api_config.get('connection_timeout', 10)
        self.max_retries = api_config.get('max_retries', 5)  # Increased retries
        self.retry_delay = api_config.get('retry_delay', 2.0)  # Increased delay
        self.backoff_factor = api_config.get('backoff_factor', 2.0)
        self.jitter = api_config.get('jitter', True)
        
        # Rate limiting - More aggressive for batch processing
        self.rate_limiter = RateLimiter(
            max_requests=config.get('processing.rate_limit.max_requests_per_minute', 30),  # Increased
            window=config.get('processing.rate_limit.window_seconds', 60)
        )
        
        # Circuit breaker - More tolerant
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('circuit_breaker.failure_threshold', 10),  # Increased threshold
            recovery_timeout=config.get('circuit_breaker.recovery_timeout', 30)  # Faster recovery
        )
        
        # Create session
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create configured session"""
        session = requests.Session()
        
        # Configure retry strategy with better error handling
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            raise_on_status=False,  # Don't raise on status codes
            respect_retry_after_header=True
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=50,  # Increased connection pool
            pool_maxsize=50,      # Increased max connections
            pool_block=False      # Non-blocking pool
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Setup headers
        security_config = config.get('security', {})
        session.headers.update({
            'User-Agent': security_config.get('user_agent', 'VSS-Integration-System/2.0.0'),
            **security_config.get('headers', {})
        })
        
        # Setup proxy if enabled
        if security_config.get('enable_proxy', False):
            proxy_config = security_config.get('proxy_config', {})
            if proxy_config.get('http') or proxy_config.get('https'):
                session.proxies.update(proxy_config)
        
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request with enhanced error handling and retry logic"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Rate limiting
        self.rate_limiter.acquire()
        
        # Enhanced request function with better error handling
        def make_request():
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=(self.connection_timeout, self.timeout),
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code in [429, 500, 502, 503, 504, 520, 521, 522, 523, 524]:
                    # Retryable status codes
                    raise RequestException(f"HTTP {response.status_code}: {response.text[:200]}")
                else:
                    self.logger.warning(f"API request failed: {response.status_code} - {url}")
                    return None
                    
            except (ConnectionError, Timeout) as e:
                # Connection errors should be retried
                raise e
            except RequestException as e:
                # Request exceptions should be retried
                raise e
            except Exception as e:
                # Other exceptions should be logged and re-raised
                self.logger.error(f"Unexpected error in request: {str(e)}")
                raise e
        
        # Enhanced retry logic with exponential backoff and jitter
        for attempt in range(self.max_retries + 1):
            try:
                result = self.circuit_breaker.call(make_request)
                return result
            except (ConnectionError, Timeout, RequestException) as e:
                if attempt < self.max_retries:
                    # Calculate backoff with jitter
                    backoff_time = self.retry_delay * (self.backoff_factor ** attempt)
                    if self.jitter:
                        jitter = random.uniform(0.1, 0.3) * backoff_time
                        backoff_time += jitter
                    
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}. "
                        f"Retrying in {backoff_time:.2f}s..."
                    )
                    time.sleep(backoff_time)
                else:
                    self.logger.error(f"API request failed after {self.max_retries + 1} attempts: {str(e)} - {url}")
                    return None
            except Exception as e:
                self.logger.error(f"API request error: {str(e)} - {url}")
                return None
        
        return None
    
    def get(self, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make GET request"""
        return self._make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make POST request"""
        return self._make_request('POST', endpoint, **kwargs)


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests: int = 15, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
        self.lock = threading.Lock()
    
    def acquire(self) -> bool:
        """Acquire permission to make request"""
        with self.lock:
            now = time.time()
            # Remove old requests
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = self.window - (now - oldest_request)
            if wait_time > 0:
                time.sleep(wait_time + 0.1)  # Small buffer
                return self.acquire()
            
            return False


class CircuitBreaker:
    """Enhanced circuit breaker pattern for API protection"""
    
    def __init__(self, failure_threshold: int = 10, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with enhanced circuit breaker protection"""
        with self.lock:
            current_time = time.time()
            
            if self.state == 'OPEN':
                if current_time - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    self.failure_count = 0
                    self.success_count = 0
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset failure count
                self.failure_count = 0
                self.success_count += 1
                self.last_success_time = current_time
                
                if self.state == 'HALF_OPEN':
                    # If we've had enough successes in half-open state, close the circuit
                    if self.success_count >= 3:
                        self.state = 'CLOSED'
                        self.success_count = 0
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = current_time
                
                # Only count certain errors as failures for circuit breaker
                if isinstance(e, (ConnectionError, Timeout, RequestException)):
                    if self.failure_count >= self.failure_threshold:
                        self.state = 'OPEN'
                        self.success_count = 0
                
                raise e
