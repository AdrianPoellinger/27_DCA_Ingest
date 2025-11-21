import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

def analyse_format_last_modified(csv_path, format_name, output_dir=None, show_plot=True):
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Zeilen mit dem gewünschten Format filtern
    filtered_df = df[df['FORMAT_NAME'] == format_name].copy()

    # Spalte 'LAST_MODIFIED' in datetime umwandeln
    filtered_df['LAST_MODIFIED'] = pd.to_datetime(filtered_df['LAST_MODIFIED'], errors='coerce')

    # Ungültige Datumswerte entfernen
    filtered_df = filtered_df.dropna(subset=['LAST_MODIFIED'])

    # Nach Datum sortieren
    filtered_df = filtered_df.sort_values('LAST_MODIFIED')

    # Gruppieren nach Datum und zählen
    time_series = filtered_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()

    # Plot erstellen
    plt.figure(figsize=(12, 6))
    plt.plot(time_series.index, time_series.values, marker='o', linestyle='-')
    plt.title(f"Häufigkeit von {format_name}-Dateien über die Zeit")
    plt.xlabel("Datum")
    plt.ylabel("Anzahl Dateien")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{format_name.lower()}_time_series.png")
        plt.savefig(output_path)
        print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analysiere die zeitliche Verteilung eines bestimmten Dateiformats.")
    parser.add_argument("--input", required=True, help="Pfad zur CSV-Datei")
    parser.add_argument("--format", required=True, help="Name des zu analysierenden Formats (z. B. 'VectorWorks')")
    parser.add_argument("--output", help="Verzeichnis zum Speichern des Plots")
    parser.add_argument("--no-show", action="store_true", help="Plot nicht anzeigen")

    args = parser.parse_args()
    analyse_format_last_modified(args.input, args.format, args.output, not args.no_show)
