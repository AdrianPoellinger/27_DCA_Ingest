# 27_DCA_Ingest

Digital Collection Analysis and Ingest tools for working with DROID CSV outputs.

## Features

- **DROID Analysis**: Run DROID format identification on digital collections
- **Format Analysis**: Analyze and visualize file formats in collections
- **CRMdig Relations**: Record semantic relations between files using CRMdigital vocabulary (see [docs/CRMDIG_RELATIONS.md](docs/CRMDIG_RELATIONS.md))

## Installation

### Basic Setup

Using conda (recommended):
```bash
conda env create -f environment.yml
conda activate combined-env
```

### Development Setup

For development work with the CRMdig relations module:
```bash
pip install -r requirements-dev.txt
```

This installs:
- rdflib (RDF graph manipulation)
- ipywidgets (interactive Jupyter UI)
- pytest (testing framework)

## Usage

### Jupyter Notebooks

The main analysis workflow is in `notebooks/DCA_Ingest_2025-11-11.ipynb`.

To add CRMdig file relations annotation:
1. Open the notebook
2. Add a new cell with content from `notebooks/CRMDIG_relations_cell.py`
3. Run the cell and use the interactive UI or programmatic API

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
│   ├── run_DROID.py       # DROID execution
│   └── analyse_*.py       # Analysis modules
├── notebooks/             # Jupyter notebooks
│   ├── DCA_Ingest_2025-11-11.ipynb
│   └── CRMDIG_relations_cell.py
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── res/                   # Resources and outputs
```