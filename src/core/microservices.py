"""
Microservices architecture framework
"""
import asyncio
import json
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod
import queue
from ..utils.logger import setup_module_logger


class Message:
    """Message for inter-service communication"""

    def __init__(self, message_type: str, payload: Dict[str, Any],
                 source_service: str, target_service: Optional[str] = None,
                 correlation_id: Optional[str] = None):
        self.message_type = message_type
        self.payload = payload
        self.source_service = source_service
        self.target_service = target_service
        self.correlation_id = correlation_id or self._generate_id()
        self.timestamp = time.time()
        self.ttl = 300  # 5 minutes default TTL

    def _generate_id(self) -> str:
        """Generate unique correlation ID"""
        import uuid
        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_type': self.message_type,
            'payload': self.payload,
            'source_service': self.source_service,
            'target_service': self.target_service,
            'correlation_id': self.correlation_id,
            'timestamp': self.timestamp,
            'ttl': self.ttl
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        msg = cls(
            message_type=data['message_type'],
            payload=data['payload'],
            source_service=data['source_service'],
            target_service=data.get('target_service'),
            correlation_id=data.get('correlation_id')
        )
        msg.timestamp = data.get('timestamp', time.time())
        msg.ttl = data.get('ttl', 300)
        return msg

    def is_expired(self) -> bool:
        """Check if message is expired"""
        return time.time() - self.timestamp > self.ttl


class ServiceBus:
    """Central message bus for inter-service communication"""

    def __init__(self):
        self.logger = setup_module_logger("service_bus")
        self.services: Dict[str, 'Microservice'] = {}
        self.message_queue = queue.Queue()
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

    def register_service(self, service: 'Microservice'):
        """Register a service with the bus"""
        self.services[service.service_name] = service
        self.logger.info(f"Registered service: {service.service_name}")

    def unregister_service(self, service_name: str):
        """Unregister a service"""
        if service_name in self.services:
            del self.services[service_name]
            self.logger.info(f"Unregistered service: {service_name}")

    def send_message(self, message: Message):
        """Send message to queue"""
        if not message.is_expired():
            self.message_queue.put(message)
        else:
            self.logger.warning(f"Discarded expired message: {message.correlation_id}")

    def broadcast_message(self, message: Message):
        """Broadcast message to all services"""
        for service_name, service in self.services.items():
            if service_name != message.source_service:
                targeted_message = Message(
                    message_type=message.message_type,
                    payload=message.payload,
                    source_service=message.source_service,
                    target_service=service_name,
                    correlation_id=message.correlation_id
                )
                self.send_message(targeted_message)

    def start(self):
        """Start the service bus"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._message_worker, daemon=True)
        self.worker_thread.start()
        self.logger.info("Service bus started")

    def stop(self):
        """Stop the service bus"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.logger.info("Service bus stopped")

    def _message_worker(self):
        """Background message processing worker"""
        while self.running:
            try:
                # Get message with timeout
                message = self.message_queue.get(timeout=1)

                # Route message to target service
                if message.target_service and message.target_service in self.services:
                    service = self.services[message.target_service]
                    # Run in thread pool to avoid blocking
                    executor = ThreadPoolExecutor(max_workers=1)
                    executor.submit(self._deliver_message, service, message)
                    executor.shutdown(wait=False)
                elif not message.target_service:
                    # Broadcast to all services
                    self.broadcast_message(message)
                else:
                    self.logger.warning(f"No service found for message: {message.target_service}")

                self.message_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Message processing error: {e}")

    def _deliver_message(self, service: 'Microservice', message: Message):
        """Deliver message to service"""
        try:
            service.receive_message(message)
        except Exception as e:
            self.logger.error(f"Failed to deliver message to {service.service_name}: {e}")


