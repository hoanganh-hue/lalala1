"""
Real-time monitoring with WebSocket support
"""
import asyncio
import json
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import queue
from ..utils.logger import setup_module_logger


class RealTimeMonitor:
    """Real-time monitoring system with WebSocket support"""

    def __init__(self):
        self.logger = setup_module_logger("realtime_monitor")
        self.clients = set()
        self.monitoring_data = {}
        self.alerts_queue = queue.Queue()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_thread: Optional[threading.Thread] = None

        # Alert thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'error_rate': 0.1,  # 10%
            'response_time': 5.0,  # 5 seconds
            'queue_size': 100
        }

        # Alert callbacks
        self.alert_callbacks: List[Callable] = []

    def add_client(self, client):
        """Add WebSocket client"""
        self.clients.add(client)
        self.logger.info(f"Client connected. Total clients: {len(self.clients)}")

    def remove_client(self, client):
        """Remove WebSocket client"""
        self.clients.discard(client)
        self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    def update_metric(self, metric_name: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Update monitoring metric"""
        timestamp = datetime.now().isoformat()

        self.monitoring_data[metric_name] = {
            'value': value,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }

        # Check for alerts
        self._check_alerts(metric_name, value)

        # Broadcast to clients
        self._broadcast_update(metric_name, value, timestamp, metadata)

    def _check_alerts(self, metric_name: str, value: Any):
        """Check if metric triggers alert"""

        if metric_name in self.thresholds:
            threshold = self.thresholds[metric_name]

            if isinstance(value, (int, float)) and value > threshold:
                alert = {
                    'type': 'threshold_exceeded',
                    'metric': metric_name,
                    'value': value,
                    'threshold': threshold,
                    'timestamp': datetime.now().isoformat(),
                    'severity': 'high' if value > threshold * 1.5 else 'medium'
                }

                self.alerts_queue.put(alert)
                self._trigger_alert_callbacks(alert)

    def _broadcast_update(self, metric_name: str, value: Any, timestamp: str, metadata: Optional[Dict[str, Any]]):
        """Broadcast metric update to all clients"""
        if not self.clients:
            return

        message = {
            'type': 'metric_update',
            'metric': metric_name,
            'value': value,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }

        # Send to all clients (in separate thread to avoid blocking)
        def broadcast():
            disconnected_clients = set()
            for client in self.clients:
                try:
                    # This would be client.send_json(message) for actual WebSocket
                    # For now, we'll just log
                    pass
                except Exception as e:
                    self.logger.debug(f"Failed to send to client: {e}")
                    disconnected_clients.add(client)

            # Remove disconnected clients
            for client in disconnected_clients:
                self.remove_client(client)

        threading.Thread(target=broadcast, daemon=True).start()

    def add_alert_callback(self, callback: Callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable):
        """Remove alert callback function"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)

    def _trigger_alert_callbacks(self, alert: Dict[str, Any]):
        """Trigger all alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics"""
        return {
            'metrics': self.monitoring_data.copy(),
            'clients_connected': len(self.clients),
            'alerts_pending': self.alerts_queue.qsize(),
            'timestamp': datetime.now().isoformat()
        }

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts history"""
        alerts = []
        try:
            while len(alerts) < limit and not self.alerts_queue.empty():
                alerts.append(self.alerts_queue.get_nowait())
        except queue.Empty:
            pass

        return alerts

    def set_threshold(self, metric_name: str, threshold: float):
        """Set alert threshold for metric"""
        self.thresholds[metric_name] = threshold
        self.logger.info(f"Set threshold for {metric_name}: {threshold}")

    def start_monitoring(self):
        """Start real-time monitoring"""
        self.running = True

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        # Start alert processing thread
        self.alert_thread = threading.Thread(target=self._alert_processing_loop, daemon=True)
        self.alert_thread.start()

        self.logger.info("Real-time monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.running = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        if self.alert_thread:
            self.alert_thread.join(timeout=5)

        self.logger.info("Real-time monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        import psutil

        while self.running:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                self.update_metric('system.cpu_percent', cpu_percent)
                self.update_metric('system.memory_percent', memory.percent)
                self.update_metric('system.memory_used', memory.used)

                # Application-specific metrics (would be updated by application)
                # These are placeholders for actual metrics

                time.sleep(5)  # Update every 5 seconds

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)  # Wait longer on error

    def _alert_processing_loop(self):
        """Alert processing loop"""
        while self.running:
            try:
                # Process alerts (additional processing if needed)
                if not self.alerts_queue.empty():
                    alert = self.alerts_queue.get(timeout=1)
                    # Additional alert processing logic here
                    self.alerts_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")


class WebSocketManager:
    """WebSocket connection manager"""

    def __init__(self):
        self.logger = setup_module_logger("websocket_manager")
        self.connections = {}
        self.message_handlers = {}

    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler

    def handle_connection(self, websocket, client_id: str):
        """Handle WebSocket connection"""
        self.connections[client_id] = websocket

        try:
            # Connection loop
            while True:
                # Receive message
                message = websocket.receive_json()

                # Handle message
                self._handle_message(message, client_id, websocket)

        except Exception as e:
            self.logger.debug(f"WebSocket connection closed for {client_id}: {e}")
        finally:
            # Cleanup
            if client_id in self.connections:
                del self.connections[client_id]

    def _handle_message(self, message: Dict[str, Any], client_id: str, websocket):
        """Handle incoming WebSocket message"""
        message_type = message.get('type', 'unknown')

        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            try:
                response = handler(message, client_id)
                if response:
                    websocket.send_json(response)
            except Exception as e:
                self.logger.error(f"Message handler error: {e}")
                websocket.send_json({
                    'type': 'error',
                    'error': str(e),
                    'original_message': message
                })
        else:
            websocket.send_json({
                'type': 'error',
                'error': f'Unknown message type: {message_type}'
            })

    def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for client_id, websocket in self.connections.items():
            try:
                websocket.send_json(message)
            except Exception as e:
                self.logger.debug(f"Failed to broadcast to {client_id}: {e}")

    def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.connections:
            try:
                self.connections[client_id].send_json(message)
            except Exception as e:
                self.logger.debug(f"Failed to send to {client_id}: {e}")


# Global instances
realtime_monitor = RealTimeMonitor()
websocket_manager = WebSocketManager()


def get_realtime_monitor() -> RealTimeMonitor:
    """Get global real-time monitor instance"""
    return realtime_monitor


def get_websocket_manager() -> WebSocketManager:
    """Get global WebSocket manager instance"""
    return websocket_manager


# Initialize monitoring
def init_realtime_monitoring():
    """Initialize real-time monitoring system"""

    # Set up alert callback
    def alert_callback(alert):
        realtime_monitor.logger.warning(f"Alert triggered: {alert}")

        # Broadcast alert to WebSocket clients
        websocket_manager.broadcast({
            'type': 'alert',
            'data': alert
        })

    realtime_monitor.add_alert_callback(alert_callback)

    # Set up WebSocket message handlers
    def handle_subscribe(message, client_id):
        return {'type': 'subscribed', 'client_id': client_id}

    def handle_get_metrics(message, client_id):
        metrics = realtime_monitor.get_current_metrics()
        return {'type': 'metrics_response', 'data': metrics}

    def handle_get_alerts(message, client_id):
        alerts = realtime_monitor.get_alert_history()
        return {'type': 'alerts_response', 'data': alerts}

    websocket_manager.register_handler('subscribe', handle_subscribe)
    websocket_manager.register_handler('get_metrics', handle_get_metrics)
    websocket_manager.register_handler('get_alerts', handle_get_alerts)

    # Start monitoring
    realtime_monitor.start_monitoring()

    return realtime_monitor, websocket_manager