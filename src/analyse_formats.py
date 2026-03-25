# analyse_formats.py
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def analyse_formats_df(
    df: pd.DataFrame,
    output_dir: Optional[str] = None,
    show_plot: bool = True,
    format_column: str = "FORMAT_NAME",
    top_n: Optional[int] = None,
    verbose: bool = True,
) -> pd.Series:
    """Analysiere Dateiformate aus einem bereits geladenen DataFrame.

    Gibt die aggregierten Häufigkeiten als Series zurück.
    """
    data = df.copy()
    data.columns = data.columns.str.strip()

    if format_column not in data.columns:
        raise ValueError(
            f"Spalte '{format_column}' nicht in DataFrame. "
            f"Verfügbare Spalten: {list(data.columns)}"
        )

    values = data[format_column].dropna().astype(str).str.strip()
    values = values[values != ""]

    format_counts = values.value_counts()
    if top_n is not None:
        format_counts = format_counts.head(top_n)

    if verbose:
        print(f"Gefundene Formate: {len(format_counts)}")
        if not format_counts.empty:
            print(format_counts.head(10))

    if format_counts.empty:
        if verbose:
            print("Keine Formate zum Plotten gefunden.")
        return format_counts

    _plot_format_counts(format_counts, output_dir, show_plot)
    return format_counts


def _plot_format_counts(format_counts: pd.Series, output_dir: Optional[str], show_plot: bool) -> None:
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="black")
    ax.set_facecolor("black")

    set3_colors = plt.cm.Set3.colors
    bar_colors = [set3_colors[i % len(set3_colors)] for i in range(len(format_counts))]
    format_counts.plot(kind="bar", color=bar_colors, ax=ax)

    ax.set_title("Anzahl der Dateien pro Format", color="white", fontsize=10, loc="left")
    ax.set_xlabel("Format Name", color="white", fontsize=10)
    ax.set_ylabel("Anzahl der Dateien", color="white", fontsize=10)
    ax.tick_params(axis="both", colors="white", labelsize=6)
    plt.xticks(rotation=45, ha="right")

    for spine in ax.spines.values():
        spine.set_color("white")

    ax.grid(axis="y", linestyle="--", alpha=0.35, color="white")
    plt.tight_layout()
    if output_dir:
        from pathlib import Path

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = str(Path(output_dir) / "format_counts.png")
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        print(f"Plot gespeichert unter: {output_path}")
    if show_plot:
        plt.show()