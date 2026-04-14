"""Metrics collection for monitoring."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: float
    timestamp: str
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Simple metrics collector for tracking system performance.
    
    Tracks:
    - Agent execution times
    - Token usage
    - Quality scores
    - Iteration counts
    - Error rates
    """
    
    def __init__(self):
        self._metrics: List[MetricPoint] = []
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
    
    def increment(self, name: str, value: int = 1, **labels) -> None:
        """Increment a counter."""
        key = self._make_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value
        
        self._metrics.append(MetricPoint(
            name=name,
            value=self._counters[key],
            timestamp=datetime.now().isoformat(),
            labels=labels
        ))
    
    def gauge(self, name: str, value: float, **labels) -> None:
        """Set a gauge value."""
        key = self._make_key(name, labels)
        self._gauges[key] = value
        
        self._metrics.append(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now().isoformat(),
            labels=labels
        ))
    
    def histogram(self, name: str, value: float, **labels) -> None:
        """Record a histogram value."""
        key = self._make_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
        
        self._metrics.append(MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now().isoformat(),
            labels=labels
        ))
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Create a unique key for a metric."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_counter(self, name: str, **labels) -> int:
        """Get current counter value."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)
    
    def get_gauge(self, name: str, **labels) -> Optional[float]:
        """Get current gauge value."""
        key = self._make_key(name, labels)
        return self._gauges.get(key)
    
    def get_histogram_stats(self, name: str, **labels) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(values)
        
        return {
            "count": count,
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / count,
            "p50": sorted_values[count // 2],
            "p95": sorted_values[int(count * 0.95)] if count >= 20 else sorted_values[-1],
            "p99": sorted_values[int(count * 0.99)] if count >= 100 else sorted_values[-1],
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: self.get_histogram_stats(k.split("{")[0])
                for k in self._histograms
            },
            "total_points": len(self._metrics)
        }
    
    def time_operation(self, name: str, **labels):
        """Context manager for timing operations."""
        return _TimerContext(self, name, labels)
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


class _TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: dict):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        self.collector.histogram(f"{self.name}_duration_ms", duration_ms, **self.labels)


# Global metrics instance
_global_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector()
    return _global_metrics


# Convenience functions
def record_agent_execution(
    agent: str,
    action: str,
    duration_ms: float,
    success: bool,
    tokens: int = 0
) -> None:
    """Record agent execution metrics."""
    metrics = get_metrics()
    
    metrics.histogram("agent_duration_ms", duration_ms, agent=agent, action=action)
    metrics.increment("agent_calls_total", agent=agent, action=action)
    
    if not success:
        metrics.increment("agent_errors_total", agent=agent, action=action)
    
    if tokens > 0:
        metrics.histogram("agent_tokens", tokens, agent=agent)


def record_quality_score(section: str, score: int, iteration: int) -> None:
    """Record quality score metrics."""
    metrics = get_metrics()
    
    metrics.gauge("section_score", score, section=section)
    metrics.gauge("section_iteration", iteration, section=section)
    metrics.histogram("quality_scores", score, section=section)


def record_rag_query(duration_ms: float, results_count: int) -> None:
    """Record RAG query metrics."""
    metrics = get_metrics()
    
    metrics.histogram("rag_query_duration_ms", duration_ms)
    metrics.histogram("rag_results_count", results_count)
    metrics.increment("rag_queries_total")
