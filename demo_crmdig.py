#!/usr/bin/env python
"""
Demo script to test the CRMdig RDF module functionality.
This simulates the workflow that would be used in a Jupyter notebook.
"""

import sys
import os
import tempfile
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crmdig_rdf import ensure_uids, build_graph_from_dataframe, add_relations_to_graph, save_graph

def main():
    print("="*70)
    print("CRMdig RDF Module Demo")
    print("="*70)
    
    # Create a temporary directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample DROID CSV
        csv_path = os.path.join(tmpdir, "sample_droid.csv")
        
        print("\n1. Creating sample DROID CSV...")
        sample_data = pd.DataFrame({
            'FILE_PATH': [
                '/archive/documents/original_scan.tiff',
                '/archive/documents/converted_pdf.pdf',
                '/archive/documents/enhanced_version.tiff'
            ],
            'FORMAT_NAME': ['TIFF', 'PDF 1.4', 'TIFF'],
            'LAST_MODIFIED': ['2024-01-15T10:30:00', '2024-01-16T14:22:00', '2024-01-17T09:15:00']
        })
        sample_data.to_csv(csv_path, index=False)
        print(f"   ✓ Created {csv_path}")
        print(f"   ✓ Contains {len(sample_data)} files")
        
        # Ensure UIDs
        print("\n2. Ensuring stable UIDs...")
        df = ensure_uids(
            csv_path,
            base_ns="http://example.org/archive",
            uid_column="uid",
            inplace=True
        )
        print(f"   ✓ UIDs generated for {len(df)} files")
        print(f"   ✓ Sample UIDs:")
        for idx, row in df.iterrows():
            filename = os.path.basename(row['FILE_PATH'])
            print(f"      - {filename}: {row['uid'][:16]}...")
        
        # Build graph
        print("\n3. Building RDF graph...")
        graph = build_graph_from_dataframe(
            df,
            base_ns="http://example.org/archive",
            uid_column="uid"
        )
        print(f"   ✓ Graph initialized with {len(graph)} triples")
        
        # Add relations
        print("\n4. Adding file relations...")
        relations = [
            {
                'subject_uid': df.iloc[1]['uid'],  # PDF
                'object_uid': df.iloc[0]['uid'],   # Original TIFF
                'predicate': 'derives from',
                'label': 'Converted from original scan'
            },
            {
                'subject_uid': df.iloc[2]['uid'],  # Enhanced TIFF
                'object_uid': df.iloc[0]['uid'],   # Original TIFF
                'predicate': 'is variant of',
                'label': 'Enhanced version with better contrast'
            }
        ]
        
        add_relations_to_graph(graph, relations, base_ns="http://example.org/archive")
        print(f"   ✓ Added {len(relations)} relations")
        print(f"   ✓ Graph now has {len(graph)} triples")
        
        # Save graph
        print("\n5. Saving graph to Turtle format...")
        output_path = os.path.join(tmpdir, "relations.ttl")
        save_graph(graph, output_path, format='turtle')
        print(f"   ✓ Graph saved to {output_path}")
        
        # Display sample of output
        print("\n6. Sample output (first 20 lines):")
        print("-" * 70)
        with open(output_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:20]):
                print(f"   {line.rstrip()}")
            if len(lines) > 20:
                print(f"   ... ({len(lines) - 20} more lines)")
        print("-" * 70)
        
        print("\n" + "="*70)
        print("Demo completed successfully! ✓")
        print("="*70)
        print("\nNext steps:")
        print("1. Open notebooks/DCA_Ingest_2025-11-11.ipynb")
        print("2. Add a new cell with content from notebooks/CRMDIG_relations_cell.py")
        print("3. Uncomment interactive_relation_builder() to launch the UI")
        print("4. Or use the programmatic example to create relations")
        print("="*70)

if __name__ == '__main__':
    main()