class Microservice(ABC):
    """Base class for microservices"""

    def __init__(self, service_name: str, service_bus: ServiceBus):
        self.service_name = service_name
        self.service_bus = service_bus
        self.logger = setup_module_logger(f"service.{service_name}")
        self.running = False
        self.message_handlers: Dict[str, Callable] = {}

        # Register with service bus
        self.service_bus.register_service(self)

        # Register default message handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers"""
        self.register_handler('ping', self._handle_ping)
        self.register_handler('health_check', self._handle_health_check)
        self.register_handler('shutdown', self._handle_shutdown)

    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler

    def unregister_handler(self, message_type: str):
        """Unregister message handler"""
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]

    def send_message(self, message_type: str, payload: Dict[str, Any],
                    target_service: Optional[str] = None) -> str:
        """Send message via service bus"""
        message = Message(
            message_type=message_type,
            payload=payload,
            source_service=self.service_name,
            target_service=target_service
        )
        self.service_bus.send_message(message)
        return message.correlation_id

    def receive_message(self, message: Message):
        """Receive and process message"""
        if message.message_type in self.message_handlers:
            handler = self.message_handlers[message.message_type]
            try:
                response = handler(message)
                if response is not None:
                    # Send response back if correlation_id exists
                    if message.correlation_id:
                        self.send_message(
                            message_type=f"{message.message_type}_response",
                            payload={'result': response, 'original_correlation_id': message.correlation_id},
                            target_service=message.source_service
                        )
            except Exception as e:
                self.logger.error(f"Message handler error: {e}")
                # Send error response
                if message.correlation_id:
                    self.send_message(
                        message_type=f"{message.message_type}_error",
                        payload={'error': str(e), 'original_correlation_id': message.correlation_id},
                        target_service=message.source_service
                    )
        else:
            self.logger.warning(f"No handler for message type: {message.message_type}")

    def start(self):
        """Start the service"""
        self.running = True
        self.logger.info(f"Service {self.service_name} started")

    def stop(self):
        """Stop the service"""
        self.running = False
        self.service_bus.unregister_service(self.service_name)
        self.logger.info(f"Service {self.service_name} stopped")

    @abstractmethod
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process service-specific request"""
        pass

    def _handle_ping(self, message: Message) -> Dict[str, Any]:
        """Handle ping messages"""
        return {'status': 'pong', 'service': self.service_name, 'timestamp': time.time()}

    def _handle_health_check(self, message: Message) -> Dict[str, Any]:
        """Handle health check messages"""
        return {
            'service': self.service_name,
            'status': 'healthy' if self.running else 'unhealthy',
            'timestamp': time.time()
        }

    def _handle_shutdown(self, message: Message) -> Dict[str, Any]:
        """Handle shutdown messages"""
        self.stop()
        return {'status': 'shutdown', 'service': self.service_name}


class VSSProcessingService(Microservice):
    """VSS processing microservice"""

    def __init__(self, service_bus: ServiceBus):
        super().__init__('vss_processor', service_bus)
        # Import here to avoid circular imports
        from ..processors.vss_processor import VSSIntegrationProcessor
        self.processor = VSSIntegrationProcessor(max_workers=2)

        # Register specific handlers
        self.register_handler('process_mst', self._handle_process_mst)
        self.register_handler('batch_process', self._handle_batch_process)

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process VSS integration request"""
        request_type = request.get('type', 'single')

        if request_type == 'single':
            mst = request.get('mst', '')
            return self.processor.process_single_mst(mst).to_dict()
        elif request_type == 'batch':
            msts = request.get('msts', [])
            results = self.processor.process_batch(msts)
            return {'results': [r.to_dict() for r in results]}
        else:
            raise ValueError(f"Unknown request type: {request_type}")

    def _handle_process_mst(self, message: Message) -> Dict[str, Any]:
        """Handle MST processing request"""
        mst = message.payload.get('mst', '')
        result = self.processor.process_single_mst(mst)
        return result.to_dict()

    def _handle_batch_process(self, message: Message) -> Dict[str, Any]:
        """Handle batch processing request"""
        msts = message.payload.get('msts', [])
        results = self.processor.process_batch(msts)
        return {'results': [r.to_dict() for r in results]}


class AnalyticsService(Microservice):
    """Analytics microservice"""

    def __init__(self, service_bus: ServiceBus):
        super().__init__('analytics', service_bus)
        from ..utils.analytics import get_analytics_engine
        self.analytics_engine = get_analytics_engine()

        # Register specific handlers
        self.register_handler('analyze_results', self._handle_analyze_results)
        self.register_handler('generate_report', self._handle_generate_report)

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process analytics request"""
        action = request.get('action', 'analyze')

        if action == 'analyze':
            results = request.get('results', [])
            return self.analytics_engine.analyze_processing_results(results)
        elif action == 'report':
            results = request.get('results', [])
            format_type = request.get('format', 'json')
            return self.analytics_engine.generate_report(results, format_type)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_analyze_results(self, message: Message) -> Dict[str, Any]:
        """Handle results analysis request"""
        results = message.payload.get('results', [])
        return self.analytics_engine.analyze_processing_results(results)

    def _handle_generate_report(self, message: Message) -> Dict[str, Any]:
        """Handle report generation request"""
        results = message.payload.get('results', [])
        format_type = message.payload.get('format', 'json')
        return {'report': self.analytics_engine.generate_report(results, format_type)}


class MonitoringService(Microservice):
    """Monitoring and metrics microservice"""

    def __init__(self, service_bus: ServiceBus):
        super().__init__('monitoring', service_bus)
        from ..utils.performance_monitor import get_performance_monitor
        from ..utils.prometheus_metrics import get_metrics_collector

        self.performance_monitor = get_performance_monitor()
        self.metrics_collector = get_metrics_collector()

        # Register specific handlers
        self.register_handler('get_metrics', self._handle_get_metrics)
        self.register_handler('performance_report', self._handle_performance_report)

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process monitoring request"""
        metric_type = request.get('metric_type', 'performance')

        if metric_type == 'performance':
            return self.performance_monitor.get_performance_report()
        elif metric_type == 'prometheus':
            return {'metrics': 'Available at /metrics endpoint'}
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

    def _handle_get_metrics(self, message: Message) -> Dict[str, Any]:
        """Handle metrics request"""
        return self.performance_monitor.get_performance_report()

    def _handle_performance_report(self, message: Message) -> Dict[str, Any]:
        """Handle performance report request"""
        return self.performance_monitor.get_performance_report()


# Global service bus instance
service_bus = ServiceBus()


def get_service_bus() -> ServiceBus:
    """Get global service bus instance"""
    return service_bus


def start_microservices():
    """Start all microservices"""
    global service_bus

    # Create services
    vss_service = VSSProcessingService(service_bus)
    analytics_service = AnalyticsService(service_bus)
    monitoring_service = MonitoringService(service_bus)

    # Start service bus
    service_bus.start()

    # Start services
    vss_service.start()
    analytics_service.start()
    monitoring_service.start()

    return [vss_service, analytics_service, monitoring_service]


def stop_microservices(services: List[Microservice]):
    """Stop all microservices"""
    global service_bus

    for service in services:
        service.stop()

    service_bus.stop()