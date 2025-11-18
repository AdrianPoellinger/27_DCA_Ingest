import matplotlib.pyplot as plt
import pandas as pd
import os

def analyse_format_over_creation_time_df(df, format_name, date_column="creation_iso", output_dir=None, show_plot=True, verbose=True):
    # Spaltennamen säubern
    df = df.copy()
    df.columns = df.columns.str.strip()

    if date_column not in df.columns:
        raise ValueError(f"Spalte '{date_column}' nicht in DataFrame. Verfügbare Spalten: {list(df.columns)}")

    if "FORMAT_NAME" not in df.columns:
        raise ValueError("Spalte 'FORMAT_NAME' nicht in DataFrame.")

    # Robuster Vergleich: case-insensitive, trimmed
    target = str(format_name).strip().lower()
    mask = df['FORMAT_NAME'].astype(str).str.strip().str.lower() == target
    filtered_df = df[mask].copy()

    if verbose:
        print(f"Gefilterte Zeilen für '{format_name}': {filtered_df.shape[0]}")

    if filtered_df.empty:
        print("Keine Zeilen für das gewünschte Format gefunden.")
        return None

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
    plt.title(f"Häufigkeit von {format_name}-Dateien über die Zeit")
    plt.xlabel("Datum")
    plt.ylabel("Anzahl Dateien")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "format_counts.png")
        plt.savefig(output_path)
        if verbose:
            print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()

    return time_series