import pandas as pd
from pathlib import Path

# Run from the PathBench-main project root:
# python pathfact\prepare_manual_review.py

source = Path("pathfact/outputs/disagreement_analysis.csv")
output = Path("pathfact/outputs/manual_review_80.csv")

df = pd.read_csv(source)
for col in [
    "primary_error_category",
    "secondary_error_category",
    "preferred_interpretation",
    "review_confidence",
    "review_notes"
]:
    df[col] = ""

# Researcher-led, reference-relative desk-review decisions from our discussion.
# These are NOT clinical gold labels or pathologist-validated judgments.
reviews = {
("TCGA-33-4566",6):("Evidence absence vs inference","A","Medium","Negative lymph nodes do not establish absence of lymphatic invasion."),
("TCGA-33-4566",7):("Compound / incomplete claim","Neither","Low","The claim combines lymphatic invasion and margin status; neither is established by the cited evidence."),
("TCGA-43-2576",1):("Anatomical/specimen mismatch","B","High","Reference identifies a left upper-lobe specimen, conflicting with the claimed right lung."),
("TCGA-4J-AA1J",7):("Anatomical/specimen mismatch","B","High","Reference describes uterine carcinoma, not invasive cervical squamous neoplasia in an adjacent right ureter."),
("TCGA-4V-A9QL",7):("Numerical/value mismatch","B","High","Reference gives an 8 cm tumor, not approximately 5 cm."),
("TCGA-4V-A9QL",10):("Report-content / missing evidence","A","Medium","No pending additional sections are described; absence from the reference does not establish that they were pending."),
("TCGA-86-7711",1):("Reference incompleteness","B","Medium","Reference explicitly describes the report as incomplete and lacks enough detail to verify the specimen claim."),
("TCGA-86-7711",3):("Reference incompleteness","B","Medium","Incomplete reference does not establish pleural invasion."),
("TCGA-86-7711",5):("Report-content / missing evidence","B","Medium","The incomplete reference does not establish whether neoadjuvant treatment was specified."),
("TCGA-86-8055",2):("Compound / mixed-support claim","B","High","Moderate differentiation is supported; squamous histology and tumor size are not stated."),
("TCGA-97-A4M5",2):("Evidence-scope overextension","A","Medium","Free margins/no residual tumor do not specifically establish the bronchial margin assertion as phrased."),
("TCGA-97-A4M5",4):("Evidence-scope overextension","A","Medium","Negative nodes at specified levels do not establish that all peribronchial nodes are negative."),
("TCGA-A6-2686",1):("Compound / anatomical mismatch","B","High","Right-colon specimen is described; lung and axillary-node elements are unsupported, not necessarily contradicted."),
("TCGA-A6-2686",2):("Anatomical/specimen mismatch","A","High","Reference concerns right-colon adenocarcinoma, not a lung specimen or left upper lobe."),
("TCGA-A6-2686",5):("Incomplete / corrupted claim","B","Medium","The fragmented lung resection/level/dimension assertions are not established by the colon report."),
("TCGA-A8-A09Z",5):("Incomplete / corrupted claim","A","Low","The claim is too fragmented to reliably interpret; the reference does not justify a confident contradiction."),
("TCGA-A8-A09Z",7):("Clinical attribute confusion","Neither","High","Clear margins do not mean the invasive carcinoma itself has no invasion; grade II and margin status are distinct attributes."),
("TCGA-AA-3814",3):("Incomplete / compound claim","A","Low","Claim is fragmented; some components may be supported, but the combined proposition cannot be reliably judged."),
("TCGA-AC-A3TN",4):("Compound / mixed-support claim","B","Medium","Two axillary nodes are explicitly negative; the mastectomy/sentinel-node wording is not fully established."),
("TCGA-AH-6544",1):("Reference scope mismatch","B","High","Molecular-only reference does not establish a right hemicolectomy."),
("TCGA-AH-6544",2):("Reference scope mismatch","B","High","Molecular-only reference does not establish histopathological diagnosis or hemicolectomy."),
("TCGA-AH-6544",3):("Reference scope mismatch","A","Medium","No LVI/bladder evidence is provided; absence of information is not proof of contradiction."),
("TCGA-AH-6544",4):("Reference scope mismatch","B","High","Molecular-only reference provides no lymph-node or metastasis findings."),
("TCGA-AH-6544",5):("Incomplete / compound claim","Neither","Low","Fragmented claim combines size, invasion and margins, none assessable from molecular-only text."),
("TCGA-AH-6544",6):("Reference scope mismatch","B","High","Molecular-only reference does not describe muscularis propria or distal fat."),
("TCGA-AO-A03M",4):("Semantic ambiguity / unsupported detail","B","Medium","Invasive ductal carcinoma is confirmed; 'focal' is not explicitly established."),
("TCGA-AO-A03M",8):("Compound / incomplete claim","Neither","Medium","ER is positive; the remaining high-grade-cell wording is unclear and not established."),
("TCGA-AO-A125",7):("Negation / scope ambiguity","B","Medium","Reference diagnoses breast carcinoma and does not diagnose melanoma; wording must be interpreted as no melanoma, not no tumor of any type."),
("TCGA-BC-A3KG",1):("Anatomical/specimen mismatch","B","High","Reference concerns liver resection, not right-breast gross findings."),
("TCGA-BC-A3KG",5):("Anatomical / margin-scope mismatch","B","Medium","Liver margins are described, but a posterior breast margin is not."),
("TCGA-BH-A0DL",1):("Anatomical / procedure mismatch","A","High","Reference specifies left breast segmental mastectomy, not the claimed right-sided/total procedure."),
("TCGA-BH-A0DL",7):("Evidence absence vs contradiction","B","Medium","No liver biopsy is described; absence alone does not establish contradiction."),
("TCGA-BP-4173",12):("Anatomical / diagnostic mismatch","B","High","Reference reports chronic pyelonephritis in kidney, not chronic cholecystitis."),
("TCGA-BQ-5877",3):("Incomplete / compound claim","A","Medium","Renal-vein invasion is explicitly stated; the remaining claim fragment is unclear."),
("TCGA-BR-A4J7",1):("Anatomical mismatch / compound claim","Neither","Medium","Stomach/gastrectomy element is plausible, but uterine wording is wrong or corrupted."),
("TCGA-BR-A4J7",2):("Incomplete / compound claim","Neither","Low","Some gastric tumor details are available, but the fragmented Lauren/omentum/size assertions cannot be judged as one claim."),
("TCGA-BR-A4J7",3):("Reference scope mismatch","B","High","Reference does not provide a peritoneal histologic type for this claim."),
("TCGA-BR-A4J7",7):("Incomplete / staging claim","A","Medium","Reference does not provide staging; claim is too corrupted for a confident label."),
("TCGA-CC-A5UD",1):("Compound / report-metadata claim","B","High","Clinical and specimen information are present, but informed consent is not stated."),
("TCGA-CJ-4635",4):("Semantic equivalence","B","High","Reference explicitly says the tumor has a Fuhrman nuclear grade; it need not state the numeric grade to support this wording."),
("TCGA-CN-4722",2):("Reference scope mismatch","B","High","Reference is a laryngeal biopsy report and contains no lung findings."),
("TCGA-CN-4722",5):("Reference scope mismatch","B","High","Reference does not report LVI status."),
("TCGA-CN-4722",6):("Reference scope mismatch","B","High","Reference does not report surgical margin status."),
("TCGA-CV-7433",1):("Semantic equivalence / procedure specificity","A","Medium","Laryngopharyngectomy and neck dissection broadly support the claim, although 'total laryngectomy' is not the exact reported term."),
("TCGA-CV-7446",1):("Semantic equivalence","A","High","All margins are free of tumor, supporting the general claim of negative margins."),
("TCGA-CV-7446",3):("Incomplete / partially supported claim","A","Medium","Reference confirms metastatic squamous carcinoma in one of two nodes; claim is fragmented but its central nodal-metastasis assertion is supported."),
("TCGA-CZ-5463",9):("Incomplete / compound claim","Neither","Low","Cytogenetic findings are present, but chronic inflammation/interstitial fibrosis wording is unsupported and corrupted."),
("TCGA-D1-A0ZQ",9):("Reference scope mismatch","A","Medium","No pelvic lymph nodes are described in the supplied report; phrase is brief and potentially ambiguous."),
("TCGA-D1-A17D",6):("Numerical/value mismatch","B","High","Reference mentions pelvic and para-aortic nodes but does not give a count of fifteen."),
("TCGA-D1-A17D",8):("Evidence-scope overextension","B","High","Negative lymph nodes do not establish that the entire surgical resection was negative; margin status is not supplied."),
("TCGA-D1-A17D",9):("Incomplete / compound claim","Neither","Low","Fragmented claim mixes para-aortic regions, ovaries and endometriosis; not all components can be assessed."),
("TCGA-D1-A17D",11):("Numerical/value mismatch","A","Medium","Ovaries are described, but the claimed 160 g weight is not reported."),
("TCGA-DB-A64S",1):("Anatomical evidence absence","B","High","Reference gives no left-frontal location; it does not establish a contradictory location."),
("TCGA-DB-A64S",5):("Report-content / absence claim","B","High","MIB-1 is not mentioned in the supplied reference text."),
("TCGA-DB-A64S",6):("Evidence absence vs contradiction","B","High","Reference does not mention IDH1-positive lymph nodes; absence is not a direct contradiction."),
("TCGA-DU-A76R",1):("Report-content / reference incompleteness","B","High","Reference explicitly says special stains are being requested to better characterize the neoplasm."),
("TCGA-DU-A76R",4):("Compound / mixed-support claim","Neither","High","WHO grade III is supported, but the appended '/18' is not; claim should be split."),
("TCGA-E7-A677",1):("Numerical/value mismatch","A","High","Reference gives 3×2×2 cm, conflicting with 7×6×5 cm; remaining claim text is corrupted."),
("TCGA-E7-A677",3):("Incomplete / numerical claim","Neither","Low","Claim combines unclear Clark/0.6/2 cm wording; it cannot be reliably interpreted."),
("TCGA-E9-A1R6",2):("Report-content / absence claim","B","Medium","Reference explicitly says tubule formation, nuclear pleomorphism and mitotic count are not provided; claim wording is corrupted."),
("TCGA-E9-A1R6",7):("Report-content / ambiguous wording","Neither","Low","'Surgical margins were absent' is ambiguous: it may mean margins were not included, rather than a margin-status result. Do not force a label."),
("TCGA-EL-A3CX",1):("Compound / mixed-support claim","Neither","Medium","Total thyroidectomy, right-lobe papillary carcinoma and LVI are supported; fibroadipose-tissue wording is not established."),
("TCGA-EL-A3CX",2):("Compound / unsupported subtype","Neither","Medium","Papillary thyroid carcinoma is confirmed, but adenomatous goiter is not mentioned."),
("TCGA-EL-A3CX",5):("Compound / unsupported metastasis","Neither","Medium","Papillary thyroid carcinoma is present, but metastatic disease and fibroadipose-tissue assertions are not established."),
("TCGA-G9-6351",1):("Compound / semantic ambiguity","Neither","Medium","Prostate cancer is confirmed and seminal vesicles are explicitly tumor-negative; claim does not clearly assert seminal-vesicle involvement."),
("TCGA-G9-6351",2):("Semantic equivalence","B","High","Reference confirms prostatic adenocarcinoma with Gleason 3+4 (7/10); claim is redundant but broadly consistent."),
("TCGA-GC-A3RD",6):("Compound / mixed-support claim","B","Medium","Pelvic nodes are explicitly negative for metastasis; 'no significant pathological changes' is not fully established."),
("TCGA-GF-A4EO",4):("Reference scope mismatch","B","High","Reference concerns axillary nodes and fibrofatty tissue, not visceral pleura or margins."),
("TCGA-P5-A781",1):("Anatomical contradiction","A","High","Reference explicitly identifies the right frontal lobe, conflicting with left frontal."),
("TCGA-R6-A8WC",3):("Anatomical / numerical mismatch","Neither","High","Reference describes distal esophageal adenocarcinoma, not a presigmoid tumor; 0 cm is not established."),
("TCGA-VP-A876",1):("Semantic equivalence","A","Medium","Reference confirms radical prostate excision for adenocarcinoma; claim is repetitive but its central proposition is supported."),
("TCGA-VP-A876",12):("Evidence absence vs inference","B","Medium","Reference reports negative pelvic nodes but does not establish metastatic carcinoma within the prostate itself."),
("TCGA-W3-AA1O",2):("Compound / specimen mismatch","Neither","High","Reference first specimen is a shoulder lesion without overt melanoma; second specimen has 12/48 positive axillary nodes and a 5 cm mass. Claim conflates them and gives 0 cm."),
("TCGA-W3-AA1O",3):("Compound / anatomical mismatch","Neither","High","Reference describes a shoulder lesion and right axillary nodes, not retrocaval nodes; claim mixes negative and positive assertions."),
("TCGA-W3-AA1O",4):("Numerical / specimen mismatch","Neither","High","Reference reports a 5 cm multinodular axillary mass, not melanoma measuring 0 mm."),
("TCGA-W3-AA1O",5):("Anatomical / specimen mismatch","Neither","High","Reference reports 12/48 positive right axillary nodes, not four retrocaval nodes."),
("TCGA-WC-A880",4):("Semantic equivalence","A","High","'Predominantly epithelioid type' reasonably supports predominance/dominance of that cell type."),
("TCGA-WR-A838",4):("Incomplete / unsupported marker claim","Neither","Medium","Reference confirms high-grade serous carcinoma but does not mention CD23; claim is fragmented."),
("TCGA-WR-A838",5):("Evidence absence vs contradiction","B","High","Reference does not specify invasion at surgical margins; missing margin evidence does not prove invasion."),
("TCGA-WR-A838",7):("Evidence absence vs contradiction","B","High","Reference does not provide explicit margin status; negative lymph nodes do not establish uninvolved margins."),
}

