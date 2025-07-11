"""
Unit tests for mlProject.utils.common module
"""

import os
import pytest
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from box import ConfigBox

from mlProject.utils.common import (
    read_yaml,
    create_directories,
    save_json,
    load_json,
    save_bin,
    load_bin,
    get_size
)


class TestReadYaml:
    """Test cases for read_yaml function"""
    
    @pytest.mark.unit
    def test_read_yaml_success(self, sample_yaml_file):
        """Test successful YAML file reading"""
        result = read_yaml(sample_yaml_file)
        
        assert isinstance(result, ConfigBox)
        assert result.test_key == "test_value"
        assert result.nested.key1 == "value1"
        assert result.list_key == ["item1", "item2"]
    
    @pytest.mark.unit
    def test_read_yaml_empty_file(self, temp_dir):
        """Test reading empty YAML file"""
        empty_yaml = temp_dir / "empty.yaml"
        empty_yaml.touch()
        
        with pytest.raises(ValueError, match="yaml file is empty"):
            read_yaml(empty_yaml)
    
    @pytest.mark.unit
    def test_read_yaml_invalid_file(self, temp_dir):
        """Test reading invalid YAML file"""
        invalid_yaml = temp_dir / "invalid.yaml"
        with open(invalid_yaml, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(Exception):
            read_yaml(invalid_yaml)
    
    @pytest.mark.unit
    def test_read_yaml_nonexistent_file(self, temp_dir):
        """Test reading non-existent YAML file"""
        nonexistent = temp_dir / "nonexistent.yaml"
        
        with pytest.raises(Exception):
            read_yaml(nonexistent)


class TestCreateDirectories:
    """Test cases for create_directories function"""
    
    @pytest.mark.unit
    def test_create_single_directory(self, temp_dir):
        """Test creating a single directory"""
        new_dir = temp_dir / "new_directory"
        
        create_directories([str(new_dir)])
        
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    @pytest.mark.unit
    def test_create_multiple_directories(self, temp_dir):
        """Test creating multiple directories"""
        dirs = [
            temp_dir / "dir1",
            temp_dir / "dir2",
            temp_dir / "dir3"
        ]
        
        create_directories([str(d) for d in dirs])
        
        for dir_path in dirs:
            assert dir_path.exists()
            assert dir_path.is_dir()
    
    @pytest.mark.unit
    def test_create_nested_directories(self, temp_dir):
        """Test creating nested directories"""
        nested_dir = temp_dir / "parent" / "child" / "grandchild"
        
        create_directories([str(nested_dir)])
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()
    
    @pytest.mark.unit
    def test_create_existing_directory(self, temp_dir):
        """Test creating directory that already exists"""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()
        
        # Should not raise an error
        create_directories([str(existing_dir)])
        
        assert existing_dir.exists()
        assert existing_dir.is_dir()
    
    @pytest.mark.unit
    def test_create_directories_verbose_false(self, temp_dir, mock_logger):
        """Test creating directories with verbose=False"""
        new_dir = temp_dir / "new_directory"
        
        create_directories([str(new_dir)], verbose=False)
        
        assert new_dir.exists()
        # Logger should not be called with verbose=False
        assert not mock_logger.info.called


class TestSaveJson:
    """Test cases for save_json function"""
    
    @pytest.mark.unit
    def test_save_json_success(self, temp_dir):
        """Test successful JSON saving"""
        test_data = {"key": "value", "number": 123, "list": [1, 2, 3]}
        json_path = temp_dir / "test.json"
        
        save_json(json_path, test_data)
        
        assert json_path.exists()
        with open(json_path) as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    @pytest.mark.unit
    def test_save_json_nested_data(self, temp_dir):
        """Test saving nested JSON data"""
        test_data = {
            "nested": {
                "key1": "value1",
                "key2": {"deep": "value"}
            },
            "list": [{"item": 1}, {"item": 2}]
        }
        json_path = temp_dir / "nested.json"
        
        save_json(json_path, test_data)
        
        assert json_path.exists()
        with open(json_path) as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    @pytest.mark.unit
    def test_save_json_empty_data(self, temp_dir):
        """Test saving empty JSON data"""
        test_data = {}
        json_path = temp_dir / "empty.json"
        
        save_json(json_path, test_data)
        
        assert json_path.exists()
        with open(json_path) as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data


class TestLoadJson:
    """Test cases for load_json function"""
    
    @pytest.mark.unit
    def test_load_json_success(self, sample_json_file):
        """Test successful JSON loading"""
        result = load_json(sample_json_file)
        
        assert isinstance(result, ConfigBox)
        assert result.test_key == "test_value"
        assert result.nested.key1 == "value1"
        assert result.list_key == ["item1", "item2"]
    
    @pytest.mark.unit
    def test_load_json_nonexistent_file(self, temp_dir):
        """Test loading non-existent JSON file"""
        nonexistent = temp_dir / "nonexistent.json"
        
        with pytest.raises(Exception):
            load_json(nonexistent)
    
    @pytest.mark.unit
    def test_load_json_invalid_json(self, temp_dir):
        """Test loading invalid JSON file"""
        invalid_json = temp_dir / "invalid.json"
        with open(invalid_json, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(Exception):
            load_json(invalid_json)


class TestSaveBin:
    """Test cases for save_bin function"""
    
    @pytest.mark.unit
    def test_save_bin_success(self, temp_dir, mock_joblib):
        """Test successful binary saving"""
        test_data = {"key": "value"}
        bin_path = temp_dir / "test.joblib"
        
        save_bin(test_data, bin_path)
        
        mock_joblib["dump"].assert_called_once_with(value=test_data, filename=bin_path)
    
    @pytest.mark.unit
    def test_save_bin_different_data_types(self, temp_dir, mock_joblib):
        """Test saving different data types"""
        test_cases = [
            [1, 2, 3, 4, 5],
            {"model": "test"},
            "string_data",
            123.456
        ]
        
        for i, data in enumerate(test_cases):
            bin_path = temp_dir / f"test_{i}.joblib"
            save_bin(data, bin_path)
            
            mock_joblib["dump"].assert_called_with(value=data, filename=bin_path)


class TestLoadBin:
    """Test cases for load_bin function"""
    
    @pytest.mark.unit
    def test_load_bin_success(self, temp_dir, mock_joblib):
        """Test successful binary loading"""
        bin_path = temp_dir / "test.joblib"
        mock_joblib["load"].return_value = {"key": "value"}
        
        result = load_bin(bin_path)
        
        mock_joblib["load"].assert_called_once_with(bin_path)
        assert result == {"key": "value"}
    
    @pytest.mark.unit
    def test_load_bin_nonexistent_file(self, temp_dir, mock_joblib):
        """Test loading non-existent binary file"""
        nonexistent = temp_dir / "nonexistent.joblib"
        mock_joblib["load"].side_effect = FileNotFoundError()
        
        with pytest.raises(FileNotFoundError):
            load_bin(nonexistent)


class TestGetSize:
    """Test cases for get_size function"""
    
    @pytest.mark.unit
    def test_get_size_existing_file(self, temp_dir):
        """Test getting size of existing file"""
        test_file = temp_dir / "test.txt"
        test_content = "A" * 2048  # 2KB content
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        size = get_size(test_file)
        
        assert "~ 2 KB" in size
        assert isinstance(size, str)
    
    @pytest.mark.unit
    def test_get_size_empty_file(self, temp_dir):
        """Test getting size of empty file"""
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()
        
        size = get_size(empty_file)
        
        assert "~ 0 KB" in size
    
    @pytest.mark.unit
    def test_get_size_large_file(self, temp_dir):
        """Test getting size of large file"""
        large_file = temp_dir / "large.txt"
        large_content = "A" * 10240  # 10KB content
        
        with open(large_file, 'w') as f:
            f.write(large_content)
        
        size = get_size(large_file)
        
        assert "~ 10 KB" in size
    
    @pytest.mark.unit
    def test_get_size_nonexistent_file(self, temp_dir):
        """Test getting size of non-existent file"""
        nonexistent = temp_dir / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            get_size(nonexistent)


class TestIntegration:
    """Integration tests for utility functions"""
    
    @pytest.mark.integration
    def test_yaml_to_json_conversion(self, temp_dir):
        """Test converting YAML to JSON using utility functions"""
        # Create YAML file
        yaml_data = {
            "config": {
                "model": "ElasticNet",
                "params": {"alpha": 0.1, "l1_ratio": 0.5}
            }
        }
        yaml_path = temp_dir / "config.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
        
        # Load YAML and save as JSON
        loaded_data = read_yaml(yaml_path)
        json_path = temp_dir / "config.json"
        save_json(json_path, dict(loaded_data))
        
        # Verify JSON file
        loaded_json = load_json(json_path)
        assert loaded_json.config.model == "ElasticNet"
        assert loaded_json.config.params.alpha == 0.1
    
    @pytest.mark.integration
    def test_directory_creation_and_file_operations(self, temp_dir):
        """Test creating directories and performing file operations"""
        # Create directory structure
        dirs = [
            temp_dir / "data",
            temp_dir / "models",
            temp_dir / "outputs"
        ]
        create_directories([str(d) for d in dirs])
        
        # Save files in each directory
        for i, dir_path in enumerate(dirs):
            json_path = dir_path / f"config_{i}.json"
            save_json(json_path, {"index": i, "directory": str(dir_path)})
            
            # Verify file exists and has correct content
            assert json_path.exists()
            loaded = load_json(json_path)
            assert loaded.index == i
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_large_file_operations(self, temp_dir):
        """Test operations with large files"""
        # Create large data structure
        large_data = {
            "data": list(range(10000)),
            "metadata": {f"key_{i}": f"value_{i}" for i in range(1000)}
        }
        
        # Save and load large JSON
        json_path = temp_dir / "large.json"
        save_json(json_path, large_data)
        loaded_data = load_json(json_path)
        
        assert len(loaded_data.data) == 10000
        assert len(loaded_data.metadata) == 1000
        assert loaded_data.data[9999] == 9999
        
        # Check file size
        size = get_size(json_path)
        assert "KB" in size


# Performance tests
class TestPerformance:
    """Performance tests for utility functions"""
    
    @pytest.mark.slow
    def test_yaml_loading_performance(self, temp_dir, performance_threshold):
        """Test YAML loading performance"""
        import time
        
        # Create moderately large YAML file
        yaml_data = {
            "config": {f"param_{i}": f"value_{i}" for i in range(1000)}
        }
        yaml_path = temp_dir / "large_config.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
        
        # Test loading performance
        start_time = time.time()
        result = read_yaml(yaml_path)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < performance_threshold["max_execution_time"]
        assert len(result.config) == 1000
    
    @pytest.mark.slow
    def test_directory_creation_performance(self, temp_dir, performance_threshold):
        """Test directory creation performance"""
        import time
        
        # Create many directories
        dirs = [temp_dir / f"dir_{i}" for i in range(100)]
        
        start_time = time.time()
        create_directories([str(d) for d in dirs])
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < performance_threshold["max_execution_time"]
        
        # Verify all directories were created
        for dir_path in dirs:
            assert dir_path.exists()
            assert dir_path.is_dir()