import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import argparse

def generate_format_heatmap(csv_path, output_dir=None, start_year=2004, end_year=2009, top_n=10, show_plot=True):
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Spalte 'LAST_MODIFIED' in datetime umwandeln
    df['LAST_MODIFIED'] = pd.to_datetime(df['LAST_MODIFIED'], errors='coerce')

    # Ungültige Datumswerte entfernen
    df = df.dropna(subset=['LAST_MODIFIED'])

    # Zeitraum filtern
    df = df[(df['LAST_MODIFIED'].dt.year >= start_year) & (df['LAST_MODIFIED'].dt.year <= end_year)]

    # Die 10 häufigsten Formate im gefilterten Zeitraum ermitteln
    top_formats = df['FORMAT_NAME'].value_counts().nlargest(top_n).index

    # Nur Zeilen mit diesen Formaten behalten
    df = df[df['FORMAT_NAME'].isin(top_formats)]

    # Monat extrahieren im Format YYYY-MM
    df['MONTH'] = df['LAST_MODIFIED'].dt.to_period('M').astype(str)

    # Kreuztabelle: Format vs. Monat
    heatmap_data = pd.crosstab(df['FORMAT_NAME'], df['MONTH'])

    # Spalten (Monate) sortieren
    heatmap_data = heatmap_data.reindex(sorted(heatmap_data.columns), axis=1)

    # Heatmap erstellen
    plt.figure(figsize=(16, 6))
    sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='PuRd', linewidths=0.5)
    plt.title(f"Häufigkeit der {top_n} häufigsten Formate ({start_year}–{end_year}) nach Monat")
    plt.xlabel("Monat")
    plt.ylabel("Format")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"heatmap_top{top_n}_formats_by_month_{start_year}_{end_year}.png")
        plt.savefig(output_path)
        print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Erzeuge eine Heatmap der 10 häufigsten Formate nach Monat in einem bestimmten Zeitraum.")
    parser.add_argument("--input", required=True, help="Pfad zur CSV-Datei")
    parser.add_argument("--output", help="Verzeichnis zum Speichern des Plots")
    parser.add_argument("--start", type=int, default=2004, help="Startjahr (z. B. 2004)")
    parser.add_argument("--end", type=int, default=2009, help="Endjahr (z. B. 2009)")
    parser.add_argument("--no-show", action="store_true", help="Plot nicht anzeigen")

    args = parser.parse_args()
    generate_format_heatmap(args.input, args.output, args.start, args.end, not args.no_show)
