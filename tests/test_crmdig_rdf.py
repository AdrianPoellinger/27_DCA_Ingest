"""
Smoke tests for crmdig_rdf module

These tests verify basic functionality without requiring external DROID CSV files.
"""

import os
import sys
import tempfile
import warnings
from io import StringIO
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crmdig_rdf import (
    ensure_uids,
    build_graph_from_dataframe,
    add_relations_to_graph,
    save_graph,
    guess_filepath_column
)


def create_sample_dataframe():
    """Create a small sample DataFrame mimicking DROID CSV structure."""
    return pd.DataFrame({
        'FILE_PATH': [
            '/path/to/file1.pdf',
            '/path/to/file2.tiff',
            '/path/to/file3.jpg'
        ],
        'FORMAT_NAME': ['PDF', 'TIFF', 'JPEG'],
        'LAST_MODIFIED': ['2024-01-01', '2024-01-02', '2024-01-03']
    })


def test_guess_filepath_column():
    """Test filepath column auto-detection."""
    df = pd.DataFrame({
        'FILE_PATH': ['/path/to/file.txt'],
        'OTHER_COLUMN': ['value']
    })
    
    column = guess_filepath_column(df)
    assert column == 'FILE_PATH'
    
    # Test case-insensitive
    df2 = pd.DataFrame({
        'file_path': ['/path/to/file.txt']
    })
    column2 = guess_filepath_column(df2)
    assert column2 == 'file_path'
    
    # Test URI column
    df3 = pd.DataFrame({
        'URI': ['/path/to/file.txt']
    })
    column3 = guess_filepath_column(df3)
    assert column3 == 'URI'


def test_ensure_uids():
    """Test UID generation from DataFrame."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
        df = create_sample_dataframe()
        df.to_csv(csv_path, index=False)
    
    try:
        # Test UID generation
        df_with_uids = ensure_uids(
            csv_path,
            base_ns="http://example.org",
            uid_column="uid",
            inplace=False
        )
        
        # Check UID column exists
        assert 'uid' in df_with_uids.columns
        
        # Check all UIDs are present
        assert df_with_uids['uid'].notna().all()
        
        # Check UIDs are stable (running again should produce same UIDs)
        df_with_uids2 = ensure_uids(
            csv_path,
            base_ns="http://example.org",
            uid_column="uid",
            inplace=False
        )
        
        assert df_with_uids['uid'].equals(df_with_uids2['uid'])
        
    finally:
        os.unlink(csv_path)


def test_build_graph_from_dataframe():
    """Test RDF graph building from DataFrame."""
    df = create_sample_dataframe()
    df['uid'] = ['uid1', 'uid2', 'uid3']
    
    graph = build_graph_from_dataframe(
        df,
        base_ns="http://example.org",
        uid_column="uid"
    )
    
    # Check graph is not empty
    assert len(graph) > 0
    
    # Check namespace bindings
    namespaces = dict(graph.namespaces())
    assert 'crmdig' in namespaces
    assert 'ex' in namespaces
    assert 'dcterms' in namespaces
    
    # Check that we have triples for each file
    # At minimum: identifier triple for each file (3 files = 3 triples minimum)
    assert len(graph) >= 3


def test_add_relations_to_graph():
    """Test adding relations to graph."""
    df = create_sample_dataframe()
    df['uid'] = ['uid1', 'uid2', 'uid3']
    
    graph = build_graph_from_dataframe(
        df,
        base_ns="http://example.org",
        uid_column="uid"
    )
    
    initial_size = len(graph)
    
    # Add relations
    relations = [
        {
            'subject_uid': 'uid2',
            'object_uid': 'uid1',
            'predicate': 'derives from',
            'label': 'Converted version'
        },
        {
            'subject_uid': 'uid3',
            'object_uid': 'uid1',
            'predicate': 'is variant of'
        }
    ]
    
    add_relations_to_graph(graph, relations, base_ns="http://example.org")
    
    # Check that graph grew (relations added)
    assert len(graph) > initial_size


def test_save_graph():
    """Test graph serialization."""
    df = create_sample_dataframe()
    df['uid'] = ['uid1', 'uid2', 'uid3']
    
    graph = build_graph_from_dataframe(
        df,
        base_ns="http://example.org",
        uid_column="uid"
    )
    
    # Test saving to turtle format
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'subdir', 'test.ttl')
        
        # Should create parent directories
        save_graph(graph, output_path, format='turtle')
        
        # Check file exists
        assert os.path.exists(output_path)
        
        # Check file has content
        with open(output_path, 'r') as f:
            content = f.read()
            assert len(content) > 0
            assert '@prefix' in content  # Turtle format marker


def test_full_workflow():
    """Test complete workflow: CSV -> UIDs -> Graph -> Relations -> Save."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
        df = create_sample_dataframe()
        df.to_csv(csv_path, index=False)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'relations.ttl')
        
        try:
            # Step 1: Ensure UIDs
            df = ensure_uids(
                csv_path,
                base_ns="http://example.org/test",
                uid_column="uid",
                inplace=True
            )
            
            # Step 2: Build graph
            graph = build_graph_from_dataframe(
                df,
                base_ns="http://example.org/test",
                uid_column="uid"
            )
            
            # Step 3: Add relations
            uid1 = df.iloc[0]['uid']
            uid2 = df.iloc[1]['uid']
            
            relations = [
                {
                    'subject_uid': uid2,
                    'object_uid': uid1,
                    'predicate': 'derives from',
                    'label': 'Test relation'
                }
            ]
            
            add_relations_to_graph(graph, relations, base_ns="http://example.org/test")
            
            # Step 4: Save
            save_graph(graph, output_path, format='turtle')
            
            # Verify output
            assert os.path.exists(output_path)
            
            # Read and verify content
            with open(output_path, 'r') as f:
                content = f.read()
                assert 'file1.pdf' in content or 'uid' in content
                assert '@prefix' in content
        
        finally:
            os.unlink(csv_path)


