
import pandas as pd
import matplotlib.pyplot as plt
import os

# Pfad zur CSV-Datei – bitte ggf. anpassen
csv_path = "/home/jovyan/work/dca-metadataraw/WeingutGantenbein/P_156_2005_Flaesch_Neubau-Erweiterung-Weingut-Gantenbein/CAD_results/analysis_result.csv"

# Prüfen, ob die Datei existiert
if not os.path.exists(csv_path):
    print(f"Datei nicht gefunden: {csv_path}")
else:
    # CSV-Datei einlesen
    df = pd.read_csv(csv_path)

    # Anzahl der Zeilen pro Format zählen
    format_counts = df['FORMAT_NAME'].value_counts()

    # Balkendiagramm erstellen
    plt.figure(figsize=(12, 6))
    format_counts.plot(kind='bar', color='skyblue')
    plt.title('Anzahl der Dateien pro Format')
    plt.xlabel('Format Name')
    plt.ylabel('Anzahl der Dateien')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
