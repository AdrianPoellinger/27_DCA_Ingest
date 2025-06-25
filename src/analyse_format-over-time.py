import pandas as pd
import matplotlib.pyplot as plt

# Pfad zur CSV-Datei (bitte anpassen)
csv_path = "analysis_result.csv"

# CSV-Datei einlesen
df = pd.read_csv(csv_path)

# Zeilen mit FORMAT_NAME == 'VectorWorks' filtern
vectorworks_df = df[df['FORMAT_NAME'] == 'VectorWorks'].copy()

# Spalte 'LAST_MODIFIED' in datetime umwandeln
vectorworks_df['LAST_MODIFIED'] = pd.to_datetime(vectorworks_df['LAST_MODIFIED'], errors='coerce')

# Ungültige Datumswerte entfernen
vectorworks_df = vectorworks_df.dropna(subset=['LAST_MODIFIED'])

# Nach Datum sortieren
vectorworks_df = vectorworks_df.sort_values('LAST_MODIFIED')

# Gruppieren nach Datum (z. B. pro Tag) und zählen
time_series = vectorworks_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()

# Plot erstellen
plt.figure(figsize=(12, 6))
plt.plot(time_series.index, time_series.values, marker='o', linestyle='-')
plt.title("Häufigkeit von VectorWorks-Dateien über die Zeit")
plt.xlabel("Datum")
plt.ylabel("Anzahl Dateien")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("vectorworks_time_series.png")  # Optional: Speichern als Bild
plt.show()
