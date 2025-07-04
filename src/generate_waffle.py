import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle
import matplotlib.font_manager as fm
import os

# Schriftarten lokal laden
lightfont = fm.FontProperties(fname="../src/Roboto-Light.ttf")
regularfont = fm.FontProperties(fname="../src/Roboto-Regular.ttf")
italicfont = fm.FontProperties(fname="../src/Roboto-BlackItalic.ttf")

def generate_waffle_chart(csv_path, output_dir=None, start_year=2004, end_year=2009, top_n=10, show_plot=True):
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df['LAST_MODIFIED'] = pd.to_datetime(df['LAST_MODIFIED'], errors='coerce')
    df = df.dropna(subset=['LAST_MODIFIED'])
    df = df[(df['LAST_MODIFIED'].dt.year >= start_year) & (df['LAST_MODIFIED'].dt.year <= end_year)]

    top_formats = df['FORMAT_NAME'].value_counts().nlargest(top_n).index
    df = df[df['FORMAT_NAME'].isin(top_formats)]
    df['MONTH'] = df['LAST_MODIFIED'].dt.to_period('M').astype(str)
    df_agg = df.groupby(['MONTH', 'FORMAT_NAME']).size().reset_index(name='size')

    unique_formats = sorted(df_agg['FORMAT_NAME'].unique())
    cmap = plt.get_cmap('YlGnBu')
    colors = [cmap(i / (len(unique_formats) + 1)) for i in range(len(unique_formats))] + ['#111111']
    format_color_map = dict(zip(unique_formats, colors[:-1]))

    max_month_value = df_agg.groupby('MONTH')['size'].sum().max()
    months = sorted(df_agg['MONTH'].unique())
    ncols = len(months)

    fig, axs = plt.subplots(ncols=ncols, figsize=(2.5 * ncols, 10), constrained_layout=True)
    fig.patch.set_facecolor("#111111")
    if ncols == 1:
        axs = [axs]

    for ax in axs:
        ax.set_facecolor("#111111")


    for month, ax in zip(months, axs):
        month_data = df_agg[df_agg['MONTH'] == month]
        values = month_data.groupby('FORMAT_NAME')['size'].sum().sort_values(ascending=False).to_dict()
        values_list = list(values.values())
        values_list.append(max_month_value - sum(values_list))
        color_list = [format_color_map[k] for k in values.keys()] + ['#111111']

        Waffle.make_waffle(
            ax=ax,
            rows=50,
            columns=10,
            values=values_list,
            vertical=True,
            colors=color_list,
            block_aspect_ratio=1
        )

        ax.text(x=0.1, y=-0.04, s=month, fontsize=14, ha="center", fontproperties=lightfont, color="#dddddd")
        ax.text(
            x=0.03,
            y=sum(values_list[:-1]) / max_month_value + 0.03,
            s=f"{sum(values_list[:-1])}",
            fontsize=15,
            ha="center",
            fontproperties=italicfont,
            color="#dddddd"
        )

    # Formatnamen
    label_positions = {
        fmt: (0.9, 0.9 - i * 0.07) for i, fmt in enumerate(unique_formats)
    }
    for fmt, (x, y) in label_positions.items():
        fig.text(x, y, fmt, color=format_color_map[fmt], fontproperties=regularfont, size=14)

    # Titel
    fig.text(x=0, y=1, s="Number of files modified per month", size=30, fontproperties=lightfont, va="bottom", color="#dddddd")

    # Quellenangabe
    source_params = dict(ha="right", fontproperties=lightfont, color="#888888", size=10)
    fig.text(x=1, y=-0.05, s="Data Source: Your CSV, Viz: Inspired by python-graph-gallery.com", va="top", **source_params)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"waffle_files_per_month_{start_year}_{end_year}.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()
