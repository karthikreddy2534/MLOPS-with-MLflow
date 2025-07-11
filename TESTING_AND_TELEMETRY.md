# MLProject Testing and Telemetry Guide

This guide explains how to use the comprehensive testing and telemetry features added to your MLOPS-with-MLflow project.

## 🚀 Quick Start

### Install Dependencies and Run Tests

```bash
# Install testing and telemetry dependencies
python run_tests.py --install-deps

# Run all tests with telemetry
python run_tests.py --verbose

# Run specific test types
python run_tests.py --test-type unit --verbose
python run_tests.py --test-type integration --verbose
python run_tests.py --test-type slow --verbose
```

### Demonstrate Telemetry Features

```bash
# See telemetry in action
python run_tests.py --demo-telemetry --skip-tests
```

## 📊 Testing Framework

### Test Types

We've implemented comprehensive testing with different test markers:

- **Unit Tests** (`@pytest.mark.unit`): Fast tests for individual functions
- **Integration Tests** (`@pytest.mark.integration`): Tests for component interactions
- **Slow Tests** (`@pytest.mark.slow`): Performance and large-scale tests
- **Smoke Tests** (`@pytest.mark.smoke`): Basic functionality tests

### Test Coverage

The testing framework includes:

#### 1. **Utility Functions** (`tests/unit/test_utils_common.py`)
- ✅ YAML file reading/writing
- ✅ JSON file operations
- ✅ Directory creation
- ✅ Binary file serialization
- ✅ File size calculations
- ✅ Error handling scenarios
- ✅ Performance benchmarks

#### 2. **Data Ingestion** (`tests/unit/test_data_ingestion.py`)
- ✅ File downloading with mocking
- ✅ ZIP file extraction
- ✅ Configuration validation
- ✅ Error handling scenarios
- ✅ Performance testing
- ✅ Concurrent access handling

#### 3. **Data Pipeline Components** (Can be extended)
- Data validation testing
- Data transformation testing
- Model training testing
- Model evaluation testing
- Pipeline integration testing

### Test Configuration

The testing is configured through:

- **`pytest.ini`**: Main pytest configuration
- **`tests/conftest.py`**: Test fixtures and setup
- **Coverage threshold**: 80% minimum coverage
- **HTML reports**: Generated in `tests/reports/`

## 🔍 Telemetry System

### Features Overview

Our telemetry system provides:

1. **Structured Logging**: JSON-formatted logs with metadata
2. **Performance Metrics**: Function execution time and memory usage
3. **ML Pipeline Metrics**: Model accuracy, training time, data sizes
4. **Error Tracking**: Detailed error logging and categorization
5. **Distributed Tracing**: Request/operation tracing across components
6. **Prometheus Integration**: Metrics export for monitoring

### Telemetry Components

#### 1. **Enhanced Logging** (`src/mlProject/telemetry/logger.py`)

```python
from mlProject.telemetry import get_logger

logger = get_logger("my_component")

# Structured logging with context
logger.info("Processing data", 
           stage="data_ingestion",
           records_count=1000,
           user_id="user123")

# Pipeline stage logging with metrics
logger.log_pipeline_stage("data_validation", "success", duration=2.5)

# Model metrics logging
logger.log_model_metrics(accuracy=0.95, training_time=120.5)
```

#### 2. **Performance Tracking** (`src/mlProject/telemetry/metrics.py`)

```python
from mlProject.telemetry import track_performance, MetricsCollector

# Decorator for automatic performance tracking
@track_performance("data_processing")
def process_data(data):
    # Your processing logic
    return processed_data

# Context manager for tracking operations
from mlProject.telemetry.metrics import track_operation

with track_operation("model_training") as tracker:
    # Your model training code
    tracker.add_tag("model_type", "ElasticNet")
    tracker.add_tag("dataset_size", 1000)
```

#### 3. **Distributed Tracing** (`src/mlProject/telemetry/tracer.py`)

```python
from mlProject.telemetry import create_span, trace_function

# Context manager for spans
with create_span("data_pipeline", model="ElasticNet") as span:
    span.add_tag("batch_size", 32)
    span.log("Processing started")
    # Your processing logic
    span.log("Processing completed")

# Function decorator
@trace_function("model_prediction")
def predict(model, data):
    return model.predict(data)
```

### Telemetry Integration Examples

#### Example 1: Enhanced Data Ingestion

```python
from mlProject.telemetry import get_logger, track_performance, create_span

class DataIngestion:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("data_ingestion")
    
    @track_performance("download_file")
    def download_file(self):
        with create_span("file_download", url=self.config.source_URL) as span:
            try:
                # Download logic
                self.logger.info("File downloaded successfully", 
                               file_size=file_size,
                               download_time=duration)
                span.add_tag("success", True)
            except Exception as e:
                self.logger.error("Download failed", error=str(e))
                span.add_tag("success", False)
                raise
```

#### Example 2: ML Pipeline with Telemetry

```python
from mlProject.telemetry import get_logger, track_ml_metrics

class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("model_trainer")
    
    def train(self):
        start_time = time.time()
        
        # Training logic
        model = ElasticNet(alpha=self.config.alpha, l1_ratio=self.config.l1_ratio)
        model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        
        # Evaluate model
        accuracy = model.score(X_test, y_test)
        
        # Track ML metrics
        track_ml_metrics("model_training",
                        accuracy=accuracy,
                        training_time=training_time,
                        training_samples=len(X_train),
                        alpha=self.config.alpha,
                        l1_ratio=self.config.l1_ratio)
        
        self.logger.log_model_metrics(accuracy=accuracy, training_time=training_time)
```

