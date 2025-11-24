"""
CRMdig RDF Module for DROID CSV File Relations

This module provides functionality to load DROID CSV files, generate stable UIDs for files,
build RDF graphs with file metadata, record relations between files using the CRMdigital
(CRMdig) vocabulary, and validate RDF data against SARI Reference Data Model using SHACL.

Basic Usage (Non-Interactive):
    >>> import pandas as pd
    >>> from crmdig_rdf import ensure_uids, build_graph_from_dataframe, add_relations_to_graph, save_graph, validate_with_shacl
    >>> 
    >>> # Ensure stable UIDs exist in CSV
    >>> df = ensure_uids("droid_output.csv", base_ns="http://example.org", uid_column="uid", inplace=True)
    >>> 
    >>> # Build RDF graph from DataFrame
    >>> graph = build_graph_from_dataframe(df, base_ns="http://example.org", uid_column="uid")
    >>> 
    >>> # Add relations between files
    >>> relations = [
    ...     {"subject_uid": "abc123", "object_uid": "def456", "predicate": "is output of"},
    ...     {"subject_uid": "def456", "object_uid": "ghi789", "predicate": "derives from", "label": "Original scan"}
    ... ]
    >>> add_relations_to_graph(graph, relations, base_ns="http://example.org")
    >>> 
    >>> # Validate graph against SARI SHACL shapes
    >>> conforms, report_graph, report_text = validate_with_shacl(graph)
    >>> if conforms:
    ...     print("Graph is valid according to SARI Reference Data Model")
    >>> else:
    ...     print("Validation errors:", report_text)
    >>> 
    >>> # Save graph to file
    >>> save_graph(graph, "relations.ttl", format="turtle")

Interactive Usage (in Jupyter):
    >>> from crmdig_rdf import interactive_relation_builder
    >>> interactive_relation_builder("droid_output.csv", "relations.ttl", base_ns="http://example.org", uid_column="uid")
"""

import os
import uuid
import pandas as pd
from typing import Optional, Dict, List, Union
from pathlib import Path

try:
    from rdflib import Graph, Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, DCTERMS, DC, PROV
except ImportError:
    raise ImportError("rdflib is required. Install with: pip install rdflib")

# Fixed namespace UUID for stable UID generation
NAMESPACE_UUID = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')

# Default namespace bindings
CRMDIG = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
EX = Namespace("http://example.org/")

# Default predicates mapping (friendly name -> URI)
DEFAULT_PREDICATES = {
    "is output of": CRMDIG.L11_had_output,
    "is input of": CRMDIG.L21_used_as_derivation_source,
    "is variant of": DCTERMS.isVersionOf,
    "derives from": PROV.wasDerivedFrom,
    "alternate of / same as": DCTERMS.alternative,
}


def guess_filepath_column(df: pd.DataFrame) -> Optional[str]:
    """
    Guess the filepath column from common DROID CSV column names.
    
    Args:
        df: DataFrame to search for filepath column
        
    Returns:
        Column name if found, None otherwise
    """
    common_names = ['FILE_PATH', 'URI', 'FILE_URI', 'Path', 'FilePath', 'file_path']
    
    for col in common_names:
        if col in df.columns:
            return col
    
    # Case-insensitive search
    for col in df.columns:
        if col.upper() in [name.upper() for name in common_names]:
            return col
    
    return None


