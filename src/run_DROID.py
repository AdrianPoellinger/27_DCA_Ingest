import os
import subprocess

# Define the paths
droid_script_path = "/home/jovyan/work/27_DCA_Ingest/src/droid-binary-6.7.0-bin/droid.sh"
dataset_to_analyze = "2019_Mulgens-GDrive"
folder_to_analyze = f"/home/jovyan/work/dcaonnextcloud-500gb/DigitalMaterialCopies/TorAlva/{dataset_to_analyze}"
output_folder = f"/home/jovyan/work/dca-metadataraw/TorAlva/{dataset_to_analyze}_results_hash"
output_csv_path = f"{output_folder}/analysis_result_2.csv"

try:
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    print(f"Analyzing folder: {folder_to_analyze}")
    print(f"Output will be saved to: {output_csv_path}")

    # Run the droid script with the specified folder and output CSV file
    result = subprocess.run(subprocess.run([droid_script_path, "-R", folder_to_analyze, "-o", output_csv_path, "-Pr", "profile.generateHash=true"], check=True))

    print("DROID output:", result.stdout)
    print(f"Analysis complete. The result is saved in {output_csv_path}.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
    print("DROID error output:", e.stderr)
