import pandas as pd
import os

def compare_csv_files(path1, path2, output_dir=None, compare_by='name_size'):
    # CSV-Dateien laden
    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)

    # Vergleich nach NAME
    gemeinsame_namen = pd.merge(df1, df2, on='NAME', how='inner', suffixes=('_df1', '_df2'))

    # Vergleich nach NAME und SIZE
    gemeinsame_name_size = pd.merge(df1, df2, on=['NAME', 'SIZE'], how='inner', suffixes=('_df1', '_df2'))

    # Ergebnisse anzeigen
    #print("Übereinstimmungen nach NAME:")
    #print(gemeinsame_namen)

    #print("\nÜbereinstimmungen nach NAME und SIZE:")
    #print(gemeinsame_name_size)

    # Optional speichern
    #if output_dir:
    #    os.makedirs(output_dir, exist_ok=True)
    #    gemeinsame_namen.to_csv(os.path.join(output_dir, "gemeinsame_namen.csv"), index=False)
    #    gemeinsame_name_size.to_csv(os.path.join(output_dir, "gemeinsame_name_size.csv"), index=False)
     #   print(f"Ergebnisse gespeichert in: {output_dir}")

    return gemeinsame_namen, gemeinsame_namen_size
