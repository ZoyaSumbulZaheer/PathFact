
import json
import random
import csv
from pathlib import Path
from collections import defaultdict
from huggingface_hub import HfApi

# -----------------------------
# Configuration
# -----------------------------
REPO_ID = "sofieneb/uni2h_features"
REPORTS_FILE = Path("reports/tcga_reports_splits.json")

OUTPUT_DIR = Path("tcga_subset")
MANIFEST_FILE = OUTPUT_DIR / "tcga_manifest.csv"

TRAIN_TARGET = 400
VAL_TARGET = 50
TEST_TARGET = 50

SEED = 42

# -----------------------------
# Load report splits
# -----------------------------
with open(REPORTS_FILE, "r", encoding="utf-8") as f:
    splits = json.load(f)

api = HfApi()

print("Reading Hugging Face feature file list...")
repo_files = api.list_repo_files(
    repo_id=REPO_ID,
    repo_type="dataset"
)

# Map full filenames to repository paths
feature_paths = {
    Path(file).name: file
    for file in repo_files
    if file.endswith(".h5")
}

# -----------------------------
# Stratified sampling
# -----------------------------
random.seed(SEED)

targets = {
    "train": TRAIN_TARGET,
    "val": VAL_TARGET,
    "test": TEST_TARGET
}

selected_records = []

for split_name, target in targets.items():

    cancer_groups = defaultdict(list)

    for record in splits[split_name]:

        filename = record["filename"]

        if filename in feature_paths:
            cancer_groups[record["cancer_type"]].append(record)

    # Randomly select proportionally across cancer types
    total_available = sum(len(v) for v in cancer_groups.values())

    selected = []

    if total_available < target:
        raise ValueError(
            f"Only {total_available} matched records in {split_name}"
        )

    allocations = {
        cancer: int(target * len(records) / total_available)
        for cancer, records in cancer_groups.items()
    }

    # Distribute remaining slots
    remaining = target - sum(allocations.values())

    fractions = sorted(
        cancer_groups,
        key=lambda c: (
            target * len(cancer_groups[c]) / total_available
            - allocations[c]
        ),
        reverse=True
    )

    for cancer in fractions[:remaining]:
        allocations[cancer] += 1

    for cancer, records in cancer_groups.items():
        count = allocations[cancer]
        selected.extend(random.sample(records, count))

    for record in selected:
        selected_records.append({
            "id": record["id"],
            "filename": record["filename"],
            "cancer_type": record["cancer_type"],
            "split": split_name,
            "repo_path": feature_paths[record["filename"]]
        })

    print(
        f"{split_name}: selected {len(selected)} "
        f"from {total_available} available records"
    )

# -----------------------------
# Save manifest
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(MANIFEST_FILE, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "filename",
            "cancer_type",
            "split",
            "repo_path"
        ]
    )

    writer.writeheader()
    writer.writerows(selected_records)

print("\nManifest created successfully!")
print("Total selected:", len(selected_records))
print("Manifest:", MANIFEST_FILE.resolve())
