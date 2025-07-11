"""
Metrics collection and performance tracking for MLProject
"""

import time
import psutil
import functools
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from prometheus_client import Counter, Histogram, Gauge, Info
from contextlib import contextmanager


# Global metrics
FUNCTION_CALLS = Counter('mlproject_function_calls_total', 'Total function calls', ['function', 'module'])
FUNCTION_DURATION = Histogram('mlproject_function_duration_seconds', 'Function duration', ['function', 'module'])
FUNCTION_ERRORS = Counter('mlproject_function_errors_total', 'Function errors', ['function', 'module', 'error_type'])

# ML specific metrics
DATA_INGESTION_SIZE = Gauge('mlproject_data_ingestion_size_bytes', 'Data ingestion size in bytes')
DATA_VALIDATION_ERRORS = Counter('mlproject_data_validation_errors_total', 'Data validation errors', ['error_type'])
MODEL_TRAINING_SAMPLES = Gauge('mlproject_model_training_samples', 'Number of training samples')
MODEL_METRICS = Gauge('mlproject_model_metrics', 'Model performance metrics', ['metric_type'])


@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_start: Optional[float] = None
    memory_end: Optional[float] = None
    memory_peak: Optional[float] = None
    cpu_percent: Optional[float] = None
    
    def __post_init__(self):
        """Initialize memory tracking"""
        try:
            process = psutil.Process()
            self.memory_start = process.memory_info().rss / 1024 / 1024  # MB
            self.cpu_percent = process.cpu_percent()
        except Exception:
            pass
    
    def finish(self):
        """Mark performance tracking as finished"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        try:
            process = psutil.Process()
            self.memory_end = process.memory_info().rss / 1024 / 1024  # MB
            self.memory_peak = max(self.memory_start or 0, self.memory_end or 0)
        except Exception:
            pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'duration': self.duration,
            'memory_start_mb': self.memory_start,
            'memory_end_mb': self.memory_end,
            'memory_peak_mb': self.memory_peak,
            'cpu_percent': self.cpu_percent,
        }


class MetricsCollector:
    """Centralized metrics collection"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
    
    def record_metric(self, name: str, value: Any, labels: Optional[Dict[str, str]] = None):
        """Record a custom metric"""
        metric_data = {
            'value': value,
            'timestamp': time.time(),
            'labels': labels or {}
        }
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(metric_data)
    
    def start_performance_tracking(self, operation_name: str) -> PerformanceMetrics:
        """Start performance tracking for an operation"""
        perf_metrics = PerformanceMetrics()
        self.performance_metrics[operation_name] = perf_metrics
        return perf_metrics
    
    def finish_performance_tracking(self, operation_name: str) -> Optional[PerformanceMetrics]:
        """Finish performance tracking for an operation"""
        if operation_name in self.performance_metrics:
            perf_metrics = self.performance_metrics[operation_name]
            perf_metrics.finish()
            return perf_metrics
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics
    
    def get_performance_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all performance metrics"""
        return {
            name: metrics.to_dict() 
            for name, metrics in self.performance_metrics.items()
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def track_performance(operation_name: Optional[str] = None):
    """Decorator to track function performance"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Start tracking
            perf_metrics = metrics_collector.start_performance_tracking(op_name)
            
            # Record function call
            FUNCTION_CALLS.labels(function=func.__name__, module=func.__module__).inc()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Finish tracking
                perf_metrics = metrics_collector.finish_performance_tracking(op_name)
                
                if perf_metrics and perf_metrics.duration:
                    FUNCTION_DURATION.labels(function=func.__name__, module=func.__module__).observe(perf_metrics.duration)
                
                return result
                
            except Exception as e:
                # Record error
                FUNCTION_ERRORS.labels(
                    function=func.__name__, 
                    module=func.__module__, 
                    error_type=type(e).__name__
                ).inc()
                
                # Finish tracking even on error
                metrics_collector.finish_performance_tracking(op_name)
                raise
        
        return wrapper
    return decorator


@contextmanager
def track_operation(operation_name: str):
    """Context manager for tracking operations"""
    perf_metrics = metrics_collector.start_performance_tracking(operation_name)
    try:
        yield perf_metrics
    finally:
        metrics_collector.finish_performance_tracking(operation_name)


def track_ml_metrics(stage: str, **kwargs):
    """Track ML-specific metrics"""
    
    # Data ingestion metrics
    if stage == "data_ingestion" and "data_size" in kwargs:
        DATA_INGESTION_SIZE.set(kwargs["data_size"])
    
    # Data validation metrics
    elif stage == "data_validation" and "validation_errors" in kwargs:
        for error_type, count in kwargs["validation_errors"].items():
            DATA_VALIDATION_ERRORS.labels(error_type=error_type).inc(count)
    
    # Model training metrics
    elif stage == "model_training":
        if "training_samples" in kwargs:
            MODEL_TRAINING_SAMPLES.set(kwargs["training_samples"])
        
        # Model performance metrics
        for metric_name, value in kwargs.items():
            if metric_name in ["accuracy", "precision", "recall", "f1_score", "rmse", "mae", "r2"]:
                MODEL_METRICS.labels(metric_type=metric_name).set(value)
    
    # Record custom metrics
    metrics_collector.record_metric(f"ml_{stage}", kwargs)


def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    try:
        process = psutil.Process()
        return {
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(),
            'open_files': len(process.open_files()),
            'num_threads': process.num_threads(),
        }
    except Exception:
        return {}


def reset_metrics():
    """Reset all collected metrics"""
    global metrics_collector
    metrics_collector = MetricsCollector()