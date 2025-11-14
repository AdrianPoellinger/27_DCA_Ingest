"""
Tests for add_creation_dates module

These tests verify the functionality of adding creation dates to DROID CSV files.
"""

import os
import sys
import tempfile
import pandas as pd
import pytest
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from add_creation_dates import (
    get_creation_time,
    extract_file_path_from_uri,
    add_creation_dates_to_csv
)


def test_get_creation_time():
    """Test getting creation time from a real file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_path = f.name
        f.write("test content")
    
    try:
        # Get creation time
        creation_time = get_creation_time(temp_path)
        
        # Should return a valid ISO 8601 timestamp
        assert creation_time is not None
        assert isinstance(creation_time, str)
        
        # Should match the ISO format YYYY-MM-DDTHH:MM:SS
        datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S')
        
    finally:
        # Clean up
        os.unlink(temp_path)


def test_get_creation_time_nonexistent():
    """Test getting creation time for non-existent file."""
    result = get_creation_time('/path/that/does/not/exist/file.txt')
    assert result is None


def test_extract_file_path_from_uri():
    """Test extracting file paths from different URI formats."""
    # Standard file URI
    uri1 = 'file:/home/user/documents/file.pdf'
    result1 = extract_file_path_from_uri(uri1)
    assert result1 == '/home/user/documents/file.pdf'
    
    # ZIP URI
    uri2 = 'zip:file:/home/user/archive.zip!/internal/file.txt'
    result2 = extract_file_path_from_uri(uri2)
    assert result2 == '/home/user/archive.zip'
    
    # URI with URL encoding
    uri3 = 'file:/home/user/my%20documents/file.pdf'
    result3 = extract_file_path_from_uri(uri3)
    assert result3 == '/home/user/my documents/file.pdf'
    
    # None/NaN handling
    result4 = extract_file_path_from_uri(None)
    assert result4 is None


def test_add_creation_dates_to_csv():
    """Test adding creation dates to a DROID CSV file."""
    # Create temporary directory and files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        file1 = Path(tmpdir) / 'file1.txt'
        file2 = Path(tmpdir) / 'file2.pdf'
        file1.write_text('content 1')
        file2.write_text('content 2')
        
        # Create sample DROID CSV
        csv_path = Path(tmpdir) / 'droid_output.csv'
        df = pd.DataFrame({
            'ID': [1, 2],
            'FILE_PATH': [str(file1), str(file2)],
            'URI': [f'file:{file1}', f'file:{file2}'],
            'NAME': ['file1.txt', 'file2.pdf'],
            'LAST_MODIFIED': ['2023-01-15T10:30:00', '2023-02-20T14:45:00']
        })
        df.to_csv(csv_path, index=False)
        
        # Run the function
        output_path = Path(tmpdir) / 'output.csv'
        result_df = add_creation_dates_to_csv(
            input_csv=str(csv_path),
            output_csv=str(output_path)
        )
        
        # Verify results
        assert 'CREATION_DATE' in result_df.columns
        assert len(result_df) == 2
        
        # Both files should have creation dates
        assert result_df['CREATION_DATE'].notna().sum() == 2
        
        # Output file should exist
        assert output_path.exists()
        
        # Verify output can be read back
        df_loaded = pd.read_csv(output_path)
        assert 'CREATION_DATE' in df_loaded.columns


def test_add_creation_dates_inplace():
    """Test inplace modification of CSV."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / 'test.txt'
        test_file.write_text('test')
        
        # Create sample CSV
        csv_path = Path(tmpdir) / 'test.csv'
        df = pd.DataFrame({
            'FILE_PATH': [str(test_file)],
            'URI': [f'file:{test_file}'],
            'NAME': ['test.txt']
        })
        df.to_csv(csv_path, index=False)
        
        # Modify inplace
        result_df = add_creation_dates_to_csv(
            input_csv=str(csv_path),
            inplace=True
        )
        
        # Verify the original file was modified
        df_loaded = pd.read_csv(csv_path)
        assert 'CREATION_DATE' in df_loaded.columns


def test_add_creation_dates_with_missing_files():
    """Test handling of missing files in CSV."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create CSV with paths to non-existent files
        csv_path = Path(tmpdir) / 'test.csv'
        df = pd.DataFrame({
            'FILE_PATH': ['/nonexistent/file1.txt', '/nonexistent/file2.pdf'],
            'URI': ['file:/nonexistent/file1.txt', 'file:/nonexistent/file2.pdf'],
            'NAME': ['file1.txt', 'file2.pdf']
        })
        df.to_csv(csv_path, index=False)
        
        # Run the function
        result_df = add_creation_dates_to_csv(
            input_csv=str(csv_path),
            output_csv=str(Path(tmpdir) / 'output.csv')
        )
        
        # Should still create the column, but with None values
        assert 'CREATION_DATE' in result_df.columns
        # All values should be NaN/None since files don't exist
        assert result_df['CREATION_DATE'].isna().all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
