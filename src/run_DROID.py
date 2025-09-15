import os
import subprocess
# Dynamisch das Home-Verzeichnis holen
home_dir = os.path.expanduser("~")
base_path = os.path.join(home_dir, "work")

# Dataset-Name
dataset_to_analyze = "2019_Mulgens-GDrive"

# Pfade definieren
droid_script_path = os.path.join(base_path, "27_DCA_Ingest/src/droid-binary-6.7.0-bin/droid.sh")
folder_to_analyze = os.path.join(base_path, f"dcaonnextcloud-500gb/DigitalMaterialCopies/TorAlva/{dataset_to_analyze}")
output_folder = os.path.join(base_path, f"dca-metadataraw/TorAlva/{dataset_to_analyze}_results_hash")
output_csv_path = os.path.join(output_folder, "analysis_result_2.csv")

try:
    # Output-Ordner erstellen (falls nicht vorhanden)
    os.makedirs(output_folder, exist_ok=True)

    print(f"Analyzing folder: {folder_to_analyze}")
    print(f"Output will be saved to: {output_csv_path}")

    # DROID-Skript ausführen
    result = subprocess.run(
        [droid_script_path, "-R", folder_to_analyze, "-o", output_csv_path, "-Pr", "profile.generateHash=true"],
        check=True,
        capture_output=True,
        text=True
    )

    print("DROID output:", result.stdout)
    print(f"Analysis complete. The result is saved in {output_csv_path}.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred while running DROID: {e}")
    print("DROID error output:", e.stderr)

except PermissionError as e:
    print(f"Permission error: {e}")
    print("Bitte prüfe, ob du Schreibrechte für den Zielordner hast.")

except FileNotFoundError as e:
    print(f"Datei oder Verzeichnis nicht gefunden: {e}")
    print("Bitte prüfe, ob alle Pfade korrekt sind und existieren.")
