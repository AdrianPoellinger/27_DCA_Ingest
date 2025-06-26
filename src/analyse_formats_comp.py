import pandas as pd
import matplotlib.pyplot as plt


# Konfigurierbare Ausschlussliste
deaktivierte_formate = {
    "Windows Bitmap",
    "JPEG File Interchange Format",
    "Tagged Image File Format",
    "ZIP Format",
    "Acrobat PDF 1.3 - Portable Document Format",
    "Acrobat PDF 1.4 - Portable Document Format",
    "Acrobat PDF 1.6 - Portable Document Format"
}

# Pfade zu den beiden CSV-Dateien
csv_path1 = "/home/jovyan/work/dca-metadataraw/WeingutGantenbein/P_156_2005_Flaesch_Neubau-Erweiterung-Weingut-Gantenbein/CAD_results/analysis_result.csv"
csv_path2 = "/home/jovyan/work/dca-metadataraw/WeingutGantenbein/gramazio-kohler-archiv-server/036_WeingutGantenbein/03_Plaene_results/analysis_result.csv"

# CSV-Dateien einlesen
df1 = pd.read_csv(csv_path1)
df2 = pd.read_csv(csv_path2)

# Spalte 'LAST_MODIFIED' in datetime umwandeln
df1['LAST_MODIFIED'] = pd.to_datetime(df1['LAST_MODIFIED'], errors='coerce')
df2['LAST_MODIFIED'] = pd.to_datetime(df2['LAST_MODIFIED'], errors='coerce')

# Ungültige Datumswerte entfernen
df1 = df1.dropna(subset=['LAST_MODIFIED'])
df2 = df2.dropna(subset=['LAST_MODIFIED'])

# Zeitraum filtern: nur Daten von 2004 bis 2009
df1 = df1[(df1['LAST_MODIFIED'].dt.year >= 2006) & (df1['LAST_MODIFIED'].dt.year <= 2006)]
df2 = df2[(df2['LAST_MODIFIED'].dt.year >= 2006) & (df2['LAST_MODIFIED'].dt.year <= 2006)]

# Optional: Formate ausschließen
df1 = df1[~df1['FORMAT_NAME'].isin(deaktivierte_formate)]
df2 = df2[~df2['FORMAT_NAME'].isin(deaktivierte_formate)]

# Die 10 häufigsten Formate in beiden Dateien ermitteln
top_formats1 = df1['FORMAT_NAME'].value_counts().nlargest(5).index
top_formats2 = df2['FORMAT_NAME'].value_counts().nlargest(5).index

# Plot vorbereiten
plt.figure(figsize=(14, 7))

# Farben für Datei 1 (Blau-Schattierung)
#colors1 = plt.cm.Blues_r(range(50, 50 + 20 * len(top_formats1), 20))
pastel2 = plt.get_cmap("Pastel2")

# Farben für Datei 2 (Rot-Schattierung)
#colors2 = plt.cm.Reds_r(range(50, 50 + 20 * len(top_formats2), 20))
dark2 = plt.get_cmap("Dark2")


# Farben für Datei 1
colors1 = [pastel2(i / len(top_formats1)) for i in range(len(top_formats1))]

# Farben für Datei 2
colors2 = [dark2(i / len(top_formats2)) for i in range(len(top_formats2))]


# Plot für Datei 1
for i, format_name in enumerate(top_formats1):
    format_df = df1[df1['FORMAT_NAME'] == format_name].copy()
    format_df = format_df.sort_values('LAST_MODIFIED')
    time_series = format_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()
    plt.plot(time_series.index, time_series.values, marker='o', linestyle='-', label=f"{format_name} (Datei 1)", color=colors1[i])

# Plot für Datei 2
for i, format_name in enumerate(top_formats2):
    format_df = df2[df2['FORMAT_NAME'] == format_name].copy()
    format_df = format_df.sort_values('LAST_MODIFIED')
    time_series = format_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()
    plt.plot(time_series.index, time_series.values, marker='s', linestyle='--', label=f"{format_name} (Datei 2)", color=colors2[i])

# Diagramm formatieren
plt.title("Top 10 häufigste Formate (2004–2009) aus zwei CSV-Dateien (ausgewählte Formate deaktiviert)")
plt.xlabel("Datum")
plt.ylabel("Anzahl Dateien")
plt.xticks(rotation=45)
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig("vergleich_top10_formats_bereinigt.png")
plt.show()
