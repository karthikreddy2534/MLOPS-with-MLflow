"""
Enhanced logging system with structured logging and telemetry
"""

import os
import sys
import json
import logging
import structlog
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricsExporter
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil


# Prometheus metrics
REQUEST_COUNT = Counter('mlproject_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('mlproject_request_duration_seconds', 'Request latency')
MEMORY_USAGE = Gauge('mlproject_memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('mlproject_cpu_usage_percent', 'CPU usage percentage')

# ML Pipeline specific metrics
PIPELINE_STAGE_DURATION = Histogram('mlproject_pipeline_stage_duration_seconds', 'Pipeline stage duration', ['stage'])
PIPELINE_STAGE_STATUS = Counter('mlproject_pipeline_stage_status_total', 'Pipeline stage status', ['stage', 'status'])
MODEL_ACCURACY = Gauge('mlproject_model_accuracy', 'Model accuracy score')
MODEL_TRAINING_TIME = Histogram('mlproject_model_training_duration_seconds', 'Model training time')


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'process_id': os.getpid(),
            'thread_id': record.thread,
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'extra_fields'):
            log_entry.update(getattr(record, 'extra_fields', {}))
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add system metrics
        log_entry['system_metrics'] = self._get_system_metrics()
        
        return json.dumps(log_entry)
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            process = psutil.Process()
            return {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
            }
        except Exception:
            return {}


class TelemetryLogger:
    """Enhanced logger with telemetry capabilities"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_structured_logging()
        
    def _setup_structured_logging(self):
        """Setup structured logging with JSON format"""
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Setup JSON formatter
        json_formatter = JSONFormatter()
        
        # File handler for JSON logs
        json_handler = logging.FileHandler(log_dir / "telemetry.json")
        json_handler.setFormatter(json_formatter)
        json_handler.setLevel(logging.INFO)
        
        # Console handler for readable logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Add handlers to logger
        self.logger.addHandler(json_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        self._log_with_extra(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        self._log_with_extra(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        self._log_with_extra(logging.ERROR, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with extra fields"""
        self._log_with_extra(logging.ERROR, message, exc_info=True, **kwargs)
    
    def _log_with_extra(self, level: int, message: str, **kwargs):
        """Log message with extra fields"""
        # Update system metrics
        self._update_system_metrics()
        
        # Create log record with extra fields
        extra_fields = {k: v for k, v in kwargs.items() if k != 'exc_info'}
        
        # Create a custom LogRecord
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), kwargs.get('exc_info', None)
        )
        record.extra_fields = extra_fields
        
        # Handle the record
        self.logger.handle(record)
    
    def _update_system_metrics(self):
        """Update Prometheus system metrics"""
        try:
            process = psutil.Process()
            MEMORY_USAGE.set(process.memory_info().rss)
            CPU_USAGE.set(process.cpu_percent())
        except Exception:
            pass
    
    def log_pipeline_stage(self, stage: str, status: str, duration: Optional[float] = None, **kwargs):
        """Log pipeline stage with metrics"""
        PIPELINE_STAGE_STATUS.labels(stage=stage, status=status).inc()
        
        if duration is not None:
            PIPELINE_STAGE_DURATION.labels(stage=stage).observe(duration)
        
        self.info(
            f"Pipeline stage: {stage}",
            stage=stage,
            status=status,
            duration=duration,
            **kwargs
        )
    
    def log_model_metrics(self, accuracy: float, training_time: float, **kwargs):
        """Log model training metrics"""
        MODEL_ACCURACY.set(accuracy)
        MODEL_TRAINING_TIME.observe(training_time)
        
        self.info(
            "Model training completed",
            accuracy=accuracy,
            training_time=training_time,
            **kwargs
        )


def setup_telemetry(metrics_port: int = 8000):
    """Setup telemetry infrastructure"""
    
    # Setup OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    
    # Start Prometheus metrics server
    try:
        start_http_server(metrics_port)
        print(f"Metrics server started on port {metrics_port}")
    except Exception as e:
        print(f"Failed to start metrics server: {e}")


def get_logger(name: str) -> TelemetryLogger:
    """Get a telemetry logger instance"""
    return TelemetryLogger(name)