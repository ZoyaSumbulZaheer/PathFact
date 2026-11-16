
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

import pandas as pd

# -------------------------------------------------
# Configuration
# -------------------------------------------------

MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/generate"

BASE = Path(__file__).resolve().parent
INPUT = BASE / "data" / "generated_reports.csv"
OUTPUT = BASE / "outputs"

OUTPUT.mkdir(exist_ok=True)

# -------------------------------------------------
# Ollama request
# -------------------------------------------------


def ask_qwen(prompt, max_retries=3):

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096,
            "repeat_penalty": 1.15,
            "repeat_last_n": 128,
            "num_predict": 2048
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    for attempt in range(1, max_retries + 1):

        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                result = json.loads(response.read().decode("utf-8"))

            return result["response"], result.get("total_duration", 0)

        except urllib.error.HTTPError as e:

            error_details = e.read().decode("utf-8", errors="replace")

            print(f"\nOllama HTTP error {e.code}: {error_details[:1000]}")

            if e.code not in (500, 502, 503, 504):
                raise

            if attempt < max_retries:
                wait_time = attempt * 30
                print(f"Retry {attempt}/{max_retries} after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

        except (urllib.error.URLError, TimeoutError) as e:

            print(f"\nOllama connection error: {e}")

            if attempt < max_retries:
                wait_time = attempt * 30
                print(f"Retry {attempt}/{max_retries} after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise



# -------------------------------------------------
# JSON extraction
# -------------------------------------------------

def extract_claims(report):
    prompt = f"""
You are a pathology claim extraction assistant.

Extract atomic factual claims from this AI-generated pathology report.

Rules:
- Extract only explicitly stated information.
- Do not invent missing information.
- Preserve uncertainty and ambiguity.
- Separate diagnosis, location, grade, invasion,
  molecular findings, margins and recommendations.
- Flag incomplete or contradictory statements.
- Do not merge independent findings.

Use these extraction statuses:
explicit, uncertain, incomplete, contradictory.

Return JSON with this structure:

{{
  "claims": [
    {{
      "claim_id": 1,
      "claim_text": "",
      "clinical_field": "",
      "extraction_status": ""
    }}
  ]
}}

REPORT:
{report}
"""

    response, duration = ask_qwen(prompt)
    data = json.loads(response)

    return data, duration


# -------------------------------------------------
# Experiment A: Direct prompting
# -------------------------------------------------

def experiment_a(claims, reference):
    prompt = f"""
Compare each generated pathology claim against the reference report.

Assign exactly one label:
- Supported
- Contradicted
- Not Supported
- Unverifiable

Definitions:
Supported: Reference evidence supports the claim.
Contradicted: Reference evidence explicitly conflicts.
Not Supported: Available reference evidence does not substantiate it.
Unverifiable: Available evidence is insufficient to determine correctness.

Evaluate claims independently.
Do not use external medical knowledge.
Do not assume missing information is false.
Provide reference evidence and a reason.

Return JSON:

{{
  "evaluations": [
    {{
      "claim_id": 1,
      "claim": "",
      "label": "",
      "evidence": "",
      "reason": ""
    }}
  ]
}}

CLAIMS:
{json.dumps(claims, ensure_ascii=False)}

REFERENCE REPORT:
{reference}
"""

    response, duration = ask_qwen(prompt)

    return json.loads(response), duration


# -------------------------------------------------
# Experiment B: Criteria-based prompting
# -------------------------------------------------

def experiment_b(claims, reference):
    prompt = f"""
You are an evidence-grounded pathology factuality judge.

Evaluate every claim against the supplied reference report.

Follow these steps for EACH claim:

STEP 1: Identify the exact clinical proposition.
STEP 2: Identify the relevant reference evidence.
STEP 3: Check whether the wording is semantically equivalent,
         even if different terminology is used.
STEP 4: Identify explicit agreement, explicit conflict,
         partial support, or insufficient evidence.
STEP 5: Assign one final factuality label.

LABEL DEFINITIONS:

Supported:
The complete clinical proposition is supported by evidence.

Contradicted:
Reference evidence explicitly conflicts with the proposition.

Not Supported:
The available reference is sufficiently relevant to assess
the proposition, but does not substantiate it.

Unverifiable:
The reference lacks sufficient information to determine
whether the proposition is true or false.

IMPORTANT RULES:

- Do not use external medical knowledge.
- Missing evidence alone does not establish falsity.
- Preserve anatomical distinctions.
- Recognize synonymous or semantically equivalent diagnoses.
- Separate compound claims into their independently assessable parts.
- If only part of a compound claim is supported, identify
  the supported and unsupported portions in the reason.
- Never invent reference evidence.
- Quote or reproduce the exact relevant reference wording.
- Do not treat recommendations as confirmed findings.

Return JSON only:

{{
  "evaluations": [
    {{
      "claim_id": 1,
      "claim": "",
      "label": "",
      "evidence": "",
      "reason": "",
      "evidence_assessment": ""
    }}
  ]
}}

CLAIMS:
{json.dumps(claims, ensure_ascii=False)}

REFERENCE REPORT:
{reference}
"""

    response, duration = ask_qwen(prompt)

    return json.loads(response), duration


# -------------------------------------------------
# Main experiment
# -------------------------------------------------


def main():

    df = pd.read_csv(INPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    claims_file = OUTPUT / "extracted_claims.json"
    a_file = OUTPUT / "experiment_A_direct.json"
    b_file = OUTPUT / "experiment_B_criteria.json"

    # Load previously saved results
    def load_results(file_path):
        if file_path.exists():
            return json.loads(file_path.read_text(encoding="utf-8"))
        return []

    all_claims = load_results(claims_file)
    results_a = load_results(a_file)
    results_b = load_results(b_file)

    # Verify that saved records are aligned
    ids_claims = [x["case_id"] for x in all_claims]
    ids_a = [x["case_id"] for x in results_a]
    ids_b = [x["case_id"] for x in results_b]

    if ids_claims != ids_a or ids_claims != ids_b:
        raise ValueError("Saved result files are not aligned. Stopping.")

    completed_ids = set(ids_claims)

    extraction_times = []
    time_a = []
    time_b = []

    total = len(df)

    print(f"Starting PathFact experiments on {total} cases")
    print(f"Model: {MODEL}")
    print(f"Previously completed: {len(completed_ids)}")
    print(f"Remaining: {total - len(completed_ids)}")

    for index, row in df.iterrows():

        case_id = row["case_id"]

        if case_id in completed_ids:
            print(f"\n[{index + 1}/{total}] Skipping {case_id} (already completed)")
            continue

        print(f"\n[{index + 1}/{total}] Processing {case_id}")

        # Stage 1: Claim extraction
        extracted, extraction_time = extract_claims(
            row["generated_report"]
        )

        claims = extracted.get("claims", [])

        print(f"Extracted claims: {len(claims)}")

        # Stage 2: Experiment A
        output_a, duration_a = experiment_a(
            claims,
            row["reference_report"]
        )

        print("Experiment A completed")

        # Stage 3: Experiment B
        output_b, duration_b = experiment_b(
            claims,
            row["reference_report"]
        )

        print("Experiment B completed")

        # Save all three results together after both experiments finish
        all_claims.append({
            "case_id": case_id,
            "claims": claims
        })

        results_a.append({
            "case_id": case_id,
            **output_a
        })

        results_b.append({
            "case_id": case_id,
            **output_b
        })

        extraction_times.append(extraction_time)
        time_a.append(duration_a)
        time_b.append(duration_b)

        claims_file.write_text(
            json.dumps(all_claims, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        a_file.write_text(
            json.dumps(results_a, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        b_file.write_text(
            json.dumps(results_b, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        completed_ids.add(case_id)

        print(f"Saved progress: {len(completed_ids)}/{total}")

    print("\nAll remaining experiments completed.")
    print("Total completed cases:", len(completed_ids))
    print("Output directory:", OUTPUT)


if __name__ == "__main__":
    main()

