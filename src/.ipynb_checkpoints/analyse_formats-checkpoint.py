# analyse_formats.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

def analyse_formats(csv_path, output_dir=None, show_plot=True):
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    format_counts = df['FORMAT_NAME'].value_counts()

    plt.figure(figsize=(12, 6))
    format_counts.plot(kind='bar', color='skyblue')
    plt.title('Anzahl der Dateien pro Format')
    plt.xlabel('Format Name')
    plt.ylabel('Anzahl der Dateien')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "format_counts.png")
        plt.savefig(output_path)
        print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analysiere Dateiformate in einer CSV-Datei.")
    parser.add_argument("--input", required=True, help="Pfad zur CSV-Datei")
    parser.add_argument("--output", help="Verzeichnis zum Speichern des Plots")
    parser.add_argument("--no-show", action="store_true", help="Plot nicht anzeigen")

    args = parser.parse_args()
    analyse_formats(args.input, args.output, not args.no_show)
