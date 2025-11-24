# SARI SHACL Validation Demo

This document demonstrates how to use the SARI Reference Data Model SHACL validation in the DCA_Ingest notebook.

## Quick Start

### Using the Interactive UI (Recommended)

1. Open `notebooks/DCA_Ingest_2025-11-11.ipynb`
2. Run all cells up to the export section (last cell)
3. In the export cell, uncomment this line:
   ```python
   interactive_relation_builder(CSV_PATH, OUT_RDF, base_ns=BASE_NS, uid_column='uid')
   ```
4. Run the cell - you'll see an interactive UI with:
   - Dropdown menus to select files
   - Predicate selection (e.g., "derives from", "is output of")
   - Optional label field
   - **"Validate with SHACL"** button - validates without saving
   - **"Save Graph"** button - validates and saves

### Programmatic Usage

```python
from crmdig_rdf import (
    ensure_uids,
    build_graph_from_dataframe,
    add_relations_to_graph,
    validate_with_shacl,
    save_validation_report,
    save_graph
)

# 1. Load data and ensure UIDs
df = ensure_uids(CSV_PATH, base_ns=BASE_NS, uid_column='uid', inplace=True)

# 2. Build RDF graph
graph = build_graph_from_dataframe(df, base_ns=BASE_NS, uid_column='uid')

# 3. Add relations
relations = [
    {
        'subject_uid': 'uid-123',
        'object_uid': 'uid-456',
        'predicate': 'derives from',
        'label': 'Converted from original'
    }
]
add_relations_to_graph(graph, relations, base_ns=BASE_NS)

# 4. Validate with SARI SHACL shapes
conforms, report_graph, report_text = validate_with_shacl(graph, base_ns=BASE_NS)

if conforms:
    print("✓ Graph conforms to SARI Reference Data Model")
else:
    print("⚠ Validation issues:")
    print(report_text)
    # Save validation report
    save_validation_report(report_graph, report_text, "validation_report")

# 5. Save graph
save_graph(graph, "output.ttl", format="turtle")
```

## What Gets Validated?

The SARI SHACL shapes validate:

### 1. Required Metadata
- ✅ Every file must have `dcterms:identifier` (unique ID)
- ✅ Every file must have `rdfs:label` (filename)

### 2. URI Structure
- ✅ File URIs follow pattern: `{base_ns}/file/{uid}`

### 3. Relation Validity
- ✅ Relations must point to valid file URIs
- ✅ Relation targets must exist in the dataset (have identifier)

### 4. Circular Relations
- ❌ Files cannot reference themselves
- ❌ Prevents: `file1 -> derives from -> file1`

## Example Validation Output

### Valid Graph
```
✓ SHACL Validation: PASSED
Graph conforms to SARI Reference Data Model
Total relations: 5
Total triples: 125
```

### Invalid Graph (Missing Label)
```
⚠ SHACL Validation: ISSUES FOUND

Validation Report
Conforms: False
Results (1):
Constraint Violation in MinCountConstraintComponent:
  Focus Node: <http://example.org/dca/file/abc123>
  Result Path: rdfs:label
  Message: Each digital file must have at least one label (rdfs:label / filename)
```

### Circular Relation Detected
```
⚠ SHACL Validation: ISSUES FOUND

Constraint Violation:
  Message: Circular relations detected - a file cannot be related to itself
  Focus Node: <http://example.org/dca/file/xyz789>
```

## Validation Reports

When validation fails, reports are saved in two formats:

1. **Human-readable text**: `validation_report.txt`
   - Easy to read error messages
   - Lists all constraint violations

2. **RDF format**: `validation_report.ttl`
   - Machine-readable validation results
   - Can be processed programmatically
   - Includes detailed provenance information

## SHACL Shapes Location

The SARI SHACL shapes are defined in:
```
res/shacl/sari_shapes.ttl
```

You can customize these shapes for project-specific requirements while maintaining SARI compliance.

## Integration with Existing Workflow

The SARI SHACL validation is seamlessly integrated:

1. **No breaking changes**: Existing code works without modification
2. **Opt-in validation**: Validation only runs when explicitly called
3. **Graceful degradation**: Graphs can be saved even if validation fails
4. **Clear feedback**: Validation results are displayed in Jupyter interface

## Dependencies

Ensure you have installed:
```bash
pip install -r requirements-dev.txt
```

This includes:
- `rdflib>=6.0.0` - RDF graph manipulation
- `pyshacl>=0.20.0` - SHACL validation engine
- `ipywidgets>=8.0.0` - Interactive Jupyter UI
- `pandas>=1.3.0` - Data handling

## Learn More

- Full documentation: [docs/CRMDIG_RELATIONS.md](../docs/CRMDIG_RELATIONS.md)
- SARI Reference Data Model: https://swissartresearch.net/
- SHACL Specification: https://www.w3.org/TR/shacl/
- CRMdig Vocabulary: http://www.ics.forth.gr/isl/CRMdig/

## Troubleshooting

### pyshacl not installed
```
Error: pyshacl is required for SHACL validation
```
**Solution**: `pip install pyshacl`

### SHACL shapes file not found
```
FileNotFoundError: SHACL shapes file not found
```
**Solution**: Ensure `res/shacl/sari_shapes.ttl` exists in the repository

### Validation takes too long
- Large datasets (>10,000 files) may take 10-30 seconds to validate
- Consider validating only after adding all relations, not after each addition
- Use the separate "Validate" button to check without saving
