"""
Suggested code cell for DCA_Ingest_2025-11-11.ipynb

Add this cell to your notebook to enable CRMdig file relations annotation.
"""

# ============================================================================
# CRMdig File Relations Cell
# ============================================================================
# This cell provides interactive and programmatic tools for recording
# relations between files using CRMdigital (CRMdig) vocabulary.
#
# Prerequisites:
#   pip install rdflib ipywidgets
# ============================================================================

import sys
import os

# Import the CRMdig RDF module
# Add src path if not already in sys.path
if 'base_path' in locals():
    src_path = os.path.join(base_path, "27_DCA_Ingest/src")
else:
    src_path = os.path.join(os.path.expanduser("~"), "work/27_DCA_Ingest/src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from crmdig_rdf import ensure_uids, build_graph_from_dataframe, add_relations_to_graph, save_graph, interactive_relation_builder

# ============================================================================
# Configuration
# ============================================================================

# Reuse CSV_PATH and OUTPUT_DIR from earlier cells
# (These should be defined in previous notebook cells)
if 'CSV_PATH' not in locals() or 'OUTPUT_DIR' not in locals():
    print("Warning: CSV_PATH and OUTPUT_DIR not found. Using defaults.")
    CSV_PATH = os.path.join(os.path.expanduser("~"), "work/dcaonnextcloud-500gb/dca-metadataraw/Semiramis/2104_mockup_results/analysis_result.csv")
    OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "work/dcaonnextcloud-500gb/dca-metadataraw/Semiramis/2104_mockup_results/res")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set base namespace for RDF URIs
BASE_NS = "http://example.org/dca"

# Set output RDF file path
OUT_RDF = os.path.join(OUTPUT_DIR, "relations.ttl")

print(f"CSV Path: {CSV_PATH}")
print(f"Output RDF: {OUT_RDF}")
print(f"Base Namespace: {BASE_NS}")

# ============================================================================
# Step 1: Ensure Stable UIDs exist in CSV
# ============================================================================

print("\nEnsuring stable UIDs in CSV...")
df = ensure_uids(CSV_PATH, base_ns=BASE_NS, uid_column='uid', inplace=True)
print(f"✓ UIDs ensured for {len(df)} files")

# ============================================================================
# Step 2: Interactive Relation Builder (Jupyter UI)
# ============================================================================

# Uncomment the following line to launch the interactive UI:
# interactive_relation_builder(CSV_PATH, OUT_RDF, base_ns=BASE_NS, uid_column='uid')

print("\nTo launch the interactive UI, uncomment the line above and run this cell.")

# ============================================================================
# Step 3: Programmatic Example (Alternative to Interactive UI)
# ============================================================================
# 
# If you prefer to create relations programmatically instead of using the UI,
# uncomment and modify the example below:
#
# # Build graph from CSV
# graph = build_graph_from_dataframe(df, base_ns=BASE_NS, uid_column='uid')
# print(f"Graph initialized with {len(graph)} triples")
#
# # Define relations between files
# # Example: File A is output of Process B, File C derives from File A
# relations = [
#     {
#         "subject_uid": "your-file-uid-1",  # Replace with actual UID from CSV
#         "object_uid": "your-file-uid-2",
#         "predicate": "is output of",
#         "label": "Converted from original scan"
#     },
#     {
#         "subject_uid": "your-file-uid-3",
#         "object_uid": "your-file-uid-1",
#         "predicate": "derives from",
#         "label": "Enhanced version"
#     },
# ]
#
# # Add relations to graph
# add_relations_to_graph(graph, relations, base_ns=BASE_NS)
# print(f"Added {len(relations)} relations to graph")
#
# # Save graph to file
# save_graph(graph, OUT_RDF, format='turtle')
# print(f"✓ Graph saved to: {OUT_RDF}")
#
# # Display some triples
# print("\nSample triples:")
# for i, (s, p, o) in enumerate(graph):
#     if i < 10:
#         print(f"  {s} -> {p} -> {o}")
#     else:
#         break

print("\n" + "="*70)
print("CRMdig Relations Cell Ready!")
print("Choose one:")
print("1. Uncomment interactive_relation_builder() line to use the UI")
print("2. Uncomment the programmatic example to create relations via code")
print("="*70)
