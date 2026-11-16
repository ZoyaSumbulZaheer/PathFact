
import csv
from pathlib import Path
from huggingface_hub import hf_hub_download

# Hugging Face dataset
REPO_ID = "sofieneb/uni2h_features"

# Manifest created in Step 1
MANIFEST = Path("tcga_subset/tcga_manifest.csv")

# Download destination
DOWNLOAD_DIR = Path("tcga_subset/features")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Read selected files
with open(MANIFEST, "r", encoding="utf-8") as f:
    records = list(csv.DictReader(f))

total = len(records)
successful = 0
failed = []

print(f"Starting download of {total} feature files...\n")

for i, record in enumerate(records, start=1):

    repo_path = record["repo_path"]

    try:
        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=repo_path,
            repo_type="dataset",
            local_dir=str(DOWNLOAD_DIR)
        )

        successful += 1

        print(f"[{i}/{total}] Downloaded: {record['filename']}")

    except Exception as e:
        failed.append((repo_path, str(e)))
        print(f"[{i}/{total}] FAILED: {repo_path}")
        print("Error:", e)

print("\n========== DOWNLOAD SUMMARY ==========")
print("Total files:", total)
print("Successfully downloaded:", successful)
print("Failed downloads:", len(failed))

if failed:
    with open("tcga_subset/failed_downloads.txt", "w", encoding="utf-8") as f:
        for path, error in failed:
            f.write(f"{path}\n{error}\n\n")

    print("Failed download details saved.")
