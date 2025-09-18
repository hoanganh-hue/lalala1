"""
Optimized VSS Processor với Intelligent API Routing
- Smart API Selection (Enterprise API First, VSS API Fallback)
- Parallel Data Processing
- Real-time Performance Monitoring
- Advanced Error Handling và Recovery
- Data Quality Assurance

Author: MiniMax Agent
Date: 2025-09-15
"""

import asyncio
import concurrent.futures
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import json
from pathlib import Path

# Import local modules
from ..api.enhanced_vss_client import EnhancedVSSClient, create_enhanced_vss_client
from ..api.enterprise_client import EnterpriseClient
from ..core.data_validator import DataValidator
from ..config.default_config import Config

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIStrategy(Enum):
    """API Strategy options"""
    ENTERPRISE_FIRST = "enterprise_first"
    VSS_ONLY = "vss_only"
    PARALLEL = "parallel"
    AUTO = "auto"

class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class ProcessingRequest:
    """Processing request data structure"""
    mst: str
    priority: int = 1
    max_retries: int = 3
    current_attempt: int = 0
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if request has expired (older than 1 hour)"""
        return datetime.now() - self.created_at > timedelta(hours=1)
        
    @property
    def should_retry(self) -> bool:
        """Check if request should be retried"""
        return (self.status == ProcessingStatus.FAILED and 
                self.current_attempt < self.max_retries and
                not self.is_expired)

@dataclass
class ProcessingMetrics:
    """Comprehensive processing metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    enterprise_api_success: int = 0
    vss_api_success: int = 0
    enterprise_api_failures: int = 0
    vss_api_failures: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    peak_concurrent_requests: int = 0
    current_concurrent_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def update(self, success: bool, processing_time: float, api_used: str = "unknown", cache_hit: bool = False):
        """Update metrics"""
        self.total_requests += 1
        self.total_processing_time += processing_time
        self.average_processing_time = self.total_processing_time / self.total_requests
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            
        if success:
            self.successful_requests += 1
            if api_used == "enterprise":
                self.enterprise_api_success += 1
            elif api_used == "vss":
                self.vss_api_success += 1
        else:
            self.failed_requests += 1
            if api_used == "enterprise":
                self.enterprise_api_failures += 1
            elif api_used == "vss":
                self.vss_api_failures += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def enterprise_success_rate(self) -> float:
        """Enterprise API success rate"""
        total_enterprise = self.enterprise_api_success + self.enterprise_api_failures
        if total_enterprise == 0:
            return 0.0
        return (self.enterprise_api_success / total_enterprise) * 100
    
    @property
    def vss_success_rate(self) -> float:
        """VSS API success rate"""
        total_vss = self.vss_api_success + self.vss_api_failures
        if total_vss == 0:
            return 0.0
        return (self.vss_api_success / total_vss) * 100

