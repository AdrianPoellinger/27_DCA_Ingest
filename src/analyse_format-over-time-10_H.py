import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
plt.title("Häufigkeit der 10 häufigsten Formate (2004–2009) nach Monat")
plt.xlabel("Monat")
plt.ylabel("Format")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("../res/heatmap_top10_formats_by_month_2004_2009.png")
plt.show()

