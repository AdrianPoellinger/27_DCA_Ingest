
import matplotlib.pyplot as plt
import pandas as pd
import os

def analyse_format_over_creation_time_df(df, format_name, date_column="creation_iso", output_dir=None, show_plot=True, verbose=True):
    # Spaltennamen säubern
    df = df.copy()
    df.columns = df.columns.str.strip()

    if date_column not in df.columns:
        raise ValueError(f"Spalte '{date_column}' nicht in DataFrame. Verfügbare Spalten: {list(df.columns)}")

    # Robuster Vergleich: case-insensitive
    target = str(format_name).strip().lower()

    # Prüfen, ob FORMAT_NAME existiert und Treffer hat
    use_column = None
    if "FORMAT_NAME" in df.columns:
        mask_format = df['FORMAT_NAME'].astype(str).str.strip().str.lower() == target
        if mask_format.any():
            use_column = "FORMAT_NAME"
            mask = mask_format

    # Falls keine Treffer, EXT prüfen
    if use_column is None and "EXT" in df.columns:
        mask_ext = df['EXT'].astype(str).str.strip().str.lower() == target
        if mask_ext.any():
            use_column = "EXT"
            mask = mask_ext

    if use_column is None:
        print(f"Kein Treffer für '{format_name}' in FORMAT_NAME oder EXT.")
        return None

    filtered_df = df[mask].copy()
    if verbose:
        print(f"Gefilterte Zeilen für '{format_name}' in Spalte '{use_column}': {filtered_df.shape[0]}")

    # Datumsstrings bereinigen und parsen
    s = filtered_df[date_column].astype(str).str.strip().replace(r'(^nan$)', '', regex=True)
    s = s.str.replace(r'Z$', '', regex=True)
    parsed = pd.to_datetime(s, errors='coerce', infer_datetime_format=True, utc=True)
    filtered_df['_parsed_dt'] = parsed

    nat_count = parsed.isna().sum()
    if verbose:
        print(f"Parsen abgeschlossen: {nat_count} ungültige Datumswerte (von {len(parsed)})")

    filtered_df = filtered_df.dropna(subset=['_parsed_dt'])
    if filtered_df.empty:
        print("Alle Datumswerte wurden zu NaT. Prüfe das Format der Datums-Spalte.")
        return None

    filtered_df = filtered_df.sort_values('_parsed_dt')
    time_series = filtered_df['_parsed_dt'].dt.date.value_counts().sort_index()

    if time_series.empty:
        print("Zeitreihe ist leer nach Aggregation.")
        return None

    if verbose:
        print(time_series.head(10))

    # Plot erstellen
    plt.figure(figsize=(12,6))
    plt.plot(time_series.index, time_series.values, marker='o', linestyle='-')
    plt.title(f"Häufigkeit von '{format_name}'-Dateien über die Zeit (Spalte: {use_column})")
    plt.xlabel("Datum")
    plt.ylabel("Anzahl Dateien")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{use_column}_{format_name}_counts.png")
        plt.savefig(output_path)
        if verbose:
            print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()

    return
