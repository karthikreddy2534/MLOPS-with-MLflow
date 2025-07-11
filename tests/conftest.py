"""
Pytest configuration and fixtures for MLProject tests
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from box import ConfigBox

# Add src to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the telemetry imports that might fail
try:
    from mlProject.telemetry import get_logger, setup_telemetry, MetricsCollector
except ImportError:
    # Create mock objects if telemetry imports fail
    get_logger = MagicMock()
    setup_telemetry = MagicMock()
    MetricsCollector = MagicMock()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    config = {
        "artifacts_root": "artifacts",
        "data_ingestion": {
            "root_dir": "artifacts/data_ingestion",
            "source_URL": "https://example.com/data.zip",
            "local_data_file": "artifacts/data_ingestion/data.zip",
            "unzip_dir": "artifacts/data_ingestion/"
        },
        "data_validation": {
            "root_dir": "artifacts/data_validation",
            "STATUS_FILE": "artifacts/data_validation/status.txt",
            "unzip_data_dir": "artifacts/data_ingestion/winequality-red.csv"
        },
        "data_transformation": {
            "root_dir": "artifacts/data_transformation",
            "data_path": "artifacts/data_ingestion/winequality-red.csv"
        },
        "model_trainer": {
            "root_dir": "artifacts/model_trainer",
            "train_data_path": "artifacts/data_transformation/train.csv",
            "test_data_path": "artifacts/data_transformation/test.csv",
            "model_name": "model.joblib"
        },
        "model_evaluation": {
            "root_dir": "artifacts/model_evaluation",
            "test_data_path": "artifacts/data_transformation/test.csv",
            "model_path": "artifacts/model_trainer/model.joblib",
            "metric_file_name": "artifacts/model_evaluation/metrics.json"
        }
    }
    return ConfigBox(config)


@pytest.fixture
def sample_params():
    """Sample parameters for testing"""
    params = {
        "ElasticNet": {
            "alpha": 0.1,
            "l1_ratio": 0.5
        }
    }
    return ConfigBox(params)


@pytest.fixture
def sample_schema():
    """Sample schema for testing"""
    schema = {
        "COLUMNS": {
            "fixed acidity": "float64",
            "volatile acidity": "float64",
            "citric acid": "float64",
            "residual sugar": "float64",
            "chlorides": "float64",
            "free sulfur dioxide": "float64",
            "total sulfur dioxide": "float64",
            "density": "float64",
            "pH": "float64",
            "sulphates": "float64",
            "alcohol": "float64",
            "quality": "int64"
        },
        "TARGET_COLUMN": {
            "name": "quality"
        }
    }
    return ConfigBox(schema)


@pytest.fixture
def sample_data():
    """Sample wine quality data for testing"""
    np.random.seed(42)
    data = {
        "fixed acidity": np.random.uniform(6.0, 12.0, 100),
        "volatile acidity": np.random.uniform(0.2, 1.0, 100),
        "citric acid": np.random.uniform(0.0, 0.8, 100),
        "residual sugar": np.random.uniform(1.0, 8.0, 100),
        "chlorides": np.random.uniform(0.02, 0.15, 100),
        "free sulfur dioxide": np.random.uniform(5.0, 40.0, 100),
        "total sulfur dioxide": np.random.uniform(20.0, 150.0, 100),
        "density": np.random.uniform(0.995, 1.0, 100),
        "pH": np.random.uniform(3.0, 4.0, 100),
        "sulphates": np.random.uniform(0.4, 1.2, 100),
        "alcohol": np.random.uniform(9.0, 14.0, 100),
        "quality": np.random.randint(3, 9, 100)
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_file(temp_dir, sample_data):
    """Create a sample CSV file for testing"""
    csv_path = temp_dir / "test_data.csv"
    sample_data.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_yaml_file(temp_dir):
    """Create a sample YAML file for testing"""
    yaml_content = """
test_key: test_value
nested:
  key1: value1
  key2: value2
list_key:
  - item1
  - item2
"""
    yaml_path = temp_dir / "test_config.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    return yaml_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing"""
    json_content = {
        "test_key": "test_value",
        "nested": {
            "key1": "value1",
            "key2": "value2"
        },
        "list_key": ["item1", "item2"]
    }
    json_path = temp_dir / "test_data.json"
    
    import json
    with open(json_path, 'w') as f:
        json.dump(json_content, f)
    
    return json_path


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('mlProject.logger') as mock_log:
        yield mock_log


@pytest.fixture
def mock_mlflow():
    """Mock MLflow for testing"""
    with patch('mlflow.start_run'), \
         patch('mlflow.log_params'), \
         patch('mlflow.log_metric'), \
         patch('mlflow.sklearn.log_model'), \
         patch('mlflow.set_registry_uri'), \
         patch('mlflow.get_tracking_uri'):
        yield


@pytest.fixture
def mock_download():
    """Mock file download for testing"""
    with patch('urllib.request.urlretrieve') as mock_retrieve:
        mock_retrieve.return_value = ("test_file.zip", {})
        yield mock_retrieve


@pytest.fixture
def mock_zipfile():
    """Mock zipfile for testing"""
    with patch('zipfile.ZipFile') as mock_zip:
        mock_zip.return_value.__enter__.return_value.extractall = MagicMock()
        yield mock_zip


@pytest.fixture
def mock_joblib():
    """Mock joblib for testing"""
    with patch('joblib.dump') as mock_dump, \
         patch('joblib.load') as mock_load:
        mock_load.return_value = MagicMock()
        yield {"dump": mock_dump, "load": mock_load}


@pytest.fixture
def mock_sklearn_model():
    """Mock scikit-learn model for testing"""
    mock_model = MagicMock()
    mock_model.fit.return_value = mock_model
    mock_model.predict.return_value = np.array([5, 6, 7, 8, 5])
    mock_model.score.return_value = 0.85
    return mock_model


@pytest.fixture(autouse=True)
def cleanup_artifacts():
    """Cleanup artifacts directory after each test"""
    yield
    
    # Clean up any created artifacts
    if os.path.exists("artifacts"):
        shutil.rmtree("artifacts")
    
    # Clean up logs
    if os.path.exists("logs"):
        shutil.rmtree("logs")


@pytest.fixture
def mock_config_manager():
    """Mock ConfigurationManager for testing"""
    with patch('mlProject.config.configuration.ConfigurationManager') as mock_cm:
        yield mock_cm


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance threshold for testing"""
    return {
        "max_execution_time": 5.0,  # 5 seconds
        "max_memory_usage": 100,    # 100 MB
    }


# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )