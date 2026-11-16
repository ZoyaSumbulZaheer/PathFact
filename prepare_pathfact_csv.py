
import json
import csv
from pathlib import Path

input_file = Path("output/tcga_wsi_caption_500/predictions.json")
output_file = Path("pathfact/data/generated_reports.csv")

output_file.parent.mkdir(parents=True, exist_ok=True)

with open(input_file, "r", encoding="utf-8") as f:
    predictions = json.load(f)

with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "case_id",
            "split",
            "generated_report",
            "reference_report"
        ]
    )

    writer.writeheader()

    for case_id, item in predictions.items():
        writer.writerow({
            "case_id": case_id,
            "split": "test",
            "generated_report": item["pred"],
            "reference_report": item["target"]
        })

print("PathFact dataset created successfully.")
print("Total records:", len(predictions))
print("Output:", output_file)
