"""
Performance monitoring and health checks

Tracks metrics, response times, and system health for the MCP server.
"""

import time
import psutil
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict, deque
import threading


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    tool_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-level metrics"""
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_percent: float
    uptime_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """Monitor performance and track metrics"""

    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor

        Args:
            max_history: Maximum number of historical metrics to keep
        """
        self.max_history = max_history
        self.start_time = time.time()

        # Metrics storage
        self.request_history: deque = deque(maxlen=max_history)
        self.tool_stats: Dict[str, List[float]] = defaultdict(list)
        self.error_count: Dict[str, int] = defaultdict(int)
        self.success_count: Dict[str, int] = defaultdict(int)

        # Thread safety
        self.lock = threading.Lock()

    def start_request(self, tool_name: str) -> RequestMetrics:
        """
        Start tracking a request

        Args:
            tool_name: Name of the tool being called

        Returns:
            RequestMetrics instance
        """
        return RequestMetrics(
            tool_name=tool_name,
            start_time=time.time()
        )

    def end_request(self, metrics: RequestMetrics, success: bool = True, error: Optional[str] = None) -> None:
        """
        End tracking a request and record metrics

        Args:
            metrics: RequestMetrics instance from start_request
            success: Whether the request succeeded
            error: Error message if failed
        """
        metrics.end_time = time.time()
        metrics.duration_ms = (metrics.end_time - metrics.start_time) * 1000
        metrics.success = success
        metrics.error = error

        with self.lock:
            self.request_history.append(metrics)
            self.tool_stats[metrics.tool_name].append(metrics.duration_ms)

            if success:
                self.success_count[metrics.tool_name] += 1
            else:
                self.error_count[metrics.tool_name] += 1

    def get_tool_stats(self, tool_name: str) -> Dict:
        """
        Get statistics for a specific tool

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with statistics
        """
        with self.lock:
            durations = self.tool_stats.get(tool_name, [])
            if not durations:
                return {
                    'tool_name': tool_name,
                    'call_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'avg_duration_ms': 0,
                    'min_duration_ms': 0,
                    'max_duration_ms': 0
                }

            return {
                'tool_name': tool_name,
                'call_count': len(durations),
                'success_count': self.success_count[tool_name],
                'error_count': self.error_count[tool_name],
                'success_rate': self.success_count[tool_name] / len(durations) if durations else 0,
                'avg_duration_ms': sum(durations) / len(durations),
                'min_duration_ms': min(durations),
                'max_duration_ms': max(durations),
                'p50_duration_ms': sorted(durations)[len(durations) // 2],
                'p95_duration_ms': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations)
            }

    def get_all_stats(self) -> Dict:
        """
        Get statistics for all tools

        Returns:
            Dictionary with all statistics
        """
        with self.lock:
            all_tools = set(self.tool_stats.keys())
            return {
                'total_requests': len(self.request_history),
                'total_success': sum(self.success_count.values()),
                'total_errors': sum(self.error_count.values()),
                'uptime_seconds': time.time() - self.start_time,
                'tools': {tool: self.get_tool_stats(tool) for tool in all_tools}
            }

    def get_recent_requests(self, count: int = 10) -> List[Dict]:
        """
        Get most recent requests

        Args:
            count: Number of recent requests to return

        Returns:
            List of request dictionaries
        """
        with self.lock:
            recent = list(self.request_history)[-count:]
            return [
                {
                    'tool_name': req.tool_name,
                    'duration_ms': req.duration_ms,
                    'success': req.success,
                    'error': req.error,
                    'timestamp': datetime.fromtimestamp(req.start_time).isoformat()
                }
                for req in recent
            ]

    def reset(self) -> None:
        """Reset all metrics"""
        with self.lock:
            self.request_history.clear()
            self.tool_stats.clear()
            self.error_count.clear()
            self.success_count.clear()
            self.start_time = time.time()


class HealthCheck:
    """Health check utilities"""

    @staticmethod
    def get_system_metrics() -> SystemMetrics:
        """
        Get current system metrics

        Returns:
            SystemMetrics instance
        """
        process = psutil.Process(os.getpid())

        return SystemMetrics(
            cpu_percent=process.cpu_percent(interval=0.1),
            memory_percent=process.memory_percent(),
            memory_mb=process.memory_info().rss / (1024 * 1024),
            disk_percent=psutil.disk_usage('/').percent,
            uptime_seconds=time.time() - process.create_time()
        )

    @staticmethod
    def check_health() -> Dict:
        """
        Perform health check

        Returns:
            Dictionary with health status
        """
        try:
            metrics = HealthCheck.get_system_metrics()

            # Determine health status
            issues = []
            if metrics.cpu_percent > 80:
                issues.append("High CPU usage")
            if metrics.memory_percent > 80:
                issues.append("High memory usage")
            if metrics.disk_percent > 90:
                issues.append("Low disk space")

            status = "healthy" if not issues else "degraded"

            return {
                'status': status,
                'timestamp': metrics.timestamp.isoformat(),
                'uptime_seconds': metrics.uptime_seconds,
                'system': {
                    'cpu_percent': metrics.cpu_percent,
                    'memory_percent': metrics.memory_percent,
                    'memory_mb': metrics.memory_mb,
                    'disk_percent': metrics.disk_percent
                },
                'issues': issues
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }


# Global monitor instance
_monitor = None


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()

    # Simulate some requests
    for i in range(10):
        metrics = monitor.start_request("search_gigs")
        time.sleep(0.1)  # Simulate work
        monitor.end_request(metrics, success=True)

    # Get statistics
    stats = monitor.get_all_stats()
    print("All Stats:", stats)

    tool_stats = monitor.get_tool_stats("search_gigs")
    print("\nTool Stats:", tool_stats)

    # Health check
    health = HealthCheck.check_health()
    print("\nHealth:", health)
