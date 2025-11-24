# CRMdig File Relations Module with SARI SHACL Validation

## Übersicht / Overview

**Deutsch:**
Dieses Modul ermöglicht es, Beziehungen zwischen Dateien aus DROID CSV-Analysen zu erfassen und als RDF mit CRMdigital (CRMdig) Vokabular zu speichern. Es bietet sowohl eine interaktive Jupyter-Oberfläche als auch eine programmatische API. Alle RDF-Exporte werden automatisch gegen das SARI Reference Data Model mit SHACL validiert.

**English:**
This module enables recording relations between files from DROID CSV analyses and storing them as RDF using CRMdigital (CRMdig) vocabulary. It provides both an interactive Jupyter interface and a programmatic API. All RDF exports are automatically validated against the SARI Reference Data Model using SHACL.

---

## Installation

### Voraussetzungen / Prerequisites

**Deutsch:**
Installieren Sie die erforderlichen Python-Pakete:

**English:**
Install the required Python packages:

```bash
pip install rdflib ipywidgets pandas pyshacl
```

Oder verwenden Sie die Entwicklungs-Abhängigkeitsdatei:

Or use the development requirements file:

```bash
pip install -r requirements-dev.txt
```

---

## Verwendung / Usage

### Interaktive Nutzung (Jupyter Notebook) / Interactive Usage (Jupyter Notebook)

**Deutsch:**

1. Öffnen Sie das Notebook `notebooks/DCA_Ingest_2025-11-11.ipynb`
2. Führen Sie die vorherigen Zellen aus, um `CSV_PATH` und `OUTPUT_DIR` zu definieren
3. Fügen Sie eine neue Zelle hinzu und kopieren Sie den Inhalt aus `notebooks/CRMDIG_relations_cell.py`
4. Aktivieren Sie die interaktive UI durch Entkommentieren der Zeile:
   ```python
   interactive_relation_builder(CSV_PATH, OUT_RDF, base_ns=BASE_NS, uid_column='uid')
   ```
5. Führen Sie die Zelle aus
6. Verwenden Sie die Widgets, um:
   - Subjekt- und Objektdateien auszuwählen
   - Ein Prädikat auszuwählen (z.B. "is output of", "derives from")
   - Optional ein Label hinzuzufügen
   - Beziehungen zum Graph hinzuzufügen
   - Den Graph als Turtle-Datei zu speichern

**English:**

1. Open the notebook `notebooks/DCA_Ingest_2025-11-11.ipynb`
2. Run the previous cells to define `CSV_PATH` and `OUTPUT_DIR`
3. Add a new cell and copy the content from `notebooks/CRMDIG_relations_cell.py`
4. Enable the interactive UI by uncommenting the line:
   ```python
   interactive_relation_builder(CSV_PATH, OUT_RDF, base_ns=BASE_NS, uid_column='uid')
   ```
5. Run the cell
6. Use the widgets to:
   - Select subject and object files
   - Choose a predicate (e.g., "is output of", "derives from")
   - Optionally add a label
   - Add relations to the graph
   - Save the graph as a Turtle file

---

### Programmatische Nutzung / Programmatic Usage

**Deutsch:**
Beispiel für die Verwendung ohne interaktive UI:

**English:**
Example for non-interactive usage:

```python
from src.crmdig_rdf import ensure_uids, build_graph_from_dataframe, add_relations_to_graph, save_graph

# 1. Sicherstellen, dass UIDs existieren / Ensure UIDs exist
df = ensure_uids("path/to/droid.csv", base_ns="http://example.org", uid_column="uid", inplace=True)

# 2. Graph aus DataFrame erstellen / Build graph from DataFrame
graph = build_graph_from_dataframe(df, base_ns="http://example.org", uid_column="uid")

# 3. Beziehungen definieren / Define relations
relations = [
    {
        "subject_uid": "abc123...",
        "object_uid": "def456...",
        "predicate": "is output of",
        "label": "Converted from original"
    },
    {
        "subject_uid": "def456...",
        "object_uid": "ghi789...",
        "predicate": "derives from"
    }
]

# 4. Beziehungen zum Graph hinzufügen / Add relations to graph
add_relations_to_graph(graph, relations, base_ns="http://example.org")

# 5. Graph speichern / Save graph
save_graph(graph, "output/relations.ttl", format="turtle")
```

---

## Standard-Prädikate / Default Predicates

Das Modul bietet vordefinierte Prädikate für häufige Beziehungen:

The module provides predefined predicates for common relations:

- **"is output of"** → CRMdig.L11_had_output
- **"is input of"** → CRMdig.L21_used_as_derivation_source
- **"is variant of"** → DCTERMS.isVersionOf
- **"derives from"** → PROV.wasDerivedFrom
- **"alternate of / same as"** → DCTERMS.alternative

Sie können auch benutzerdefinierte URIs verwenden.

You can also use custom URIs.

---

## Funktionen / Functions

### `ensure_uids(csv_path, base_ns, uid_column, filepath_column, inplace)`

**Deutsch:**
Lädt eine DROID CSV und stellt sicher, dass eine Spalte mit stabilen UIDs (UUID5 basierend auf Dateipfad) existiert.

**English:**
Loads a DROID CSV and ensures a column with stable UIDs (UUID5 based on file path) exists.

