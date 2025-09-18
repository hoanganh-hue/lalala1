"""
Prometheus metrics for monitoring
"""
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
from typing import Optional
import time
from ..utils.logger import setup_module_logger


class MetricsCollector:
    """Collect and expose Prometheus metrics"""

    def __init__(self):
        self.logger = setup_module_logger("metrics")

        # Counter metrics
        self.requests_total = Counter(
            'vss_requests_total',
            'Total number of requests processed',
            ['method', 'endpoint', 'status']
        )

        self.api_calls_total = Counter(
            'vss_api_calls_total',
            'Total number of external API calls',
            ['api_name', 'status']
        )

        self.processing_errors_total = Counter(
            'vss_processing_errors_total',
            'Total number of processing errors',
            ['error_type']
        )

        # Gauge metrics
        self.active_connections = Gauge(
            'vss_active_connections',
            'Number of active connections'
        )

        self.memory_usage = Gauge(
            'vss_memory_usage_bytes',
            'Current memory usage in bytes'
        )

        self.cpu_usage = Gauge(
            'vss_cpu_usage_percent',
            'Current CPU usage percentage'
        )

        self.active_workers = Gauge(
            'vss_active_workers',
            'Number of active worker threads'
        )

        # Histogram metrics
        self.request_duration = Histogram(
            'vss_request_duration_seconds',
            'Request processing duration',
            ['method', 'endpoint'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
        )

        self.api_call_duration = Histogram(
            'vss_api_call_duration_seconds',
            'External API call duration',
            ['api_name'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
        )

        # Summary metrics
        self.processing_time_summary = Summary(
            'vss_processing_time_summary',
            'Processing time summary',
            ['operation']
        )

        # Business metrics
        self.compliance_score = Histogram(
            'vss_compliance_score',
            'Compliance score distribution',
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        )

        self.data_quality_gauge = Gauge(
            'vss_data_quality',
            'Current data quality score',
            ['quality_level']
        )

    def record_request(self, method: str, endpoint: str, status: str, duration: float):
        """Record HTTP request metrics"""
        self.requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_api_call(self, api_name: str, status: str, duration: float):
        """Record external API call metrics"""
        self.api_calls_total.labels(api_name=api_name, status=status).inc()
        self.api_call_duration.labels(api_name=api_name).observe(duration)

    def record_processing_error(self, error_type: str):
        """Record processing error"""
        self.processing_errors_total.labels(error_type=error_type).inc()

    def update_system_metrics(self, memory_bytes: int, cpu_percent: float, active_workers: int):
        """Update system resource metrics"""
        self.memory_usage.set(memory_bytes)
        self.cpu_usage.set(cpu_percent)
        self.active_workers.set(active_workers)

    def record_compliance_score(self, score: float):
        """Record compliance score"""
        self.compliance_score.observe(score)

    def update_data_quality(self, quality_level: str, score: float):
        """Update data quality metrics"""
        # Reset all quality levels first
        for level in ['HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']:
            self.data_quality_gauge.labels(quality_level=level).set(0)

        # Set current quality level
        self.data_quality_gauge.labels(quality_level=quality_level).set(score)

    def record_processing_time(self, operation: str, duration: float):
        """Record processing time"""
        self.processing_time_summary.labels(operation=operation).observe(duration)

    def increment_active_connections(self):
        """Increment active connections counter"""
        self.active_connections.inc()

    def decrement_active_connections(self):
        """Decrement active connections counter"""
        self.active_connections.dec()


# Global metrics collector
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    return metrics_collector


def start_metrics_server(port: int = 8000):
    """Start Prometheus metrics HTTP server"""
    try:
        start_http_server(port)
        logger = setup_module_logger("metrics_server")
        logger.info(f"Prometheus metrics server started on port {port}")
        logger.info(f"Metrics available at http://localhost:{port}/metrics")
    except Exception as e:
        logger = setup_module_logger("metrics_server")
        logger.error(f"Failed to start metrics server: {e}")


# Initialize metrics server when module is imported
# This will be called from main application
def init_metrics():
    """Initialize metrics collection"""
    # Metrics server will be started by the main application
    pass