# Keep the source unchanged; populate a separate copy.
for col in ["primary_error_category", "secondary_error_category",
            "preferred_interpretation", "review_confidence", "review_notes"]:
    if col not in df.columns:
        df[col] = ""

# Use the existing preliminary category as a provisional secondary category
# only when a more specific secondary category has not been supplied.
for idx, row in df.iterrows():
    key = (str(row["case_id"]), int(row["claim_id"]))
    if key in reviews:
        category, preferred, confidence, notes = reviews[key]
        df.at[idx, "primary_error_category"] = category
        df.at[idx, "preferred_interpretation"] = preferred
        df.at[idx, "review_confidence"] = confidence
        df.at[idx, "review_notes"] = notes
        preliminary = row.get("preliminary_category", "")
        df.at[idx, "secondary_error_category"] = (
            preliminary if pd.notna(preliminary) and str(preliminary).strip() else ""
        )

missing = []
for _, row in df.iterrows():
    key = (str(row["case_id"]), int(row["claim_id"]))
    if key not in reviews:
        missing.append(key)

df.to_csv(output, index=False, encoding="utf-8-sig")

print(f"Input rows: {len(df)}")
print(f"Manually reviewed keys in script: {len(reviews)}")
print(f"Rows populated: {len(df) - len(missing)}")
print(f"Rows still requiring review: {len(missing)}")
if missing:
    print("Unmapped case/claim IDs:")
    for item in missing:
        print(item)
print(f"\nCreated: {output}")
print("Original disagreement_analysis.csv was not modified.")