### `build_graph_from_dataframe(df, base_ns, uid_column, filepath_column)`

**Deutsch:**
Erstellt einen RDF-Graph aus einem DataFrame mit grundlegenden Metadaten (Label, Pfad, Format, Datum, UID).

**English:**
Creates an RDF graph from a DataFrame with basic metadata (label, path, format, date, UID).

### `add_relations_to_graph(graph, relations, base_ns)`

**Deutsch:**
Fügt Beziehungen zwischen Dateien zum Graph hinzu.

**English:**
Adds relations between files to the graph.

### `save_graph(graph, output_path, format)`

**Deutsch:**
Serialisiert den RDF-Graph in eine Datei (Turtle, RDF/XML, N-Triples, etc.).

**English:**
Serializes the RDF graph to a file (Turtle, RDF/XML, N-Triples, etc.).

### `interactive_relation_builder(csv_path, out_rdf_path, base_ns, uid_column, filepath_column)`

**Deutsch:**
Startet eine interaktive Jupyter-UI zum Erstellen von Dateibeziehungen mit integrierter SHACL-Validierung.

**English:**
Launches an interactive Jupyter UI for creating file relations with integrated SHACL validation.

### `validate_with_shacl(graph, shacl_path, base_ns)`

**Deutsch:**
Validiert einen RDF-Graph gegen SARI Reference Data Model SHACL Shapes.

**English:**
Validates an RDF graph against SARI Reference Data Model SHACL shapes.

**Returns:**
- `conforms` (bool): True wenn der Graph den SHACL Shapes entspricht / True if graph conforms to SHACL shapes
- `report_graph` (Graph): RDF-Graph mit Validierungsbericht / RDF graph with validation report
- `report_text` (str): Menschenlesbarer Validierungsbericht / Human-readable validation report

### `save_validation_report(report_graph, report_text, output_path)`

**Deutsch:**
Speichert SHACL-Validierungsbericht als RDF (Turtle) und Text.

**English:**
Saves SHACL validation report as RDF (Turtle) and text.

---

## SARI Reference Data Model & SHACL Validation

**Deutsch:**
Das Modul enthält SHACL Shapes für die Validierung von RDF-Daten gemäß dem SARI Reference Data Model. Die Validierung prüft:

- **Pflichtfelder**: Jede Datei muss einen eindeutigen Identifier, Label und Dateipfad haben
- **Datentypen**: Format-Namen und andere Metadaten müssen korrekte Datentypen haben
- **Beziehungen**: Relations müssen auf gültige Datei-URIs verweisen
- **URI-Struktur**: Datei-URIs müssen dem Muster `{base_ns}/file/{uid}` folgen
- **Zirkuläre Beziehungen**: Dateien können nicht auf sich selbst verweisen

**English:**
The module includes SHACL shapes for validating RDF data according to the SARI Reference Data Model. The validation checks:

- **Required Fields**: Each file must have a unique identifier, label, and file path
- **Data Types**: Format names and other metadata must have correct data types
- **Relations**: Relations must point to valid file URIs
- **URI Structure**: File URIs must follow the pattern `{base_ns}/file/{uid}`
- **Circular Relations**: Files cannot reference themselves

**SHACL Shapes Location / Speicherort der SHACL Shapes:**
`res/shacl/sari_shapes.ttl`

---

## Ausgabeformat / Output Format

**Deutsch:**
Die Ausgabe ist eine RDF-Datei im Turtle-Format (.ttl) mit:
- URIs für jede Datei: `{base_ns}/file/{uid}`
- Metadaten-Tripel (Label, Pfad, Format, Datum, UID)
- Beziehungs-Tripel zwischen Dateien

**English:**
The output is an RDF file in Turtle format (.ttl) with:
- URIs for each file: `{base_ns}/file/{uid}`
- Metadata triples (label, path, format, date, UID)
- Relation triples between files

Beispiel / Example:
```turtle
@prefix crmdig: <http://www.ics.forth.gr/isl/CRMdig/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ex: <http://example.org/dca/> .

ex:file/abc123 a ex:File ;
    rdfs:label "document.pdf" ;
    ex:originalPath "/path/to/document.pdf" ;
    ex:formatName "PDF" ;
    dcterms:identifier "abc123" .

ex:file/def456 a ex:File ;
    rdfs:label "document_converted.tiff" ;
    ex:originalPath "/path/to/document_converted.tiff" ;
    ex:formatName "TIFF" ;
    dcterms:identifier "def456" .

ex:file/def456 prov:wasDerivedFrom ex:file/abc123 .
```

---

## Fehlerbehebung / Troubleshooting

**Problem:** `ImportError: rdflib is required`
**Lösung / Solution:** `pip install rdflib`

**Problem:** `ImportError: ipywidgets and IPython are required`
**Lösung / Solution:** `pip install ipywidgets ipython`

**Problem:** Column 'FILE_PATH' not found
**Lösung / Solution:** Das Modul versucht automatisch, die Dateipfad-Spalte zu erkennen. Wenn dies fehlschlägt, geben Sie `filepath_column` explizit an. / The module tries to auto-detect the filepath column. If this fails, specify `filepath_column` explicitly.

---

## Lizenz / License

Dieses Modul ist Teil des 27_DCA_Ingest Projekts.

This module is part of the 27_DCA_Ingest project.
