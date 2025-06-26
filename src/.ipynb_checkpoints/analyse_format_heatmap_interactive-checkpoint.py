import pandas as pd
import plotly.express as px
import os

def generate_interactive_heatmap(csv_path, output_dir=None, start_year=2004, end_year=2009, top_n=10):
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Spalte 'LAST_MODIFIED' in datetime umwandeln
    df['LAST_MODIFIED'] = pd.to_datetime(df['LAST_MODIFIED'], errors='coerce')
    df = df.dropna(subset=['LAST_MODIFIED'])

    # Zeitraum filtern
    df = df[(df['LAST_MODIFIED'].dt.year >= start_year) & (df['LAST_MODIFIED'].dt.year <= end_year)]

    # Die top_n häufigsten Formate ermitteln
    top_formats = df['FORMAT_NAME'].value_counts().nlargest(top_n).index
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
        title=f"Interaktive Heatmap der {top_n} häufigsten Formate ({start_year}–{end_year}) nach Monat",
        xaxis_title="Monat",
        yaxis_title="Format"
    )

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"interactive_heatmap_top{top_n}_{start_year}_{end_year}.html")
        fig.write_html(output_path)
        print(f"Interaktive Heatmap gespeichert unter: {output_path}")

    fig.show()
