"""
Performance monitoring utilities
"""
import time
import psutil
import threading
from typing import Dict, Any, Optional
from collections import deque
import gc
from ..utils.logger import setup_module_logger


class PerformanceMonitor:
    """Monitor system performance and memory usage"""

    def __init__(self, max_samples: int = 100):
        self.logger = setup_module_logger("performance_monitor")
        self.max_samples = max_samples
        self.cpu_samples = deque(maxlen=max_samples)
        self.memory_samples = deque(maxlen=max_samples)
        self.gc_stats = deque(maxlen=max_samples)
        self.start_time = time.time()
        self._lock = threading.Lock()

        # Start monitoring thread
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                with self._lock:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_samples.append({
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent
                    })

                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_samples.append({
                        'timestamp': time.time(),
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used
                    })

                    # GC stats
                    self.gc_stats.append({
                        'timestamp': time.time(),
                        'collections': gc.get_count(),
                        'stats': gc.get_stats()
                    })

            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")

            time.sleep(5)  # Sample every 5 seconds

    def get_cpu_stats(self) -> Dict[str, Any]:
        """Get CPU usage statistics"""
        with self._lock:
            if not self.cpu_samples:
                return {'current': 0, 'avg': 0, 'max': 0, 'min': 0}

            current = self.cpu_samples[-1]['cpu_percent'] if self.cpu_samples else 0
            values = [s['cpu_percent'] for s in self.cpu_samples]

            return {
                'current': current,
                'avg': sum(values) / len(values),
                'max': max(values),
                'min': min(values),
                'samples': len(values)
            }

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        with self._lock:
            if not self.memory_samples:
                return {'current_percent': 0, 'avg_percent': 0, 'max_percent': 0}

            current = self.memory_samples[-1] if self.memory_samples else {}
            values = [s['percent'] for s in self.memory_samples]

            return {
                'current': current.get('used', 0),
                'current_percent': current.get('percent', 0),
                'total': current.get('total', 0),
                'available': current.get('available', 0),
                'avg_percent': sum(values) / len(values) if values else 0,
                'max_percent': max(values) if values else 0,
                'samples': len(values)
            }

    def get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics"""
        with self._lock:
            if not self.gc_stats:
                return {'collections': [0, 0, 0], 'objects_collected': 0}

            latest = self.gc_stats[-1] if self.gc_stats else {}
            collections = latest.get('collections', [0, 0, 0])

            return {
                'collections': collections,
                'total_objects': sum(collections),
                'stats': latest.get('stats', [])
            }

    def force_gc(self) -> Dict[str, Any]:
        """Force garbage collection and return stats"""
        before = gc.get_count()
        collected = gc.collect()
        after = gc.get_count()

        stats = {
            'collected': collected,
            'before': before,
            'after': after,
            'reduction': [b - a for b, a in zip(before, after)]
        }

        self.logger.info(f"GC: collected {collected} objects, counts: {before} -> {after}")
        return stats

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'cpu': self.get_cpu_stats(),
            'memory': self.get_memory_stats(),
            'gc': self.get_gc_stats(),
            'process_info': {
                'pid': psutil.Process().pid,
                'threads': len(psutil.Process().threads()),
                'open_files': len(psutil.Process().open_files())
            }
        }

    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        self.logger.info("Starting memory optimization...")

        # Force garbage collection
        gc_stats = self.force_gc()

        # Clear any cached data if possible
        # This would be implemented based on specific cache clearing needs

        # Get memory stats after optimization
        after_stats = self.get_memory_stats()

        return {
            'gc_stats': gc_stats,
            'memory_after': after_stats,
            'optimization_time': time.time()
        }

    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self._monitoring = False
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return performance_monitor