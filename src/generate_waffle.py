import os
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle
import matplotlib.font_manager as fm

# Lade Schriftarten relativ zum Skript-Ordner (robuster als harte "../src/..." Pfade)
HERE = os.path.dirname(__file__)
lightfont_path = os.path.join(HERE, "Roboto-Light.ttf")
regularfont_path = os.path.join(HERE, "Roboto-Regular.ttf")
italicfont_path = os.path.join(HERE, "Roboto-BlackItalic.ttf")

# Fallback: falls die Dateien nicht vorhanden sind, benutze die Default-FontProperties
def _font_prop(path):
    if os.path.exists(path):
        return fm.FontProperties(fname=path)
    return fm.FontProperties()  # default system font

lightfont = _font_prop(lightfont_path)
regularfont = _font_prop(regularfont_path)
italicfont = _font_prop(italicfont_path)


def generate_waffle_chart(
    csv_path: Optional[str] = None,
    df: Optional[pd.DataFrame] = None,
    output_dir: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    top_n: int = 10,
    show_plot: bool = True,
    date_col: str = "creation_iso",
):
    """
    Erzeuge Waffle-Charts pro Monat basierend auf einer Datums-Spalte (standard: 'creation_iso').

    Parameter:
    - csv_path: Pfad zur CSV-Datei (wird nur benutzt, falls df nicht übergeben wird).
    - df: Optional bereits geladener DataFrame (falls übergeben, wird csv_path ignoriert).
    - output_dir: Optionales Verzeichnis zum Speichern des PNG.
    - start_year, end_year: Wenn None, aus den Daten berechnet.
    - top_n: Anzahl der Top-Formate (FORMAT_NAME), die angezeigt werden.
    - show_plot: True -> plt.show() aufrufen.
    - date_col: Name der Datums-Spalte in df (z.B. "creation_iso" oder "LAST_MODIFIED").
    """
    # Lade DataFrame falls nötig
    if df is None:
        if not csv_path:
            raise ValueError("csv_path oder df müssen angegeben werden.")
        if not os.path.exists(csv_path):
            print(f"Datei nicht gefunden: {csv_path}")
            return
        df = pd.read_csv(csv_path)

    if date_col not in df.columns:
        # Fallback auf alte Spalte falls vorhanden
        if "LAST_MODIFIED" in df.columns:
            print(f"Warnung: '{date_col}' nicht gefunden — verwende 'LAST_MODIFIED' als Fallback.")
            date_col = "LAST_MODIFIED"
        else:
            print(f"Fehler: Datums-Spalte '{date_col}' nicht in DataFrame vorhanden.")
            return

    # Konvertiere Datumsspalte
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    if df.empty:
        print("Keine gültigen Datumsangaben in der ausgewählten Spalte gefunden.")
        return

    # Bestimme Zeitraum wenn nicht gegeben
    if start_year is None:
        start_year = int(df[date_col].dt.year.min())
    if end_year is None:
        end_year = int(df[date_col].dt.year.max())

    # Filter nach Jahr
    df = df[(df[date_col].dt.year >= start_year) & (df[date_col].dt.year <= end_year)]
    if df.empty:
        print(f"Keine Daten im Zeitraum {start_year}-{end_year}.")
        return

    # Top N Formate und Aggregation pro Monat
    if "FORMAT_NAME" not in df.columns:
        print("Fehler: Spalte 'FORMAT_NAME' fehlt im DataFrame.")
        return

    top_formats = df["FORMAT_NAME"].value_counts().nlargest(top_n).index
    df = df[df["FORMAT_NAME"].isin(top_formats)]
    df["MONTH"] = df[date_col].dt.to_period("M").astype(str)
    df_agg = df.groupby(["MONTH", "FORMAT_NAME"]).size().reset_index(name="size")

    unique_formats = sorted(df_agg["FORMAT_NAME"].unique())
    cmap = plt.get_cmap("YlGnBu")
    colors = [cmap(i / (len(unique_formats) + 1)) for i in range(len(unique_formats))] + ["#111111"]
    format_color_map = dict(zip(unique_formats, colors[:-1]))

    max_month_value = df_agg.groupby("MONTH")["size"].sum().max()
    months = sorted(df_agg["MONTH"].unique())
    ncols = len(months)

    # Falls sehr viele Monate vorhanden sind, begrenze die Breite pro Chart (optional)
    fig, axs = plt.subplots(ncols=ncols, figsize=(2.5 * ncols, 10), constrained_layout=True)
    fig.patch.set_facecolor("#111111")
    if ncols == 1:
        axs = [axs]

    for ax in axs:
        ax.set_facecolor("#111111")

    for month, ax in zip(months, axs):
        month_data = df_agg[df_agg["MONTH"] == month]
        values = (
            month_data.groupby("FORMAT_NAME")["size"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )
        values_list = list(values.values())
        # Rest-Kästchen mit Hintergrundfarbe hinzufügen, damit alle Charts gleich groß sind
        values_list.append(max_month_value - sum(values_list))
        color_list = [format_color_map[k] for k in values.keys()] + ["#111111"]

        # Erzeuge Waffle. pywaffle kann je nach Version unterschiedliche API haben,
        # deshalb verwenden wir die class-basierte Erstellung via Waffle(...) falls make_waffle nicht existiert.
        try:
            Waffle.make_waffle(
                ax=ax,
                rows=50,
                columns=10,
                values=values_list,
                vertical=True,
                colors=color_list,
                block_aspect_ratio=1,
            )
        except Exception:
            # Alternative Konstruktion
            waffle = Waffle(
                rows=50,
                columns=10,
                values=values_list,
                vertical=True,
                colors=color_list,
                block_aspect_ratio=1,
            )
            waffle.plot(ax=ax)

        ax.text(
            x=0.1,
            y=-0.04,
            s=month,
            fontsize=14,
            ha="center",
            fontproperties=lightfont,
            color="#dddddd",
        )
        ax.text(
            x=0.03,
            y=sum(values_list[:-1]) / max_month_value + 0.03,
            s=f"{sum(values_list[:-1])}",
            fontsize=15,
            ha="center",
            fontproperties=italicfont,
            color="#dddddd",
        )

    # Formatnamen als Legende / Labels am rechten Rand
    label_positions = {fmt: (0.1, 0.1 - i * 0.07) for i, fmt in enumerate(unique_formats)}
    for fmt, (x, y) in label_positions.items():
        fig.text(x, y, fmt, color=format_color_map[fmt], fontproperties=regularfont, size=14)

    # Titel
    fig.text(
        x=0,
        y=1,
        s=f"Number of files modified per month ({start_year}-{end_year})",
        size=30,
        fontproperties=lightfont,
        va="bottom",
        color="#dddddd",
    )

    # Quellenangabe
    source_params = dict(ha="right", fontproperties=lightfont, color="#888888", size=10)
    fig.text(
        x=1,
        y=-0.05,
        s="Data Source: Your CSV, Viz: Inspired by python-graph-gallery.com",
        va="top",
        **source_params,
    )

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(
            output_dir, f"waffle_files_per_month_{start_year}_{end_year}.png"
        )
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Plot gespeichert unter: {output_path}")

    if show_plot:
        plt.show()