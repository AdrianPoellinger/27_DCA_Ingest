
import pandas as pd

# CSV-Dateien laden
df1 = pd.read_csv("/home/jovyan/work/dca-metadataraw/WeingutGantenbein/P_156_2005_Flaesch_Neubau-Erweiterung-Weingut-Gantenbein/CAD_results/analysis_result.csv")
df2 = pd.read_csv("/home/jovyan/work/dca-metadataraw/WeingutGantenbein/gramazio-kohler-archiv-server/036_WeingutGantenbein/03_Plaene_results/analysis_result.csv")

# 1. Vergleich nach "NAME"
gemeinsame_namen = pd.merge(df1, df2, on='NAME', how='inner', suffixes=('_df1', '_df2'))

# 2. Vergleich nach "NAME" und "SIZE"
gemeinsame_name_size = pd.merge(df1, df2, on=['NAME', 'SIZE'], how='inner', suffixes=('_df1', '_df2'))

# Ergebnisse anzeigen
#print("Übereinstimmungen nach NAME:")
#print(gemeinsame_namen)

#print("\nÜbereinstimmungen nach NAME und SIZE:")
#print(gemeinsame_name_size)
