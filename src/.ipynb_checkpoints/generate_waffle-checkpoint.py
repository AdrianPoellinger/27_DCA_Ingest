import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle
import os

def generate_waffle_chart(csv_path, output_dir=None, start_year=2004, end_year=2009, show_plot=True):
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df['LAST_MODIFIED'] = pd.to_datetime(df['LAST_MODIFIED'], errors='coerce')
    df = df.dropna(subset=['LAST_MODIFIED'])

    # Zeitraum filtern
    df = df[(df['LAST_MODIFIED'].dt.year >= start_year) & (df['LAST_MODIFIED'].dt.year <= end_year)]

    # Top 10 Dateiformate
    top_formats = df['FORMAT_NAME'].value_counts().nlargest(10).index
    df = df[df['FORMAT_NAME'].isin(top_formats)]

    # Monat extrahieren
    df['MONTH'] = df['LAST_MODIFIED'].dt.to_period('M').astype(str)

    # Aggregieren
    df_agg = df.groupby(['MONTH', 'FORMAT_NAME']).size().reset_index(name='size')

    # Farben aus Set3
    unique_formats = sorted(df_agg['FORMAT_NAME'].unique())
    cmap = plt.get_cmap('Set3')
    colors = [cmap(i % cmap.N) for i in range(len(unique_formats))]
    format_color_map = dict(zip(unique_formats, colors))

    # Maximalwert für gleichmäßige Waffelgröße
    max_month_value = df_agg.groupby('MONTH')['size'].sum().max()

    # Plot vorbereiten
    months = sorted(df_agg['MONTH'].unique())
    ncols = len(months)
    fig, axs = plt.subplots(ncols=ncols, figsize=(2.5 * ncols, 10), constrained_layout=True)

    if ncols == 1:
        axs = [axs]

    for month, ax in zip(months, axs):
        month_data = df_agg[df_agg['MONTH'] == month]
        values = month_data.groupby('FORMAT_NAME')['size'].sum().sort_values(ascending=False).to_dict()
        values_list = list(values.values())
        values_list.append(max_month_value - sum(values_list))  # Rest auffüllen
        color_list = [format_color_map[k] for k in values.keys()] + ['white']

        Waffle.make_waffle(
            ax=ax,
            rows=20,
            columns=20,
            values=values_list,
            colors=color_list,
            vertical=True,
            block_aspect_ratio=1
        )

        ax.text(x=0.1, y=-0.04, s=month, fontsize=12, ha="center")

    # Beschriftung am rechten Rand
    label_params = dict(
        x=1.05,
        size=12,
        transform=axs[-1].transAxes,
        clip_on=False,
    )
    for i, fmt in enumerate(unique_formats):
        y_pos = 0.95 - i * 0.05
        axs[-1].text(y=y_pos, s=fmt, color=format_color_map[fmt], **label_params)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"waffle_files_per_month_{start_year}_{end_year}.png")
        plt.savefig(output_path)
        print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()