class OptimizedVSSProcessor:
    """
    Optimized VSS Processor với tất cả tính năng advanced
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 api_strategy: APIStrategy = APIStrategy.ENTERPRISE_FIRST,
                 max_concurrent_requests: int = 10,
                 enable_caching: bool = True,
                 enable_monitoring: bool = True):
        
        # Configuration
        self.config = config or Config.get_default_config()
        self.api_strategy = api_strategy
        self.max_concurrent_requests = max_concurrent_requests
        self.enable_caching = enable_caching
        self.enable_monitoring = enable_monitoring
        
        # Initialize API clients
        self.enterprise_client = self._create_enterprise_client()
        self.vss_client = self._create_vss_client()
        
        # Data validator
        self.data_validator = DataValidator()
        
        # Processing components
        self.processing_queue: Dict[str, ProcessingRequest] = {}
        self.metrics = ProcessingMetrics()
        self._queue_lock = threading.Lock()
        self._metrics_lock = threading.Lock()
        
        # Thread pool for concurrent processing
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent_requests,
            thread_name_prefix="VSS_Processor"
        )
        
        # Performance monitoring
        self.performance_history: List[Dict[str, Any]] = []
        self.monitoring_interval = 60  # seconds
        self._monitoring_thread = None
        
        if self.enable_monitoring:
            self._start_monitoring()
            
        logger.info(f"OptimizedVSSProcessor initialized with strategy: {api_strategy.value}")
    
    def _create_enterprise_client(self) -> EnterpriseClient:
        """Create Enterprise API client"""
        try:
            return EnterpriseClient(
                base_url=self.config.get("ENTERPRISE_API_URL", ""),
                api_key=self.config.get("ENTERPRISE_API_KEY", ""),
                timeout=self.config.get("REQUEST_TIMEOUT", 30)
            )
        except Exception as e:
            logger.warning(f"Failed to create Enterprise client: {e}")
            return None
    
    def _create_vss_client(self) -> EnhancedVSSClient:
        """Create Enhanced VSS client"""
        proxy_configs = self.config.get("PROXY_CONFIGS", [])
        return create_enhanced_vss_client(proxy_configs)
    
    def _start_monitoring(self):
        """Start performance monitoring thread"""
        def monitor():
            while self.enable_monitoring:
                try:
                    self._collect_performance_data()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(5)  # Short delay before retry
        
        self._monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self._monitoring_thread.start()
        logger.info("Performance monitoring started")
    
    def _collect_performance_data(self):
        """Collect current performance data"""
        with self._metrics_lock:
            metrics_snapshot = {
                "timestamp": datetime.now().isoformat(),
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.success_rate,
                "average_processing_time": self.metrics.average_processing_time,
                "concurrent_requests": self.metrics.current_concurrent_requests,
                "enterprise_success_rate": self.metrics.enterprise_success_rate,
                "vss_success_rate": self.metrics.vss_success_rate,
                "queue_size": len(self.processing_queue)
            }
            
        # Keep only last 24 hours of data
        current_time = datetime.now()
        self.performance_history = [
            data for data in self.performance_history
            if datetime.fromisoformat(data["timestamp"]) > current_time - timedelta(hours=24)
        ]
        
        self.performance_history.append(metrics_snapshot)
    
    def get_company_info(self, mst: str, priority: int = 1, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get company information with intelligent routing
        
        Args:
            mst: Mã số thuế
            priority: Priority level (1-10, higher = more priority)
            force_refresh: Force refresh data (bypass cache)
            
        Returns:
            Company information dict
        """
        start_time = time.time()
        
        try:
            # Create processing request
            request = ProcessingRequest(
                mst=mst,
                priority=priority,
                status=ProcessingStatus.PROCESSING,
                started_at=datetime.now()
            )
            
            with self._queue_lock:
                self.processing_queue[mst] = request
            
            # Update concurrent requests counter
            with self._metrics_lock:
                self.metrics.current_concurrent_requests += 1
                if self.metrics.current_concurrent_requests > self.metrics.peak_concurrent_requests:
                    self.metrics.peak_concurrent_requests = self.metrics.current_concurrent_requests
            
            try:
                # Execute intelligent routing
                result = self._execute_intelligent_routing(mst, force_refresh)
                
                # Validate result
                validated_result = self.data_validator.validate_company_data(result)
                
                # Update request status
                processing_time = time.time() - start_time
                request.status = ProcessingStatus.SUCCESS
                request.completed_at = datetime.now()
                request.result = validated_result
                request.processing_time = processing_time
                
                # Update metrics
                with self._metrics_lock:
                    self.metrics.update(
                        success=True, 
                        processing_time=processing_time,
                        api_used=result.get("_api_source", "unknown"),
                        cache_hit=result.get("_from_cache", False)
                    )
                
                logger.info(f"Successfully processed MST: {mst} in {processing_time:.2f}s")
                return validated_result
                
            except Exception as e:
                # Handle failure
                processing_time = time.time() - start_time
                request.status = ProcessingStatus.FAILED
                request.completed_at = datetime.now()
                request.error = str(e)
                request.processing_time = processing_time
                
                # Update metrics
                with self._metrics_lock:
                    self.metrics.update(
                        success=False, 
                        processing_time=processing_time
                    )
                
                logger.error(f"Failed to process MST: {mst} in {processing_time:.2f}s - {str(e)}")
                raise
                
        finally:
            # Cleanup
            with self._metrics_lock:
                self.metrics.current_concurrent_requests = max(0, self.metrics.current_concurrent_requests - 1)
            
            # Remove from queue after some time (keep for debugging)
            threading.Timer(300, lambda: self.processing_queue.pop(mst, None)).start()
    
    def _execute_intelligent_routing(self, mst: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Execute intelligent API routing based on strategy
        """
        if self.api_strategy == APIStrategy.ENTERPRISE_FIRST:
            return self._enterprise_first_strategy(mst, force_refresh)
        elif self.api_strategy == APIStrategy.VSS_ONLY:
            return self._vss_only_strategy(mst, force_refresh)
        elif self.api_strategy == APIStrategy.PARALLEL:
            return self._parallel_strategy(mst, force_refresh)
        elif self.api_strategy == APIStrategy.AUTO:
            return self._auto_strategy(mst, force_refresh)
        else:
            raise ValueError(f"Unknown API strategy: {self.api_strategy}")
    
    def _enterprise_first_strategy(self, mst: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Enterprise API first, fallback to VSS API"""
        
        # Try Enterprise API first
        if self.enterprise_client:
            try:
                result = self.enterprise_client.get_company_info(mst)
                if result and result.get("mst"):
                    result["_api_source"] = "enterprise"
                    result["_from_cache"] = False
                    logger.info(f"Enterprise API success for MST: {mst}")
                    return result
            except Exception as e:
                logger.warning(f"Enterprise API failed for MST: {mst}: {e}")
        
        # Fallback to VSS API
        try:
            result = self.vss_client.get_company_info(mst, force_refresh)
            result["_api_source"] = "vss"
            logger.info(f"VSS API success for MST: {mst}")
            return result
        except Exception as e:
            logger.error(f"Both APIs failed for MST: {mst}")
            raise Exception(f"All API attempts failed. Last error: {e}")
    
    def _vss_only_strategy(self, mst: str, force_refresh: bool = False) -> Dict[str, Any]:
        """VSS API only"""
        result = self.vss_client.get_company_info(mst, force_refresh)
        result["_api_source"] = "vss"
        return result
    
    def _parallel_strategy(self, mst: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Execute both APIs in parallel and return first successful result"""
        
        def call_enterprise():
            if self.enterprise_client:
                try:
                    result = self.enterprise_client.get_company_info(mst)
                    if result and result.get("mst"):
                        result["_api_source"] = "enterprise"
                        return result
                except:
                    pass
            return None
        
        def call_vss():
            try:
                result = self.vss_client.get_company_info(mst, force_refresh)
                result["_api_source"] = "vss"
                return result
            except:
                return None
        
        # Execute in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_enterprise = executor.submit(call_enterprise)
            future_vss = executor.submit(call_vss)
            
            # Wait for first successful result
            for future in concurrent.futures.as_completed([future_enterprise, future_vss], timeout=30):
                try:
                    result = future.result()
                    if result:
                        return result
                except Exception as e:
                    logger.warning(f"Parallel API call failed: {e}")
        
        raise Exception("All parallel API attempts failed")
    
    def _auto_strategy(self, mst: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Auto strategy based on current performance metrics"""
        
        # Decide strategy based on success rates
        enterprise_rate = self.metrics.enterprise_success_rate
        vss_rate = self.metrics.vss_success_rate
        
        if enterprise_rate > 80:
            # Enterprise API is performing well
            return self._enterprise_first_strategy(mst, force_refresh)
        elif vss_rate > enterprise_rate:
            # VSS API is performing better
            return self._vss_only_strategy(mst, force_refresh)
        else:
            # Use parallel approach when unsure
            return self._parallel_strategy(mst, force_refresh)
    
    def batch_process(self, 
                     mst_list: List[str], 
                     callback: Optional[Callable] = None,
                     progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Process multiple MST in parallel with progress tracking
        
        Args:
            mst_list: List of MST to process
            callback: Callback function for each completed item
            progress_callback: Progress update callback
            
        Returns:
            List of results
        """
        start_time = time.time()
        results = []
        completed = 0
        total = len(mst_list)
        
        logger.info(f"Starting batch processing of {total} MST codes")
        
        def process_single(mst: str) -> Tuple[str, Dict[str, Any]]:
            """Process single MST and return result"""
            try:
                result = self.get_company_info(mst)
                return mst, {"success": True, "data": result}
            except Exception as e:
                return mst, {"success": False, "error": str(e)}
        
        # Process in batches to avoid overwhelming the system
        batch_size = min(self.max_concurrent_requests, total)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Submit all tasks
            future_to_mst = {executor.submit(process_single, mst): mst for mst in mst_list}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_mst):
                mst, result = future.result()
                results.append({
                    "mst": mst,
                    **result
                })
                
                completed += 1
                
                # Execute callbacks
                if callback:
                    callback(mst, result)
                    
                if progress_callback:
                    progress_callback(completed, total, (completed/total)*100)
                
                # Log progress every 10%
                if completed % max(1, total // 10) == 0:
                    progress = (completed / total) * 100
                    elapsed = time.time() - start_time
                    estimated_total = elapsed / (completed / total)
                    remaining = estimated_total - elapsed
                    
                    logger.info(f"Batch progress: {completed}/{total} ({progress:.1f}%) "
                              f"- Elapsed: {elapsed:.1f}s - Remaining: {remaining:.1f}s")
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r.get("success", False))
        success_rate = (success_count / total) * 100
        
        logger.info(f"Batch processing completed: {success_count}/{total} ({success_rate:.1f}%) "
                   f"in {total_time:.1f}s - Avg: {total_time/total:.2f}s per item")
        
        return results
    
    def get_processing_status(self, mst: str = None) -> Dict[str, Any]:
        """Get current processing status"""
        with self._queue_lock:
            if mst:
                request = self.processing_queue.get(mst)
                if request:
                    return {
                        "mst": mst,
                        "status": request.status.value,
                        "created_at": request.created_at.isoformat(),
                        "started_at": request.started_at.isoformat() if request.started_at else None,
                        "completed_at": request.completed_at.isoformat() if request.completed_at else None,
                        "processing_time": request.processing_time,
                        "current_attempt": request.current_attempt,
                        "max_retries": request.max_retries,
                        "error": request.error
                    }
                return {"mst": mst, "status": "not_found"}
            else:
                # Return overall status
                total_requests = len(self.processing_queue)
                status_counts = {}
                for request in self.processing_queue.values():
                    status = request.status.value
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                return {
                    "total_requests": total_requests,
                    "status_breakdown": status_counts,
                    "queue_snapshot": list(self.processing_queue.keys())
                }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        with self._metrics_lock:
            metrics_dict = {
                "current_metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "success_rate": self.metrics.success_rate,
                    "average_processing_time": self.metrics.average_processing_time,
                    "current_concurrent_requests": self.metrics.current_concurrent_requests,
                    "peak_concurrent_requests": self.metrics.peak_concurrent_requests
                },
                "api_performance": {
                    "enterprise_api": {
                        "success_count": self.metrics.enterprise_api_success,
                        "failure_count": self.metrics.enterprise_api_failures,
                        "success_rate": self.metrics.enterprise_success_rate
                    },
                    "vss_api": {
                        "success_count": self.metrics.vss_api_success,
                        "failure_count": self.metrics.vss_api_failures,
                        "success_rate": self.metrics.vss_success_rate
                    }
                },
                "caching": {
                    "cache_hits": self.metrics.cache_hits,
                    "cache_misses": self.metrics.cache_misses,
                    "cache_hit_rate": (self.metrics.cache_hits / max(1, self.metrics.cache_hits + self.metrics.cache_misses)) * 100
                },
                "configuration": {
                    "api_strategy": self.api_strategy.value,
                    "max_concurrent_requests": self.max_concurrent_requests,
                    "caching_enabled": self.enable_caching,
                    "monitoring_enabled": self.enable_monitoring
                }
            }
        
        # Add performance history if available
        if self.performance_history:
            metrics_dict["performance_history"] = self.performance_history[-20:]  # Last 20 snapshots
        
        # Add VSS client metrics
        if self.vss_client:
            metrics_dict["vss_client_metrics"] = self.vss_client.get_performance_metrics()
            
        return metrics_dict
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "processor": {
                "api_strategy": self.api_strategy.value,
                "concurrent_requests": self.metrics.current_concurrent_requests,
                "queue_size": len(self.processing_queue),
                "thread_pool_active": not self.executor._shutdown
            },
            "clients": {},
            "metrics_summary": {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.success_rate,
                "average_response_time": self.metrics.average_processing_time
            }
        }
        
        # Check Enterprise client
        if self.enterprise_client:
            try:
                enterprise_health = self.enterprise_client.health_check()
                health["clients"]["enterprise"] = enterprise_health
            except Exception as e:
                health["clients"]["enterprise"] = {"status": "unhealthy", "error": str(e)}
        else:
            health["clients"]["enterprise"] = {"status": "not_configured"}
        
        # Check VSS client
        try:
            vss_health = self.vss_client.health_check()
            health["clients"]["vss"] = vss_health
            if vss_health.get("status") != "healthy":
                health["status"] = "degraded"
        except Exception as e:
            health["clients"]["vss"] = {"status": "unhealthy", "error": str(e)}
            health["status"] = "unhealthy"
        
        return health
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Auto-optimize performance based on metrics"""
        optimizations = []
        
        # Analyze current performance
        metrics = self.get_performance_metrics()
        
        # Adjust API strategy based on performance
        enterprise_rate = metrics["api_performance"]["enterprise_api"]["success_rate"]
        vss_rate = metrics["api_performance"]["vss_api"]["success_rate"]
        
        if enterprise_rate < 50 and vss_rate > 80:
            if self.api_strategy != APIStrategy.VSS_ONLY:
                self.api_strategy = APIStrategy.VSS_ONLY
                optimizations.append("Switched to VSS_ONLY strategy due to poor Enterprise API performance")
        elif enterprise_rate > 90 and self.api_strategy != APIStrategy.ENTERPRISE_FIRST:
            self.api_strategy = APIStrategy.ENTERPRISE_FIRST
            optimizations.append("Switched to ENTERPRISE_FIRST strategy due to excellent Enterprise API performance")
        
        # Adjust concurrent requests based on success rate
        current_success_rate = metrics["current_metrics"]["success_rate"]
        if current_success_rate < 80 and self.max_concurrent_requests > 5:
            self.max_concurrent_requests = max(5, self.max_concurrent_requests - 2)
            optimizations.append(f"Reduced concurrent requests to {self.max_concurrent_requests} to improve success rate")
        elif current_success_rate > 95 and self.max_concurrent_requests < 20:
            self.max_concurrent_requests += 2
            optimizations.append(f"Increased concurrent requests to {self.max_concurrent_requests} for better throughput")
        
        # Clear cache if hit rate is low
        cache_hit_rate = metrics["caching"]["cache_hit_rate"]
        if cache_hit_rate < 10 and self.vss_client:
            self.vss_client.clear_cache()
            optimizations.append("Cleared cache due to low hit rate")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": optimizations,
            "current_config": {
                "api_strategy": self.api_strategy.value,
                "max_concurrent_requests": self.max_concurrent_requests
            }
        }
    
    def export_metrics(self, filepath: str = None) -> str:
        """Export metrics to file"""
        if not filepath:
            filepath = f"vss_processor_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        metrics_data = {
            "export_timestamp": datetime.now().isoformat(),
            "processor_config": {
                "api_strategy": self.api_strategy.value,
                "max_concurrent_requests": self.max_concurrent_requests,
                "enable_caching": self.enable_caching,
                "enable_monitoring": self.enable_monitoring
            },
            "performance_metrics": self.get_performance_metrics(),
            "processing_queue": {
                mst: {
                    "status": req.status.value,
                    "created_at": req.created_at.isoformat(),
                    "processing_time": req.processing_time,
                    "error": req.error
                } for mst, req in self.processing_queue.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metrics exported to: {filepath}")
        return filepath
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down OptimizedVSSProcessor...")
        
        # Stop monitoring
        self.enable_monitoring = False
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        logger.info("OptimizedVSSProcessor shutdown completed")

# Factory function
def create_optimized_processor(config: Dict[str, Any] = None, 
                             api_strategy: str = "enterprise_first") -> OptimizedVSSProcessor:
    """
    Factory function để tạo Optimized VSS Processor
    
    Args:
        config: Configuration dict
        api_strategy: API strategy ("enterprise_first", "vss_only", "parallel", "auto")
        
    Returns:
        Configured OptimizedVSSProcessor
    """
    strategy_map = {
        "enterprise_first": APIStrategy.ENTERPRISE_FIRST,
        "vss_only": APIStrategy.VSS_ONLY,
        "parallel": APIStrategy.PARALLEL,
        "auto": APIStrategy.AUTO
    }
    
    return OptimizedVSSProcessor(
        config=config,
        api_strategy=strategy_map.get(api_strategy, APIStrategy.ENTERPRISE_FIRST),
        max_concurrent_requests=10,
        enable_caching=True,
        enable_monitoring=True
    )

if __name__ == "__main__":
    # Test code
    processor = create_optimized_processor()
    
    # Test single request
    try:
        result = processor.get_company_info("0123456789")
        print(f"Single request result: {result}")
        
        # Get metrics
        metrics = processor.get_performance_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
        
        # Health check
        health = processor.health_check()
        print(f"Health: {json.dumps(health, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        processor.shutdown()