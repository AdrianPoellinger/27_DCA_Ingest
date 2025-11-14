"""
add_creation_dates.py

Ergänzt eine DROID CSV-Datei mit Erstellungsdaten (Creation Time/Birth Time) für jede Datei.

DROID (Digital Record Object Identification) liefert das letzte Änderungsdatum (LAST_MODIFIED),
aber nicht das Erstellungsdatum. Dieses Skript liest die DROID CSV-Datei, ermittelt für jede
Datei das Erstellungsdatum und fügt eine neue Spalte 'CREATION_DATE' hinzu.

Usage:
    python add_creation_dates.py --input droid_output.csv --output enriched_output.csv
    
    oder in einem Jupyter Notebook:
    
    from add_creation_dates import add_creation_dates_to_csv
    add_creation_dates_to_csv("droid_output.csv", "enriched_output.csv")
"""

import pandas as pd
import os
import platform
from pathlib import Path
from datetime import datetime
import argparse


def get_creation_time(file_path):
    """
    Ermittelt das Erstellungsdatum einer Datei.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        tuple: (ISO 8601 formatiertes Erstellungsdatum oder None, Methode als String oder None)
               Methode kann sein: 'st_birthtime', 'st_ctime (Windows)', 'min(st_ctime, st_mtime) (Linux)'
    """
    try:
        # Überprüfe ob Datei existiert
        if not os.path.exists(file_path):
            return None, None
        
        path = Path(file_path)
        
        # Auf Windows: st_ctime ist das Erstellungsdatum
        # Auf Unix/Linux: st_ctime ist das Änderungsdatum der Metadaten
        # Auf neueren Systemen: st_birthtime (falls verfügbar)
        
        stat_info = path.stat()
        method = None
        
        # Versuche st_birthtime zu nutzen (macOS, neuere BSD-Systeme)
        if hasattr(stat_info, 'st_birthtime'):
            creation_time = stat_info.st_birthtime
            method = 'st_birthtime'
        # Windows nutzt st_ctime als Erstellungszeit
        elif platform.system() == 'Windows':
            creation_time = stat_info.st_ctime
            method = 'st_ctime (Windows)'
        else:
            # Auf Linux ist das Erstellungsdatum schwierig zu bekommen
            # st_ctime ist hier die Zeit der letzten Metadaten-Änderung
            # Wir nehmen das Minimum von ctime und mtime als best guess
            creation_time = min(stat_info.st_ctime, stat_info.st_mtime)
            method = 'min(st_ctime, st_mtime) (Linux)'
        
        # Konvertiere zu ISO 8601 Format (wie DROID es verwendet)
        dt = datetime.fromtimestamp(creation_time)
        return dt.strftime('%Y-%m-%dT%H:%M:%S'), method
        
    except Exception as e:
        # Bei Fehlern None zurückgeben
        print(f"Warnung: Konnte Erstellungsdatum für '{file_path}' nicht ermitteln: {e}")
        return None, None


def extract_file_path_from_uri(uri):
    """
    Extrahiert den Dateipfad aus einer DROID URI.
    
    DROID URIs haben das Format: file:/path/to/file oder zip:file:/path/to/archive!/file
    
    Args:
        uri (str): DROID URI
        
    Returns:
        str: Dateipfad oder None
    """
    if pd.isna(uri):
        return None
    
    # Wenn es eine ZIP-URI ist, extrahiere nur den Archiv-Pfad
    if uri.startswith('zip:'):
        # Format: zip:file:/path/to/archive!/internal/file
        # Wir interessieren uns für den Archiv-Pfad
        parts = uri.split('!')
        if len(parts) > 0:
            archive_uri = parts[0]
            # Entferne 'zip:file:' Präfix
            archive_uri = archive_uri.replace('zip:file:', '')
            # URL-Dekodierung (z.B. %20 -> Leerzeichen)
            import urllib.parse
            return urllib.parse.unquote(archive_uri)
    
    # Standard file: URI
    if uri.startswith('file:'):
        file_path = uri.replace('file:', '')
        # URL-Dekodierung
        import urllib.parse
        return urllib.parse.unquote(file_path)
    
    return None


