"""
Distributed tracing module for MLProject
"""

import time
import uuid
import functools
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode


@dataclass
class TraceContext:
    """Trace context for storing trace information"""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: str = "success"
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: list = field(default_factory=list)
    
    def finish(self, status: str = "success", error: Optional[Exception] = None):
        """Finish the trace context"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        
        if error:
            self.status = "error"
            self.tags["error"] = str(error)
            self.tags["error_type"] = type(error).__name__
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the trace context"""
        self.tags[key] = value
    
    def log(self, message: str, level: str = "info", **kwargs):
        """Add a log entry to the trace context"""
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace context to dictionary"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status,
            "tags": self.tags,
            "logs": self.logs,
        }


class TracingManager:
    """Manage distributed tracing"""
    
    def __init__(self):
        self.active_traces: Dict[str, TraceContext] = {}
        self.completed_traces: list = []
    
    def create_trace(self, operation_name: str, parent_span_id: Optional[str] = None) -> TraceContext:
        """Create a new trace context"""
        trace_context = TraceContext(
            operation_name=operation_name,
            parent_span_id=parent_span_id
        )
        self.active_traces[trace_context.span_id] = trace_context
        return trace_context
    
    def finish_trace(self, span_id: str, status: str = "success", error: Optional[Exception] = None):
        """Finish a trace"""
        if span_id in self.active_traces:
            trace_context = self.active_traces.pop(span_id)
            trace_context.finish(status, error)
            self.completed_traces.append(trace_context)
            return trace_context
        return None
    
    def get_trace(self, span_id: str) -> Optional[TraceContext]:
        """Get an active trace context"""
        return self.active_traces.get(span_id)
    
    def get_completed_traces(self) -> list:
        """Get all completed traces"""
        return self.completed_traces
    
    def clear_traces(self):
        """Clear all traces"""
        self.active_traces.clear()
        self.completed_traces.clear()


# Global tracing manager
tracing_manager = TracingManager()


@contextmanager
def create_span(operation_name: str, parent_span_id: Optional[str] = None, **tags):
    """Context manager for creating spans"""
    trace_context = tracing_manager.create_trace(operation_name, parent_span_id)
    
    # Add initial tags
    for key, value in tags.items():
        trace_context.add_tag(key, value)
    
    try:
        yield trace_context
        tracing_manager.finish_trace(trace_context.span_id, "success")
    except Exception as e:
        tracing_manager.finish_trace(trace_context.span_id, "error", e)
        raise


def trace_function(operation_name: Optional[str] = None, **default_tags):
    """Decorator to trace function execution"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with create_span(op_name, **default_tags) as span:
                # Add function metadata
                span.add_tag("function", func.__name__)
                span.add_tag("module", func.__module__)
                span.add_tag("args_count", len(args))
                span.add_tag("kwargs_count", len(kwargs))
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Add result metadata if it's a simple type
                if isinstance(result, (int, float, str, bool)):
                    span.add_tag("result", result)
                elif hasattr(result, '__len__'):
                    span.add_tag("result_length", len(result))
                
                return result
        
        return wrapper
    return decorator


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID from OpenTelemetry"""
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            return format(current_span.get_span_context().trace_id, '032x')
    except Exception:
        pass
    return None


def add_trace_tags(**tags):
    """Add tags to the current OpenTelemetry span"""
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            for key, value in tags.items():
                current_span.set_attribute(key, str(value))
    except Exception:
        pass


def log_to_trace(message: str, level: str = "info", **kwargs):
    """Log message to current trace"""
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            current_span.add_event(message, kwargs)
    except Exception:
        pass


def create_child_span(operation_name: str, parent_span: Optional[Span] = None):
    """Create a child span using OpenTelemetry"""
    try:
        tracer = trace.get_tracer(__name__)
        
        if parent_span:
            with trace.use_span(parent_span):
                return tracer.start_span(operation_name)
        else:
            return tracer.start_span(operation_name)
    except Exception:
        return None


def finish_span_with_error(span: Span, error: Exception):
    """Finish a span with error information"""
    try:
        if span:
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(error).__name__)
            span.set_attribute("error.message", str(error))
            span.end()
    except Exception:
        pass


def get_trace_summary() -> Dict[str, Any]:
    """Get a summary of all traces"""
    completed_traces = tracing_manager.get_completed_traces()
    
    if not completed_traces:
        return {"total_traces": 0}
    
    total_duration = sum(t.duration or 0 for t in completed_traces)
    success_count = sum(1 for t in completed_traces if t.status == "success")
    error_count = sum(1 for t in completed_traces if t.status == "error")
    
    return {
        "total_traces": len(completed_traces),
        "total_duration": total_duration,
        "average_duration": total_duration / len(completed_traces) if completed_traces else 0,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": success_count / len(completed_traces) if completed_traces else 0,
    }