def test_csv_with_commas_in_fields():
    """Test that CSV files with commas in data fields are handled correctly."""
    # Create a CSV with commas in file paths (a common real-world scenario)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
        # Write CSV content with commas in field values (properly quoted)
        f.write('FILE_PATH,FORMAT_NAME,LAST_MODIFIED\n')
        f.write('"/path/with,comma/file1.pdf",PDF,2024-01-01\n')
        f.write('"/another/path,with,multiple,commas/file2.tiff",TIFF,2024-01-02\n')
        f.write('/normal/path/file3.jpg,JPEG,2024-01-03\n')
    
    try:
        # Should not raise ParserError
        df = ensure_uids(
            csv_path,
            base_ns="http://example.org",
            uid_column="uid",
            inplace=False
        )
        
        # Verify all rows were read correctly
        assert len(df) == 3
        assert 'uid' in df.columns
        assert df['uid'].notna().all()
        
        # Verify file paths were preserved correctly (including commas)
        assert 'comma' in df.iloc[0]['FILE_PATH']
        assert 'multiple' in df.iloc[1]['FILE_PATH']
        
    finally:
        os.unlink(csv_path)


def test_csv_with_unquoted_commas():
    """Test that CSV files with unquoted commas are handled gracefully."""
    # Create a CSV with unquoted commas (malformed but real-world scenario)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = f.name
        f.write('FILE_PATH,FORMAT_NAME,LAST_MODIFIED\n')
        f.write('/path/to/file1.pdf,PDF,2024-01-01\n')
        # This line has an unquoted comma in the path - should be skipped
        f.write('/path/with,unquoted,comma/file2.tiff,TIFF,2024-01-02\n')
        f.write('/normal/path/file3.jpg,JPEG,2024-01-03\n')
    
    try:
        # Capture stdout to verify warnings are printed
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        # Should handle the error gracefully and skip the bad line
        df = ensure_uids(
            csv_path,
            base_ns="http://example.org",
            uid_column="uid",
            inplace=False
        )
        
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        
        # Verify that error handling was triggered
        # The key verification is that we got a DataFrame with the expected number of rows
        assert len(df) == 2, "Should have loaded 2 valid rows, skipping the malformed one"
        assert 'uid' in df.columns, "UID column should exist"
        assert df['uid'].notna().all(), "All UIDs should be non-null"
        
        # Verify the correct rows were loaded (the ones without commas in the path)
        file_paths = df['FILE_PATH'].tolist()
        assert any('file1.pdf' in fp for fp in file_paths), "Should contain file1.pdf"
        assert any('file3.jpg' in fp for fp in file_paths), "Should contain file3.jpg"
        
        # Verify warning output was generated (less fragile check)
        assert len(output) > 0, "Should have printed warning/info messages"
        
    finally:
        os.unlink(csv_path)


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