def add_creation_dates_to_csv(input_csv, output_csv=None, file_path_column='FILE_PATH', 
                                uri_column='URI', inplace=False):
    """
    Fügt einer DROID CSV-Datei eine Spalte mit Erstellungsdaten hinzu.
    
    Args:
        input_csv (str): Pfad zur DROID CSV-Datei
        output_csv (str, optional): Pfad für die Ausgabe-CSV. Falls None, wird input_csv überschrieben wenn inplace=True
        file_path_column (str): Name der Spalte mit dem Dateipfad (Standard: 'FILE_PATH')
        uri_column (str): Name der Spalte mit der URI (Standard: 'URI')
        inplace (bool): Falls True und output_csv ist None, wird die Eingabedatei überschrieben
        
    Returns:
        pd.DataFrame: DataFrame mit hinzugefügter CREATION_DATE Spalte
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"CSV-Datei nicht gefunden: {input_csv}")
    
    print(f"Lese CSV-Datei: {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Überprüfe ob notwendige Spalten vorhanden sind
    if file_path_column not in df.columns and uri_column not in df.columns:
        raise ValueError(f"Weder '{file_path_column}' noch '{uri_column}' Spalte in CSV gefunden")
    
    # Ermittle Erstellungsdaten
    creation_dates = []
    method_stats = {}  # Track which methods were used
    total_files = len(df)
    
    print(f"Ermittle Erstellungsdaten für {total_files} Einträge...")
    
    for idx, row in df.iterrows():
        # Versuche zuerst FILE_PATH Spalte
        file_path = row.get(file_path_column, None)
        
        # Falls FILE_PATH leer oder nicht vorhanden, versuche URI zu parsen
        if pd.isna(file_path) or not file_path:
            uri = row.get(uri_column, None)
            file_path = extract_file_path_from_uri(uri)
        
        # Ermittle Erstellungsdatum
        if file_path:
            creation_date, method = get_creation_time(file_path)
            # Track method usage
            if method:
                method_stats[method] = method_stats.get(method, 0) + 1
        else:
            creation_date = None
        
        creation_dates.append(creation_date)
        
        # Fortschrittsanzeige alle 100 Einträge
        if (idx + 1) % 100 == 0:
            print(f"  Verarbeitet: {idx + 1}/{total_files}")
    
    # Füge neue Spalte hinzu
    df['CREATION_DATE'] = creation_dates
    
    # Zähle erfolgreich ermittelte Daten
    valid_dates = sum(1 for d in creation_dates if d is not None)
    print(f"Erstellungsdaten ermittelt: {valid_dates}/{total_files}")
    
    # Zeige verwendete Methoden
    if method_stats:
        print("\nVerwendete Methoden zur Ermittlung des Erstellungsdatums:")
        for method, count in sorted(method_stats.items()):
            percentage = (count / valid_dates * 100) if valid_dates > 0 else 0
            print(f"  - {method}: {count} Dateien ({percentage:.1f}%)")
    
    # Speichere Ergebnis
    if output_csv:
        output_path = output_csv
    elif inplace:
        output_path = input_csv
    else:
        # Standard: füge '_with_creation_dates' vor der Dateiendung hinzu
        base, ext = os.path.splitext(input_csv)
        output_path = f"{base}_with_creation_dates{ext}"
    
    df.to_csv(output_path, index=False)
    print(f"Angereicherte CSV gespeichert: {output_path}")
    
    return df


def main():
    """CLI Entry Point"""
    parser = argparse.ArgumentParser(
        description='Fügt Erstellungsdaten zu einer DROID CSV-Datei hinzu.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python add_creation_dates.py --input droid_results.csv
  python add_creation_dates.py --input droid_results.csv --output enriched.csv
  python add_creation_dates.py --input droid_results.csv --inplace
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='Pfad zur DROID CSV-Datei')
    parser.add_argument('--output', '-o',
                       help='Pfad für die Ausgabe-CSV (optional)')
    parser.add_argument('--inplace', action='store_true',
                       help='Überschreibe die Eingabedatei')
    parser.add_argument('--file-path-column', default='FILE_PATH',
                       help='Name der Dateipfad-Spalte (Standard: FILE_PATH)')
    parser.add_argument('--uri-column', default='URI',
                       help='Name der URI-Spalte (Standard: URI)')
    
    args = parser.parse_args()
    
    try:
        add_creation_dates_to_csv(
            input_csv=args.input,
            output_csv=args.output,
            file_path_column=args.file_path_column,
            uri_column=args.uri_column,
            inplace=args.inplace
        )
    except Exception as e:
        print(f"Fehler: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
