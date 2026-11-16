
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
INPUT = BASE / "outputs" / "prompt_disagreements.csv"
OUTPUT = BASE / "outputs" / "disagreement_analysis.csv"

df = pd.read_csv(INPUT)

def classify_disagreement(row):
    claim = str(row["claim"]).lower()
    reasons = (
        str(row["A_reason"]).lower() + " " +
        str(row["B_reason"]).lower()
    )

    # Incomplete or incoherent claims
    if any(x in reasons for x in [
        "incomplete", "incoherent", "fragmented",
        "unclear", "ambiguous"
    ]):
        return "Incomplete_or_Ambiguous_Claim"

    # Claims combining multiple independent facts
    if any(x in claim for x in [
        " and ", " but ", " however "
    ]) and len(claim.split()) > 12:
        return "Potential_Compound_Claim"

    # Claims about what the report mentions
    if any(x in claim for x in [
        "does not mention", "no mention",
        "not specified", "does not contain",
        "without mentioning"
    ]):
        return "Report_Content_or_Absence"

    # Evidence interpretation and inference
    if any(x in reasons for x in [
        "implies", "suggests", "inferred",
        "does not explicitly", "not explicitly",
        "absence of evidence", "does not confirm"
    ]):
        return "Evidence_Interpretation_or_Inference"

    # Semantic equivalence
    if any(x in reasons for x in [
        "semantically", "equivalent",
        "terminology", "wording", "partial match"
    ]):
        return "Semantic_Equivalence"

    # Explicit contradiction
    if any(x in reasons for x in [
        "contradicts", "conflicts", "opposite"
    ]):
        return "Contradiction_Handling"

    return "Requires_Manual_Review"


df["preliminary_category"] = df.apply(
    classify_disagreement, axis=1
)

df["manual_category"] = ""
df["review_notes"] = ""

df.to_csv(OUTPUT, index=False)

print("DISAGREEMENT ANALYSIS DATASET CREATED")
print("Total disagreements:", len(df))
print("\nPRELIMINARY CATEGORY COUNTS:")
print(df["preliminary_category"].value_counts().to_string())
print("\nOUTPUT:")
print(OUTPUT)
