import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
INPUT = BASE / "pathfact" / "outputs" / "manual_review_80.csv"
OUTPUT = BASE / "pathfact" / "outputs" / "manual_review_80_consolidated.csv"

# Consolidates the detailed researcher-review labels into six broader themes.
# The original primary_error_category column is preserved.
CATEGORY_MAP = {
    # Reference scope and evidence availability
    "Reference scope mismatch": "Reference scope and evidence availability",
    "Evidence absence vs inference": "Reference scope and evidence availability",
    "Evidence-scope overextension": "Reference scope and evidence availability",
    "Evidence absence vs contradiction": "Reference scope and evidence availability",
    "Report-content / missing evidence": "Reference scope and evidence availability",
    "Reference incompleteness": "Reference scope and evidence availability",
    "Report-content / absence claim": "Reference scope and evidence availability",
    "Anatomical evidence absence": "Reference scope and evidence availability",
    "Report-content / reference incompleteness": "Reference scope and evidence availability",
    "Report-content / ambiguous wording": "Reference scope and evidence availability",

    # Compound, incomplete, or fragmented claims
    "Incomplete / unsupported marker claim": "Compound, incomplete, or fragmented claims",
    "Incomplete / compound claim": "Compound, incomplete, or fragmented claims",
    "Compound / mixed-support claim": "Compound, incomplete, or fragmented claims",
    "Compound / incomplete claim": "Compound, incomplete, or fragmented claims",
    "Incomplete / corrupted claim": "Compound, incomplete, or fragmented claims",
    "Incomplete / staging claim": "Compound, incomplete, or fragmented claims",
    "Compound / report-metadata claim": "Compound, incomplete, or fragmented claims",
    "Incomplete / partially supported claim": "Compound, incomplete, or fragmented claims",
    "Incomplete / numerical claim": "Compound, incomplete, or fragmented claims",
    "Compound / unsupported subtype": "Compound, incomplete, or fragmented claims",
    "Compound / unsupported metastasis": "Compound, incomplete, or fragmented claims",
    "Compound / semantic ambiguity": "Compound, incomplete, or fragmented claims",

    # Anatomical, specimen, and procedural mismatches
    "Anatomical / specimen mismatch": "Anatomical, specimen, and procedural mismatches",
    "Anatomical/specimen mismatch": "Anatomical, specimen, and procedural mismatches",
    "Compound / anatomical mismatch": "Anatomical, specimen, and procedural mismatches",
    "Anatomical / margin-scope mismatch": "Anatomical, specimen, and procedural mismatches",
    "Anatomical / procedure mismatch": "Anatomical, specimen, and procedural mismatches",
    "Anatomical / diagnostic mismatch": "Anatomical, specimen, and procedural mismatches",
    "Anatomical mismatch / compound claim": "Anatomical, specimen, and procedural mismatches",
    "Anatomical contradiction": "Anatomical, specimen, and procedural mismatches",
    "Compound / specimen mismatch": "Anatomical, specimen, and procedural mismatches",

    # Numerical and measurement mismatches
    "Numerical/value mismatch": "Numerical and measurement mismatches",
    "Numerical / specimen mismatch": "Numerical and measurement mismatches",
    "Anatomical / numerical mismatch": "Numerical and measurement mismatches",

    # Semantic equivalence and terminology specificity
    "Semantic equivalence": "Semantic equivalence and terminology specificity",
    "Semantic ambiguity / unsupported detail": "Semantic equivalence and terminology specificity",
    "Semantic equivalence / procedure specificity": "Semantic equivalence and terminology specificity",

    # Clinical attribute, negation, and scope interpretation
    "Clinical attribute confusion": "Clinical attribute, negation, and scope interpretation",
    "Negation / scope ambiguity": "Clinical attribute, negation, and scope interpretation",
}

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT}. Save manual_review_80.csv in pathfact/outputs first."
        )

    df = pd.read_csv(INPUT)

    required = {"case_id", "claim_id", "primary_error_category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    df["primary_error_category"] = df["primary_error_category"].fillna("").astype(str).str.strip()
    unknown = sorted(set(df["primary_error_category"]) - set(CATEGORY_MAP))
    if unknown:
        raise ValueError(
            "These detailed categories have no consolidation mapping yet:\n- "
            + "\n- ".join(unknown)
        )

    df["consolidated_error_category"] = df["primary_error_category"].map(CATEGORY_MAP)

    if df["consolidated_error_category"].isna().any():
        raise ValueError("Some records were not assigned a consolidated category.")

    counts = (
        df["consolidated_error_category"]
        .value_counts()
        .rename_axis("consolidated_error_category")
        .reset_index(name="count")
    )
    counts["percentage"] = (counts["count"] / len(df) * 100).round(2)

    df.to_csv(OUTPUT, index=False)

    print(f"Input records: {len(df)}")
    print(f"Records assigned: {df['consolidated_error_category'].notna().sum()}")
    print(f"Unique cases: {df['case_id'].nunique()}")
    print("\nCONSOLIDATED CATEGORY COUNTS")
    print(counts.to_string(index=False))
    print(f"\nCreated: {OUTPUT.relative_to(BASE.parent)}")
    print("Original manual_review_80.csv was not modified.")

if __name__ == "__main__":
    main()