def ensure_uids(
    csv_path: str,
    base_ns: str = "http://example.org",
    uid_column: str = "uid",
    filepath_column: Optional[str] = None,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Load a DROID CSV and ensure a stable UID column exists.
    
    UIDs are generated using UUID5 with a fixed namespace and the file path.
    This ensures the same file path always generates the same UID.
    
    Args:
        csv_path: Path to DROID CSV file
        base_ns: Base namespace for generating UIDs
        uid_column: Name of column to store UIDs
        filepath_column: Name of filepath column (auto-detected if None)
        inplace: If True, update the CSV file with UIDs
        
    Returns:
        DataFrame with UID column added
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If filepath column cannot be determined
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Auto-detect filepath column if not provided
    if filepath_column is None:
        filepath_column = guess_filepath_column(df)
        if filepath_column is None:
            raise ValueError(
                f"Could not determine filepath column. Available columns: {list(df.columns)}"
            )
    
    if filepath_column not in df.columns:
        raise ValueError(
            f"Filepath column '{filepath_column}' not found. Available columns: {list(df.columns)}"
        )
    
    # Generate stable UIDs if column doesn't exist or has missing values
    if uid_column not in df.columns or df[uid_column].isna().any():
        def generate_uid(filepath):
            if pd.isna(filepath):
                return None
            # Combine base_ns and filepath for stable UUID generation
            name = f"{base_ns}#{filepath}"
            return str(uuid.uuid5(NAMESPACE_UUID, name))
        
        df[uid_column] = df[filepath_column].apply(generate_uid)
    
    # Save if inplace requested
    if inplace:
        df.to_csv(csv_path, index=False)
    
    return df


def build_graph_from_dataframe(
    df: pd.DataFrame,
    base_ns: str = "http://example.org",
    uid_column: str = "uid",
    filepath_column: Optional[str] = None
) -> Graph:
    """
    Build an RDF graph from a DataFrame with file metadata.
    
    Creates one URI per file (base_ns + "/file/" + uid) and adds basic metadata triples:
    - rdfs:label (filename)
    - ex:originalPath (full file path)
    - ex:formatName (from FORMAT_NAME column if present)
    - dcterms:modified (from LAST_MODIFIED column if present)
    - dcterms:identifier (the UID)
    
    Args:
        df: DataFrame with file data
        base_ns: Base namespace for URIs
        uid_column: Name of UID column
        filepath_column: Name of filepath column (auto-detected if None)
        
    Returns:
        RDF Graph with file metadata
        
    Raises:
        ValueError: If required columns are missing
    """
    if uid_column not in df.columns:
        raise ValueError(f"UID column '{uid_column}' not found in DataFrame")
    
    # Auto-detect filepath column if not provided
    if filepath_column is None:
        filepath_column = guess_filepath_column(df)
        if filepath_column is None:
            raise ValueError(
                f"Could not determine filepath column. Available columns: {list(df.columns)}"
            )
    
    # Initialize graph with namespace bindings
    g = Graph()
    ns = Namespace(base_ns.rstrip('/') + '/')
    g.bind('crmdig', CRMDIG)
    g.bind('ex', ns)
    g.bind('prov', PROV)
    g.bind('dcterms', DCTERMS)
    g.bind('dc', DC)
    
    # Add triples for each file
    for idx, row in df.iterrows():
        uid = row.get(uid_column)
        if pd.isna(uid):
            continue
        
        # Create URI for this file
        file_uri = URIRef(f"{base_ns.rstrip('/')}/file/{uid}")
        
        # Add basic metadata
        # Label (filename from path)
        filepath = row.get(filepath_column)
        if pd.notna(filepath):
            filename = os.path.basename(str(filepath))
            g.add((file_uri, RDFS.label, Literal(filename)))
            g.add((file_uri, ns.originalPath, Literal(str(filepath))))
        
        # Format name
        if 'FORMAT_NAME' in df.columns and pd.notna(row.get('FORMAT_NAME')):
            g.add((file_uri, ns.formatName, Literal(row['FORMAT_NAME'])))
        
        # Last modified
        if 'LAST_MODIFIED' in df.columns and pd.notna(row.get('LAST_MODIFIED')):
            g.add((file_uri, DCTERMS.modified, Literal(row['LAST_MODIFIED'])))
        
        # Identifier (UID)
        g.add((file_uri, DCTERMS.identifier, Literal(uid)))
    
    return g


def add_relations_to_graph(
    graph: Graph,
    relations: List[Dict[str, str]],
    base_ns: str = "http://example.org"
) -> None:
    """
    Add relations between files to an RDF graph.
    
    Relations are provided as a list of dicts with:
    - subject_uid: UID of subject file
    - object_uid: UID of object file
    - predicate: Either a friendly key (from DEFAULT_PREDICATES) or a full URI
    - label: Optional label for the relation
    
    Args:
        graph: RDF graph to add relations to
        relations: List of relation dicts
        base_ns: Base namespace for URIs
    """
    ns = Namespace(base_ns.rstrip('/') + '/')
    
    for relation in relations:
        subject_uid = relation.get('subject_uid')
        object_uid = relation.get('object_uid')
        predicate = relation.get('predicate')
        label = relation.get('label')
        
        if not subject_uid or not object_uid or not predicate:
            continue
        
        # Create URIs
        subject_uri = URIRef(f"{base_ns.rstrip('/')}/file/{subject_uid}")
        object_uri = URIRef(f"{base_ns.rstrip('/')}/file/{object_uid}")
        
        # Determine predicate URI
        if predicate in DEFAULT_PREDICATES:
            predicate_uri = DEFAULT_PREDICATES[predicate]
        else:
            # Assume it's a full URI
            predicate_uri = URIRef(predicate)
        
        # Add relation triple
        graph.add((subject_uri, predicate_uri, object_uri))
        
        # Add optional label
        if label:
            # Create a blank node for the relation statement (reification)
            # or just add as comment - keeping it simple
            graph.add((subject_uri, RDFS.comment, Literal(f"{predicate}: {label}")))


def save_graph(graph: Graph, output_path: str, format: str = "turtle") -> None:
    """
    Serialize RDF graph to file.
    
    Creates parent directories if they don't exist.
    
    Args:
        graph: RDF graph to serialize
        output_path: Path to output file
        format: RDF serialization format (turtle, xml, n3, nt, etc.)
    """
    # Create parent directories
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Serialize graph
    graph.serialize(destination=output_path, format=format)


def validate_with_shacl(
    graph: Graph,
    shacl_path: Optional[str] = None,
    base_ns: str = "http://example.org"
) -> tuple:
    """
    Validate RDF graph against SARI Reference Data Model using SHACL shapes.
    
    Args:
        graph: RDF graph to validate
        shacl_path: Path to SHACL shapes file (uses default SARI shapes if None)
        base_ns: Base namespace used in the graph (for dynamic shape adjustment)
        
    Returns:
        Tuple of (conforms: bool, report_graph: Graph, report_text: str)
        - conforms: True if graph validates successfully, False otherwise
        - report_graph: RDF graph containing validation report
        - report_text: Human-readable validation report text
        
    Raises:
        ImportError: If pyshacl is not installed
        FileNotFoundError: If SHACL shapes file not found
    """
    try:
        from pyshacl import validate
    except ImportError:
        raise ImportError(
            "pyshacl is required for SHACL validation. Install with: pip install pyshacl"
        )
    
    # Use default SARI shapes if none provided
    if shacl_path is None:
        # Get default SHACL shapes from res/shacl/sari_shapes.ttl
        module_dir = Path(__file__).parent.parent
        shacl_path = module_dir / "res" / "shacl" / "sari_shapes.ttl"
    
    if not os.path.exists(shacl_path):
        raise FileNotFoundError(f"SHACL shapes file not found: {shacl_path}")
    
    # Load SHACL shapes
    shacl_graph = Graph()
    shacl_graph.parse(shacl_path, format="turtle")
    
    # Add File class type to all file URIs in the data graph if not present
    # This ensures SHACL shape targets work correctly
    ns = Namespace(base_ns.rstrip('/') + '/')
    file_class = ns.File
    
    # Find all file URIs (those matching pattern /file/{uid})
    for s, p, o in graph:
        if "/file/" in str(s):
            # Add type triple if not already present
            if (s, RDF.type, file_class) not in graph:
                graph.add((s, RDF.type, file_class))
    
    # Perform validation
    conforms, report_graph, report_text = validate(
        data_graph=graph,
        shacl_graph=shacl_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        advanced=True,
        js=False
    )
    
    return conforms, report_graph, report_text


def save_validation_report(
    report_graph: Graph,
    report_text: str,
    output_path: str
) -> None:
    """
    Save SHACL validation report to file.
    
    Saves both the RDF report graph (as Turtle) and human-readable text.
    
    Args:
        report_graph: RDF graph containing validation report
        report_text: Human-readable validation report text
        output_path: Base path for output files (will create .ttl and .txt)
    """
    # Create parent directories
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save RDF report
    base_path = Path(output_path)
    ttl_path = base_path.with_suffix('.ttl')
    report_graph.serialize(destination=str(ttl_path), format='turtle')
    
    # Save text report
    txt_path = base_path.with_suffix('.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(report_text)


def interactive_relation_builder(
    csv_path: str,
    out_rdf_path: str,
    base_ns: str = "http://example.org",
    uid_column: str = "uid",
    filepath_column: Optional[str] = None
) -> None:
    """
    Launch an interactive UI for building file relations in Jupyter.
    
    Provides widgets to:
    - Select subject and object files
    - Choose predicate (from DEFAULT_PREDICATES or custom URI)
    - Add optional label
    - Add relations to graph
    - Save graph to disk
    
    Args:
        csv_path: Path to DROID CSV file
        out_rdf_path: Path to output RDF file
        base_ns: Base namespace for URIs
        uid_column: Name of UID column
        filepath_column: Name of filepath column (auto-detected if None)
    """
    try:
        import ipywidgets as widgets
        from IPython.display import display, clear_output
    except ImportError:
        raise ImportError("ipywidgets and IPython are required for interactive mode. Install with: pip install ipywidgets ipython")
    
    # Load data and ensure UIDs
    df = ensure_uids(csv_path, base_ns=base_ns, uid_column=uid_column, filepath_column=filepath_column)
    
    # Build initial graph
    graph = build_graph_from_dataframe(df, base_ns=base_ns, uid_column=uid_column, filepath_column=filepath_column)
    
    # Detect filepath column
    if filepath_column is None:
        filepath_column = guess_filepath_column(df)
    
    # Prepare file choices (display filename with UID)
    file_choices = {}
    for idx, row in df.iterrows():
        uid = row.get(uid_column)
        filepath = row.get(filepath_column)
        if pd.notna(uid) and pd.notna(filepath):
            filename = os.path.basename(str(filepath))
            file_choices[f"{filename} ({uid[:8]})"] = uid
    
    # Store relations in memory
    relations_list = []
    
    # Create widgets
    output_area = widgets.Output()
    
    subject_dropdown = widgets.Dropdown(
        options=file_choices,
        description='Subject:',
        layout=widgets.Layout(width='500px')
    )
    
    object_dropdown = widgets.Dropdown(
        options=file_choices,
        description='Object:',
        layout=widgets.Layout(width='500px')
    )
    
    predicate_dropdown = widgets.Dropdown(
        options=list(DEFAULT_PREDICATES.keys()) + ['Custom URI...'],
        description='Predicate:',
        layout=widgets.Layout(width='500px')
    )
    
    custom_predicate_text = widgets.Text(
        description='Custom URI:',
        placeholder='http://example.org/customPredicate',
        layout=widgets.Layout(width='500px')
    )
    
    label_text = widgets.Text(
        description='Label:',
        placeholder='Optional label for this relation',
        layout=widgets.Layout(width='500px')
    )
    
    add_button = widgets.Button(
        description='Add Relation',
        button_style='primary'
    )
    
    validate_button = widgets.Button(
        description='Validate with SHACL',
        button_style='info'
    )
    
    save_button = widgets.Button(
        description='Save Graph',
        button_style='success'
    )
    
    status_label = widgets.Label(value='Ready to add relations')
    
    # Event handlers
    def on_add_relation(b):
        subject_uid = subject_dropdown.value
        object_uid = object_dropdown.value
        
        if predicate_dropdown.value == 'Custom URI...':
            predicate = custom_predicate_text.value
        else:
            predicate = predicate_dropdown.value
        
        label = label_text.value if label_text.value else None
        
        if not subject_uid or not object_uid or not predicate:
            status_label.value = 'Error: Please fill in all required fields'
            return
        
        # Add to relations list
        relation = {
            'subject_uid': subject_uid,
            'object_uid': object_uid,
            'predicate': predicate,
            'label': label
        }
        relations_list.append(relation)
        
        # Add to graph
        add_relations_to_graph(graph, [relation], base_ns=base_ns)
        
        # Update status
        status_label.value = f'Added: {subject_dropdown.label} -> {predicate} -> {object_dropdown.label}'
        
        # Clear label field
        label_text.value = ''
        
        # Update output
        with output_area:
            clear_output(wait=True)
            print(f"Total relations added: {len(relations_list)}")
            print("\nRecent relations:")
            for rel in relations_list[-5:]:
                subj = [k for k, v in file_choices.items() if v == rel['subject_uid']][0]
                obj = [k for k, v in file_choices.items() if v == rel['object_uid']][0]
                print(f"  {subj} -> {rel['predicate']} -> {obj}")
                if rel.get('label'):
                    print(f"    Label: {rel['label']}")
    
    def on_validate_graph(b):
        try:
            status_label.value = 'Validating graph against SARI SHACL shapes...'
            conforms, report_graph, report_text = validate_with_shacl(graph, base_ns=base_ns)
            
            if conforms:
                status_label.value = '✓ Validation successful! Graph conforms to SARI Reference Data Model'
                with output_area:
                    clear_output(wait=True)
                    print("✓ SHACL Validation: PASSED")
                    print(f"Total relations: {len(relations_list)}")
                    print(f"Total triples: {len(graph)}")
            else:
                status_label.value = '⚠ Validation issues found - see output area'
                with output_area:
                    clear_output(wait=True)
                    print("⚠ SHACL Validation: ISSUES FOUND\n")
                    print(report_text)
                    
                # Save validation report
                report_path = Path(out_rdf_path).parent / "validation_report"
                save_validation_report(report_graph, report_text, str(report_path))
                print(f"\nValidation report saved to: {report_path}.txt and {report_path}.ttl")
        except Exception as e:
            status_label.value = f'Error validating: {str(e)}'
            with output_area:
                clear_output(wait=True)
                print(f"Error during validation: {str(e)}")
    
    def on_save_graph(b):
        try:
            # Validate before saving
            status_label.value = 'Validating graph before saving...'
            conforms, report_graph, report_text = validate_with_shacl(graph, base_ns=base_ns)
            
            # Save graph regardless of validation result
            save_graph(graph, out_rdf_path, format='turtle')
            
            if conforms:
                status_label.value = f'✓ Success! Graph validated and saved to {out_rdf_path}'
                with output_area:
                    clear_output(wait=True)
                    print(f"✓ Graph saved to: {out_rdf_path}")
                    print("✓ SHACL validation: PASSED")
                    print(f"Total relations: {len(relations_list)}")
                    print(f"Total triples: {len(graph)}")
            else:
                status_label.value = f'⚠ Graph saved but has validation issues - see output'
                with output_area:
                    clear_output(wait=True)
                    print(f"Graph saved to: {out_rdf_path}")
                    print("\n⚠ SHACL Validation: ISSUES FOUND")
                    print(report_text[:500])  # Show first 500 chars
                    
                # Save validation report
                report_path = Path(out_rdf_path).parent / "validation_report"
                save_validation_report(report_graph, report_text, str(report_path))
                print(f"\nFull validation report: {report_path}.txt")
        except Exception as e:
            status_label.value = f'Error saving: {str(e)}'
            with output_area:
                clear_output(wait=True)
                print(f"Error: {str(e)}")
    
    add_button.on_click(on_add_relation)
    validate_button.on_click(on_validate_graph)
    save_button.on_click(on_save_graph)
    
    # Layout
    ui = widgets.VBox([
        widgets.HTML("<h3>CRMdig File Relations Builder</h3>"),
        widgets.HTML(f"<p>CSV: {csv_path}<br>Output: {out_rdf_path}</p>"),
        widgets.HTML("<p><strong>SARI Reference Data Model</strong> - Exports are validated with SHACL shapes</p>"),
        subject_dropdown,
        object_dropdown,
        predicate_dropdown,
        custom_predicate_text,
        label_text,
        widgets.HBox([add_button, validate_button, save_button]),
        status_label,
        output_area
    ])
    
    display(ui)
    
    # Initial output
    with output_area:
        print(f"Loaded {len(df)} files from CSV")
        print(f"Graph initialized with {len(graph)} triples")
# Temporary line for code review
