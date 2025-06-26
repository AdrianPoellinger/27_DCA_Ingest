import pandas as pd
import matplotlib.pyplot as plt

# Pfad zur CSV-Datei (bitte anpassen)
csv_path = "/home/jovyan/work/dca-metadataraw/WeingutGantenbein/P_156_2005_Flaesch_Neubau-Erweiterung-Weingut-Gantenbein/CAD_results/analysis_result.csv"

# CSV-Datei einlesen
df = pd.read_csv(csv_path)

# Spalte 'LAST_MODIFIED' in datetime umwandeln
df['LAST_MODIFIED'] = pd.to_datetime(df['LAST_MODIFIED'], errors='coerce')

# Ungültige Datumswerte entfernen
df = df.dropna(subset=['LAST_MODIFIED'])

# Zeitraum filtern: nur Daten von 2004 bis 2009
df = df[(df['LAST_MODIFIED'].dt.year >= 2004) & (df['LAST_MODIFIED'].dt.year <= 2009)]

# Die 10 häufigsten Formate im gefilterten Zeitraum ermitteln
top_formats = df['FORMAT_NAME'].value_counts().nlargest(10).index

# Plot vorbereiten
plt.figure(figsize=(14, 7))

# Für jedes der Top-Formate eine Zeitreihe erstellen und plotten
for format_name in top_formats:
    format_df = df[df['FORMAT_NAME'] == format_name].copy()
    format_df = format_df.sort_values('LAST_MODIFIED')
    time_series = format_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()
    plt.plot(time_series.index, time_series.values, marker='o', linestyle='-', label=format_name)

# Diagramm formatieren
plt.title("Häufigkeit der 10 häufigsten Formate (2004–2009)")
plt.xlabel("Datum")
plt.ylabel("Anzahl Dateien")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("../res/top10_formats_2004_2009.png")  # Optional: Speichern als Bild
plt.show()

