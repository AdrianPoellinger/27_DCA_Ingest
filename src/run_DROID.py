import os
import subprocess

# Define the paths
droid_script_path = "/home/jovyan/work/27_DCA_Ingest/src/droid-binary-6.7.0-bin/droid.sh"
dataset_to_analyze = "gramazio-kohler-archiv-server/036_WeingutGantenbein/03_Plaene"
folder_to_analyze = f"/home/jovyan/work/dca-digitalmaterialcopies/WeingutGantenbein/{dataset_to_analyze}"
output_folder = f"/home/jovyan/work/dca-metadataraw/WeingutGantenbein/{dataset_to_analyze}_results"
output_csv_path = f"{output_folder}/analysis_result.csv"

try:
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Run the droid script with the specified folder and output CSV file
    subprocess.run([droid_script_path, "-R", folder_to_analyze, "-o", output_csv_path], check=True)
    print(f"Analysis complete. The result is saved in {output_csv_path}.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
