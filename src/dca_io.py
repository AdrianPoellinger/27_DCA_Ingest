"""dca_io.py — Gemeinsame Lade- und Analysefunktionen für DROID-CSV-Dateien.

Wird von Analyse-Notebooks importiert, um die CSV-Ladelogik zu zentralisieren.
DROID-CSV-Dateien haben variable Spaltenbreite (FORMAT_COUNT > 1 erzeugt extra
Felder), weshalb csv.DictReader statt pd.read_csv verwendet wird.

Verwendung:
    from dca_io import load_droid_csv_auto, analyze_droid_data
    droid_df = load_droid_csv_auto("/pfad/zu/droid.csv")
    analysis  = analyze_droid_data(droid_df)
"""

import csv
import os
from typing import Dict, Optional

import pandas as pd

# ── Dateityp-Definitionen ─────────────────────────────────────────────────────
IMG_EXTENSIONS = {
    "jpg", "jpeg", "tif", "tiff", "png", "gif", "bmp", "webp",
    "dng", "cr2", "cr3", "nef", "arw", "orf", "rw2",
}
ADOBE_EXTENSIONS = {"psd", "psb", "ai", "indd", "idml", "eps", "pdf"}
CAD_EXTENSIONS   = {"dwg", "dxf", "step", "stp", "iges", "igs", "ifc", "3dm", "skp"}
TARGET_EXTENSIONS = IMG_EXTENSIONS | ADOBE_EXTENSIONS | CAD_EXTENSIONS


# ── CSV laden ─────────────────────────────────────────────────────────────────
def load_droid_csv(csv_path: str, encoding: str = "utf-8") -> pd.DataFrame:
    """Lädt eine DROID-CSV-Datei mit csv.DictReader.

    DROID fügt bei FORMAT_COUNT > 1 zusätzliche Spalten an (PUID, MIME_TYPE,
    FORMAT_NAME, FORMAT_VERSION wiederholt). DictReader sammelt diese Extras
    unter key=None (restkey); sie werden hier verworfen — der primäre
    Format-Match bleibt erhalten.
    """
    rows = []
    extra_format_rows = 0
    with open(csv_path, newline="", encoding=encoding) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if None in row:
                extra_format_rows += 1
                del row[None]
            rows.append(row)
    df = pd.DataFrame(rows)
    for col in ["ID", "PARENT_ID", "SIZE", "FORMAT_COUNT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if extra_format_rows:
        print(
            f"⚠  {extra_format_rows:,} Zeilen mit FORMAT_COUNT > 1 "
            f"(zusätzliche Format-Felder verworfen, primärer Match behalten)"
        )
    return df


def load_droid_csv_auto(csv_path: str) -> pd.DataFrame:
    """Lädt eine DROID-CSV mit automatischem Encoding-Fallback (utf-8 → latin-1)."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV nicht gefunden: {csv_path}")
    try:
        return load_droid_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        print("⚠  UTF-8 fehlgeschlagen, versuche latin-1 …")
        return load_droid_csv(csv_path, encoding="latin-1")


# ── Datenanalyse ──────────────────────────────────────────────────────────────
def analyze_droid_data(df: pd.DataFrame) -> Dict:
    """Gibt eine Kennzahlen-Übersicht eines DROID-DataFrame zurück."""
    if df.empty:
        return {}

    analysis: Dict = {}

    if "EXT" in df.columns:
        ext_lower = df["EXT"].str.lower()
        analysis["extensions"]   = df["EXT"].value_counts().head(20).to_dict()
        analysis["target_files"] = int(ext_lower.isin(TARGET_EXTENSIONS).sum())
        analysis["total_files"]  = len(df)

    md5_col = next(
        (c for c in ["MD5_HASH", "HASH", "md5", "MD5"] if c in df.columns), None
    )
    analysis["md5_column"] = md5_col
    if md5_col:
        analysis["md5_available"] = int(df[md5_col].notna().sum())
        analysis["md5_missing"]   = int(df[md5_col].isna().sum())
    else:
        analysis["md5_available"] = 0
        analysis["md5_missing"]   = len(df)

    if "SIZE" in df.columns:
        total = df["SIZE"].fillna(0).sum()
        analysis["total_size_gb"] = float(total / 1024**3)
        analysis["avg_size_mb"]   = float(df["SIZE"].fillna(0).mean() / 1024**2)

    if "FORMAT_NAME" in df.columns:
        analysis["top_formats"] = df["FORMAT_NAME"].value_counts().head(10).to_dict()

    return analysis
