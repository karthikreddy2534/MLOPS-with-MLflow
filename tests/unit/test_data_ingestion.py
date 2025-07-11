"""
Unit tests for mlProject.components.data_ingestion module
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from mlProject.components.data_ingestion import DataIngestion
from mlProject.entity.config_entity import DataIngestionConfig


class TestDataIngestion:
    """Test cases for DataIngestion class"""
    
    @pytest.fixture
    def data_ingestion_config(self, temp_dir):
        """Create a DataIngestionConfig for testing"""
        return DataIngestionConfig(
            root_dir=temp_dir / "data_ingestion",
            source_URL="https://example.com/data.zip",
            local_data_file=temp_dir / "data_ingestion" / "data.zip",
            unzip_dir=temp_dir / "data_ingestion" / "extracted"
        )
    
    @pytest.fixture
    def data_ingestion(self, data_ingestion_config):
        """Create a DataIngestion instance for testing"""
        return DataIngestion(config=data_ingestion_config)
    
    @pytest.mark.unit
    def test_init(self, data_ingestion_config):
        """Test DataIngestion initialization"""
        data_ingestion = DataIngestion(config=data_ingestion_config)
        
        assert data_ingestion.config == data_ingestion_config
        assert data_ingestion.config.root_dir == data_ingestion_config.root_dir
        assert data_ingestion.config.source_URL == data_ingestion_config.source_URL
    
    @pytest.mark.unit
    def test_download_file_success(self, data_ingestion, mock_download):
        """Test successful file download"""
        # Mock that file doesn't exist initially
        with patch('os.path.exists', return_value=False):
            data_ingestion.download_file()
        
        # Verify download was called
        mock_download.assert_called_once_with(
            url=data_ingestion.config.source_URL,
            filename=data_ingestion.config.local_data_file
        )
    
    @pytest.mark.unit
    def test_download_file_already_exists(self, data_ingestion, mock_download):
        """Test file download when file already exists"""
        # Mock that file already exists
        with patch('os.path.exists', return_value=True), \
             patch('mlProject.utils.common.get_size', return_value="~ 100 KB"):
            
            data_ingestion.download_file()
        
        # Verify download was not called
        mock_download.assert_not_called()
    
    @pytest.mark.unit
    def test_download_file_failure(self, data_ingestion, mock_download):
        """Test file download failure"""
        # Mock download failure
        mock_download.side_effect = Exception("Download failed")
        
        with patch('os.path.exists', return_value=False):
            with pytest.raises(Exception, match="Download failed"):
                data_ingestion.download_file()
    
    @pytest.mark.unit
    def test_extract_zip_file_success(self, data_ingestion, mock_zipfile):
        """Test successful ZIP file extraction"""
        # Mock os.makedirs and zipfile operations
        with patch('os.makedirs') as mock_makedirs:
            data_ingestion.extract_zip_file()
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with(data_ingestion.config.unzip_dir, exist_ok=True)
        
        # Verify zip file operations
        mock_zipfile.assert_called_once_with(data_ingestion.config.local_data_file, 'r')
        mock_zipfile.return_value.__enter__.return_value.extractall.assert_called_once_with(
            data_ingestion.config.unzip_dir
        )
    
    @pytest.mark.unit
    def test_extract_zip_file_invalid_zip(self, data_ingestion, mock_zipfile):
        """Test ZIP file extraction with invalid ZIP file"""
        # Mock zipfile exception
        mock_zipfile.side_effect = Exception("Invalid ZIP file")
        
        with patch('os.makedirs'):
            with pytest.raises(Exception, match="Invalid ZIP file"):
                data_ingestion.extract_zip_file()
    
    @pytest.mark.unit
    def test_extract_zip_file_permission_error(self, data_ingestion, mock_zipfile):
        """Test ZIP file extraction with permission error"""
        # Mock permission error during directory creation
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError, match="Permission denied"):
                data_ingestion.extract_zip_file()
    
    @pytest.mark.integration
    def test_full_data_ingestion_workflow(self, data_ingestion, mock_download, mock_zipfile):
        """Test complete data ingestion workflow"""
        # Mock file doesn't exist initially
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs:
            
            # Step 1: Download file
            data_ingestion.download_file()
            
            # Step 2: Extract file
            data_ingestion.extract_zip_file()
        
        # Verify both operations were called
        mock_download.assert_called_once()
        mock_zipfile.assert_called_once()
        mock_makedirs.assert_called_once()
    
    @pytest.mark.unit
    def test_config_validation(self, temp_dir):
        """Test configuration validation"""
        # Test with valid configuration
        valid_config = DataIngestionConfig(
            root_dir=temp_dir / "data_ingestion",
            source_URL="https://example.com/data.zip",
            local_data_file=temp_dir / "data.zip",
            unzip_dir=temp_dir / "extracted"
        )
        data_ingestion = DataIngestion(config=valid_config)
        assert data_ingestion.config == valid_config
    
    @pytest.mark.unit
    def test_download_with_different_urls(self, temp_dir, mock_download):
        """Test download with different URL formats"""
        test_urls = [
            "https://example.com/data.zip",
            "http://example.com/data.csv",
            "ftp://example.com/data.tar.gz"
        ]
        
        for url in test_urls:
            config = DataIngestionConfig(
                root_dir=temp_dir / "data_ingestion",
                source_URL=url,
                local_data_file=temp_dir / "data_ingestion" / "data.zip",
                unzip_dir=temp_dir / "data_ingestion" / "extracted"
            )
            
            data_ingestion = DataIngestion(config=config)
            
            with patch('os.path.exists', return_value=False):
                data_ingestion.download_file()
            
            # Verify the URL was used in the download call
            mock_download.assert_called_with(
                url=url,
                filename=config.local_data_file
            )
    
    @pytest.mark.unit
    def test_logging_behavior(self, data_ingestion, mock_download, mock_logger):
        """Test logging behavior during operations"""
        # Test download logging when file exists
        with patch('os.path.exists', return_value=True), \
             patch('mlProject.utils.common.get_size', return_value="~ 100 KB"):
            
            data_ingestion.download_file()
        
        # Verify appropriate log messages were called
        mock_logger.info.assert_called()
        
        # Test download logging when file doesn't exist
        mock_logger.reset_mock()
        with patch('os.path.exists', return_value=False):
            data_ingestion.download_file()
        
        mock_logger.info.assert_called()
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_large_file_handling(self, temp_dir, mock_download):
        """Test handling of large files"""
        # Create config for large file
        config = DataIngestionConfig(
            root_dir=temp_dir / "data_ingestion",
            source_URL="https://example.com/large_data.zip",
            local_data_file=temp_dir / "data_ingestion" / "large_data.zip",
            unzip_dir=temp_dir / "data_ingestion" / "extracted"
        )
        
        data_ingestion = DataIngestion(config=config)
        
        # Mock large file scenario
        with patch('os.path.exists', return_value=False):
            data_ingestion.download_file()
        
        mock_download.assert_called_once()
    
    @pytest.mark.unit
    def test_error_handling_during_extraction(self, data_ingestion):
        """Test error handling during ZIP extraction"""
        # Test various extraction errors
        error_scenarios = [
            ("BadZipFile", "Bad ZIP file"),
            ("OSError", "OS error"),
            ("MemoryError", "Memory error")
        ]
        
        for error_type, error_msg in error_scenarios:
            with patch('zipfile.ZipFile', side_effect=Exception(error_msg)):
                with patch('os.makedirs'):
                    with pytest.raises(Exception, match=error_msg):
                        data_ingestion.extract_zip_file()
    
    @pytest.mark.unit
    def test_concurrent_access_handling(self, data_ingestion, mock_download):
        """Test handling of concurrent access scenarios"""
        # Simulate race condition where file is created between existence check and download
        def side_effect_exists(path):
            # First call returns False, second call returns True
            side_effect_exists.call_count = getattr(side_effect_exists, 'call_count', 0) + 1
            return side_effect_exists.call_count > 1
        
        with patch('os.path.exists', side_effect=side_effect_exists):
            with patch('mlProject.utils.common.get_size', return_value="~ 100 KB"):
                data_ingestion.download_file()
        
        # Should still attempt download on first call
        mock_download.assert_called_once()


class TestDataIngestionConfig:
    """Test cases for DataIngestionConfig dataclass"""
    
    @pytest.mark.unit
    def test_config_creation(self, temp_dir):
        """Test DataIngestionConfig creation"""
        config = DataIngestionConfig(
            root_dir=temp_dir / "data_ingestion",
            source_URL="https://example.com/data.zip",
            local_data_file=temp_dir / "data_ingestion" / "data.zip",
            unzip_dir=temp_dir / "data_ingestion" / "extracted"
        )
        
        assert config.root_dir == temp_dir / "data_ingestion"
        assert config.source_URL == "https://example.com/data.zip"
        assert config.local_data_file == temp_dir / "data_ingestion" / "data.zip"
        assert config.unzip_dir == temp_dir / "data_ingestion" / "extracted"
    
    @pytest.mark.unit
    def test_config_immutability(self, temp_dir):
        """Test that DataIngestionConfig is immutable (frozen)"""
        config = DataIngestionConfig(
            root_dir=temp_dir / "data_ingestion",
            source_URL="https://example.com/data.zip",
            local_data_file=temp_dir / "data_ingestion" / "data.zip",
            unzip_dir=temp_dir / "data_ingestion" / "extracted"
        )
        
        # Should not be able to modify frozen dataclass
        with pytest.raises((AttributeError, TypeError)):
            setattr(config, 'root_dir', temp_dir / "other_dir")
    
    @pytest.mark.unit
    def test_config_path_handling(self, temp_dir):
        """Test path handling in configuration"""
        # Test with Path objects
        config = DataIngestionConfig(
            root_dir=Path(temp_dir) / "data_ingestion",
            source_URL="https://example.com/data.zip",
            local_data_file=Path(temp_dir) / "data_ingestion" / "data.zip",
            unzip_dir=Path(temp_dir) / "data_ingestion" / "extracted"
        )
        
        assert isinstance(config.root_dir, Path)
        assert isinstance(config.local_data_file, Path)
        assert isinstance(config.unzip_dir, Path)
        
        # Test with string paths converted to Path objects
        config_str = DataIngestionConfig(
            root_dir=Path(str(temp_dir / "data_ingestion")),
            source_URL="https://example.com/data.zip",
            local_data_file=Path(str(temp_dir / "data_ingestion" / "data.zip")),
            unzip_dir=Path(str(temp_dir / "data_ingestion" / "extracted"))
        )
        
        assert config_str.root_dir == Path(str(temp_dir / "data_ingestion"))


class TestDataIngestionPerformance:
    """Performance tests for data ingestion"""
    
    @pytest.mark.slow
    def test_download_performance(self, data_ingestion, mock_download, performance_threshold):
        """Test download performance"""
        import time
        
        # Mock download with delay
        def slow_download(*args, **kwargs):
            time.sleep(0.1)  # Simulate network delay
            return ("downloaded_file.zip", {})
        
        mock_download.side_effect = slow_download
        
        with patch('os.path.exists', return_value=False):
            start_time = time.time()
            data_ingestion.download_file()
            end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < performance_threshold["max_execution_time"]
    
    @pytest.mark.slow
    def test_extraction_performance(self, data_ingestion, mock_zipfile, performance_threshold):
        """Test extraction performance"""
        import time
        
        # Mock extraction with delay
        def slow_extract(*args, **kwargs):
            time.sleep(0.1)  # Simulate extraction delay
        
        mock_zipfile.return_value.__enter__.return_value.extractall.side_effect = slow_extract
        
        with patch('os.makedirs'):
            start_time = time.time()
            data_ingestion.extract_zip_file()
            end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < performance_threshold["max_execution_time"]