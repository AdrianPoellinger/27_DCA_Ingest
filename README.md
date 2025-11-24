# 27_DCA_Ingest

Digital Collection Analysis and Ingest tools for working with DROID CSV outputs.

## Features

- **DROID Analysis**: Run DROID format identification on digital collections
- **Creation Date Enrichment**: Add file creation dates to DROID CSV outputs (DROID only provides last modified date)
- **Format Analysis**: Analyze and visualize file formats in collections
- **CRMdig Relations**: Record semantic relations between files using CRMdigital vocabulary (see [docs/CRMDIG_RELATIONS.md](docs/CRMDIG_RELATIONS.md))
- **SARI SHACL Validation**: Validate RDF exports against SARI Reference Data Model using SHACL shapes

## Installation

### Basic Setup

Using conda (recommended):
```bash
conda env create -f environment.yml
conda activate combined-env
```

### Development Setup

For development work with the CRMdig relations module and SHACL validation:
```bash
pip install -r requirements-dev.txt
```

This installs:
- rdflib (RDF graph manipulation)
- ipywidgets (interactive Jupyter UI)
- pyshacl (SHACL validation for SARI Reference Data Model)
- pytest (testing framework)

## Usage

### Jupyter Notebooks

The main analysis workflow is in `notebooks/DCA_Ingest_2025-11-11.ipynb` or `notebooks/DCA_Ingest_2025-11-11_Keller.ipynb`.

#### Adding File Creation Dates

DROID provides the last modified date but not the creation date. After running DROID analysis, you can enrich the CSV with creation dates:

```python
from add_creation_dates import add_creation_dates_to_csv

# Enrich DROID output with creation dates
df = add_creation_dates_to_csv(
    input_csv="path/to/droid_output.csv",
    output_csv="path/to/enriched_output.csv"
)
```

Or use the command line:
```bash
python src/add_creation_dates.py --input droid_output.csv --output enriched_output.csv
```

#### CRMdig File Relations

To add CRMdig file relations annotation with SARI SHACL validation:
1. Open the notebook
2. The last cell already contains the CRMdig relations export with SARI SHACL validation
3. Run the cell and use the interactive UI or programmatic API
4. RDF exports are automatically validated against SARI Reference Data Model

See [docs/CRMDIG_RELATIONS.md](docs/CRMDIG_RELATIONS.md) for detailed instructions.

### Running Tests

```bash
pytest tests/
```

## Documentation

- [CRMdig Relations Module](docs/CRMDIG_RELATIONS.md) - Bilingual (DE/EN) documentation for recording file relations

## Project Structure

```
27_DCA_Ingest/
├── src/                    # Python modules
│   ├── crmdig_rdf.py      # CRMdig RDF relations module
│   ├── add_creation_dates.py  # Add creation dates to DROID CSV
│   ├── run_DROID.py       # DROID execution
│   └── analyse_*.py       # Analysis modules
├── notebooks/             # Jupyter notebooks
│   ├── DCA_Ingest_2025-11-11.ipynb
│   ├── DCA_Ingest_2025-11-11_Keller.ipynb
│   └── CRMDIG_relations_cell.py
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── res/                   # Resources and outputs
```