## 📈 Monitoring and Observability

### Metrics Dashboard

Once telemetry is running, you can access metrics at:
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **Structured Logs**: `logs/telemetry.json`
- **Test Reports**: `tests/reports/`

### Available Metrics

#### System Metrics
- `mlproject_memory_usage_bytes`: Memory usage in bytes
- `mlproject_cpu_usage_percent`: CPU usage percentage
- `mlproject_function_calls_total`: Total function calls
- `mlproject_function_duration_seconds`: Function execution time

#### ML Pipeline Metrics
- `mlproject_pipeline_stage_duration_seconds`: Pipeline stage duration
- `mlproject_pipeline_stage_status_total`: Pipeline stage status counts
- `mlproject_model_accuracy`: Model accuracy score
- `mlproject_model_training_duration_seconds`: Model training time
- `mlproject_data_ingestion_size_bytes`: Data ingestion size

### Log Structure

Structured logs include:
```json
{
  "timestamp": "2024-01-11T10:30:45.123456",
  "level": "INFO",
  "logger": "mlProject.components.data_ingestion",
  "module": "data_ingestion",
  "function": "download_file",
  "line": 45,
  "message": "File downloaded successfully",
  "process_id": 12345,
  "thread_id": 67890,
  "file_size": 1024000,
  "download_time": 2.5,
  "system_metrics": {
    "memory_mb": 150.5,
    "cpu_percent": 25.3,
    "memory_percent": 15.2
  }
}
```

## 🛠️ Usage Examples

### Running Tests

```bash
# Install dependencies
python run_tests.py --install-deps

# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --test-type unit
python run_tests.py --test-type integration
python run_tests.py --test-type slow

# Run with verbose output
python run_tests.py --verbose

# Demo telemetry without running tests
python run_tests.py --demo-telemetry --skip-tests
```

### Using in Your ML Pipeline

```python
# In your main.py or pipeline files
from mlProject.telemetry import get_logger, setup_telemetry

# Setup telemetry at application start
setup_telemetry(metrics_port=8000)

# Use in your components
logger = get_logger("main_pipeline")

try:
    logger.info("Starting ML pipeline", version="1.0.0")
    
    # Your pipeline stages with telemetry
    data_ingestion = DataIngestionTrainingPipeline()
    data_ingestion.main()
    
    logger.info("Pipeline completed successfully")
    
except Exception as e:
    logger.exception("Pipeline failed", stage="unknown")
    raise
```

### Testing Your Components

```python
# In your test files
import pytest
from mlProject.telemetry import get_logger

@pytest.mark.unit
def test_data_processing():
    """Test data processing with telemetry"""
    logger = get_logger("test")
    
    # Your test logic
    result = process_data(test_data)
    
    # Log test results
    logger.info("Test completed", 
               test_name="test_data_processing",
               result_size=len(result))
    
    assert result is not None
```

## 🔧 Configuration

### Test Configuration (`pytest.ini`)

```ini
[tool:pytest]
addopts = 
    --cov=src/mlProject
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --html=tests/reports/report.html
    -v
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    smoke: Smoke tests
```

### Telemetry Configuration

```python
# Custom telemetry setup
from mlProject.telemetry import setup_telemetry

setup_telemetry(
    metrics_port=8000,  # Prometheus metrics port
    log_level="INFO",   # Logging level
    enable_tracing=True # Enable distributed tracing
)
```

## 📋 Best Practices

### Testing
1. **Use appropriate test markers** for different test types
2. **Mock external dependencies** (network calls, file system)
3. **Test error scenarios** and edge cases
4. **Maintain high test coverage** (>80%)
5. **Use fixtures** for test data and configuration

### Telemetry
1. **Add context to logs** with relevant metadata
2. **Track performance** of critical operations
3. **Monitor ML-specific metrics** (accuracy, training time)
4. **Use structured logging** for better searchability
5. **Handle telemetry failures gracefully**

## 🚀 Next Steps

1. **Extend Test Coverage**: Add more test files for other components
2. **Custom Metrics**: Add domain-specific metrics for your use case
3. **Alerting**: Set up alerts based on telemetry metrics
4. **Dashboards**: Create Grafana dashboards for visualization
5. **CI/CD Integration**: Integrate tests into your CI/CD pipeline

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Run `python run_tests.py --install-deps` first
2. **Port Conflicts**: Change metrics port in telemetry setup
3. **Permission Errors**: Ensure write permissions for logs and reports
4. **Memory Issues**: Adjust performance thresholds in tests

### Debug Commands

```bash
# Check if dependencies are installed
python -c "import pytest, prometheus_client, psutil; print('All dependencies OK')"

# Run single test file
python -m pytest tests/unit/test_utils_common.py -v

# Generate coverage report only
python -m pytest --cov=src/mlProject --cov-report=html

# Check telemetry setup
python -c "from mlProject.telemetry import setup_telemetry; setup_telemetry()"
```

## 📝 Summary

You now have a comprehensive testing and telemetry system that provides:

✅ **Comprehensive Test Suite** with multiple test types and high coverage
✅ **Structured Logging** with JSON format and metadata
✅ **Performance Monitoring** with execution time and memory tracking
✅ **ML Pipeline Metrics** for model performance and training statistics
✅ **Distributed Tracing** for request/operation tracking
✅ **Prometheus Integration** for metrics export and monitoring
✅ **Automated Test Runner** with reporting and telemetry integration
✅ **Error Tracking** with detailed error logging and categorization

This system will help you maintain high code quality, monitor your ML pipeline performance, and quickly identify issues in production.

Happy testing and monitoring! 🎉