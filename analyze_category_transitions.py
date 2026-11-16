
import pandas as pd
from pathlib import Path

INPUT = Path("pathfact/outputs/manual_review_80_consolidated.csv")
OUT = Path("pathfact/outputs")

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")

    df = pd.read_csv(INPUT)

    required = [
        "consolidated_error_category",
        "A_label",
        "B_label"
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.dropna(subset=required).copy()

    df["transition"] = (
        df["A_label"].astype(str).str.strip()
        + " -> "
        + df["B_label"].astype(str).str.strip()
    )

    # Count transitions within each consolidated category
    counts = pd.crosstab(
        df["consolidated_error_category"],
        df["transition"]
    )

    counts["TOTAL"] = counts.sum(axis=1)

    # Calculate percentages within each category
    percentages = pd.crosstab(
        df["consolidated_error_category"],
        df["transition"],
        normalize="index"
    ) * 100

    percentages = percentages.round(2)
    percentages["TOTAL"] = 100.0

    # Overall transition frequencies
    overall = df["transition"].value_counts()

    # Save outputs
    counts.to_csv(
        OUT / "category_by_transition_counts.csv",
        encoding="utf-8-sig"
    )

    percentages.to_csv(
        OUT / "category_by_transition_row_percent.csv",
        encoding="utf-8-sig"
    )

    overall.to_csv(
        OUT / "overall_transition_counts.csv",
        header=["count"],
        encoding="utf-8-sig"
    )

    # Print results
    print("\nINPUT SUMMARY")
    print("Records analyzed:", len(df))
    print("Unique cases:", df["case_id"].nunique())

    print("\nCATEGORY BY TRANSITION (COUNTS)")
    print(counts.to_string())

    print("\nCATEGORY BY TRANSITION (ROW PERCENTAGES)")
    print(percentages.to_string())

    print("\nOVERALL TRANSITION COUNTS")
    print(overall.to_string())

    print("\nCreated:")
    print(OUT / "category_by_transition_counts.csv")
    print(OUT / "category_by_transition_row_percent.csv")
    print(OUT / "overall_transition_counts.csv")


if __name__ == "__main__":
    main()
