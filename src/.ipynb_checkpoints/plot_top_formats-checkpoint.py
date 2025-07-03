import pandas as pd
import matplotlib.pyplot as plt

def plot_top_formats(csv_path1, csv_path2, deaktivierte_formate=None, start_year=2004, end_year=2009, output_file="vergleich_top10_formats_bereinigt.png"):
    if deaktivierte_formate is None:
        deaktivierte_formate = {
            "Windows Bitmap",
            "JPEG File Interchange Format",
            "Tagged Image File Format"
        }
    if not os.path.exists(csv_path1 or csv_path2):
        print(f"csv Datei nicht gefunden")
        return

    df1 = pd.read_csv(csv_path1)
    df2 = pd.read_csv(csv_path2)


    # Spalte 'LAST_MODIFIED' in datetime umwandeln
    df1['LAST_MODIFIED'] = pd.to_datetime(df1['LAST_MODIFIED'], errors='coerce')
    df2['LAST_MODIFIED'] = pd.to_datetime(df2['LAST_MODIFIED'], errors='coerce')

    # Ungültige Datumswerte entfernen
    df1 = df1.dropna(subset=['LAST_MODIFIED'])
    df2 = df2.dropna(subset=['LAST_MODIFIED'])

    # Zeitraum filtern
    df1 = df1[(df1['LAST_MODIFIED'].dt.year >= start_year) & (df1['LAST_MODIFIED'].dt.year <= end_year)]
    df2 = df2[(df2['LAST_MODIFIED'].dt.year >= start_year) & (df2['LAST_MODIFIED'].dt.year <= end_year)]

    # Deaktivierte Formate ausschließen
    df1 = df1[~df1['FORMAT_NAME'].isin(deaktivierte_formate)]
    df2 = df2[~df2['FORMAT_NAME'].isin(deaktivierte_formate)]

    # Top 10 Formate
    top_formats1 = df1['FORMAT_NAME'].value_counts().nlargest(10).index
    top_formats2 = df2['FORMAT_NAME'].value_counts().nlargest(10).index

    # Plot vorbereiten
    plt.figure(figsize=(14, 7))
    colors1 = plt.cm.Blues_r(range(50, 50 + 20 * len(top_formats1), 20))
    colors2 = plt.cm.Reds_r(range(50, 50 + 20 * len(top_formats2), 20))

    for i, format_name in enumerate(top_formats1):
        format_df = df1[df1['FORMAT_NAME'] == format_name].copy()
        format_df = format_df.sort_values('LAST_MODIFIED')
        time_series = format_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()
        plt.plot(time_series.index, time_series.values, marker='o', linestyle='-', label=f"{format_name} (Datei 1)", color=colors1[i])

    for i, format_name in enumerate(top_formats2):
        format_df = df2[df2['FORMAT_NAME'] == format_name].copy()
        format_df = format_df.sort_values('LAST_MODIFIED')
        time_series = format_df['LAST_MODIFIED'].dt.date.value_counts().sort_index()
        plt.plot(time_series.index, time_series.values, marker='s', linestyle='--', label=f"{format_name} (Datei 2)", color=colors2[i])

    plt.title(f"Top 10 häufigste Formate ({start_year}–{end_year}) aus zwei Quellen (ausgewählte Formate deaktiviert)")
    plt.xlabel("Datum")
    plt.ylabel("Anzahl Dateien")
    plt.xticks(rotation=45)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()
