import pandas as pd
import plotly.express as px

# Pfad zur CSV-Datei (bitte anpassen)
csv_path = "/home/jovyan/work/dca-metadataraw/WeingutGantenbein/P_156_2005_Flaesch_Neubau-Erweiterung-Weingut-Gantenbein/CAD_results/analysis_result.csv"

# CSV-Datei einlesen
df = pd.read_csv(csv_path)

# Spalte 'LAST_MODIFIED' in datetime umwandeln
df['LAST_MODIFIED'] = pd.to_datetime(df['LAST_MODIFIED'], errors='coerce')
df = df.dropna(subset=['LAST_MODIFIED'])

# Zeitraum filtern: nur Daten von 2004 bis 2009
df = df[(df['LAST_MODIFIED'].dt.year >= 2004) & (df['LAST_MODIFIED'].dt.year <= 2009)]

# Die 10 häufigsten Formate ermitteln
top_formats = df['FORMAT_NAME'].value_counts().nlargest(10).index
df = df[df['FORMAT_NAME'].isin(top_formats)]

# Monat extrahieren
df['MONTH'] = df['LAST_MODIFIED'].dt.to_period('M').astype(str)

# Kreuztabelle erstellen
heatmap_data = pd.crosstab(df['FORMAT_NAME'], df['MONTH'])
heatmap_data = heatmap_data.reindex(sorted(heatmap_data.columns), axis=1)

# In lange Form bringen
heatmap_long = heatmap_data.reset_index().melt(id_vars='FORMAT_NAME', var_name='MONTH', value_name='COUNT')
heatmap_long['TEXT'] = heatmap_long['COUNT'].apply(lambda x: '' if x == 0 else str(x))

# Interaktive Heatmap
fig = px.imshow(
    heatmap_data.values,
    labels=dict(x="Monat", y="Format", color="Anzahl"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    text_auto=False,
    color_continuous_scale='YlGnBu'
)

# Text manuell setzen
fig.update_traces(
    text=heatmap_long['TEXT'].values.reshape(heatmap_data.shape),
    texttemplate="%{text}"
)

fig.update_layout(
    title="Interaktive Heatmap der 10 häufigsten Formate (2004–2009) nach Monat",
    xaxis_title="Monat",
    yaxis_title="Format"
)

fig.show()
