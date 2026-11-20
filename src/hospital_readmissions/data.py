"""Shared loading code for the hospital-readmissions project.

Everything the model notebooks (decision tree, random forest, tuning, clustering)
need in common lives here, so every notebook uses the same column names, the same
27 features and the same patient-level train/test split as the checkpoint results.

    from hospital_readmissions.data import load_readmit, patient_split, RECOMMENDED, TARGET

    df = load_readmit()                      # 63,874 stays, readable column names
    train, test = patient_split(df)          # same split as feature_selection.ipynb
    X_train, y_train = train[RECOMMENDED], train[TARGET]

The column dictionary below is copied from notebooks/feature_selection.ipynb
(Jeremy's attribute table). If you change a name or decision there, change it here too.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# (original CMS name, readable name, meaning, decision, why)
# decision is one of: "target", "use", "split only", "drop"
ATTRIBUTES = [
    ('STAY_ID', 'stay_id', 'Id of this hospital stay.', 'drop', 'Unique per row. An identifier, not a predictor.'),
    ('DESYNPUF_ID', 'patient_id', 'Synthetic patient id.', 'split only', 'Use it to keep a patient entirely in train or entirely in test. Do not pass it to the model.'),
    ('ADMSN_DT', 'admission_date', 'Admission date of the stay (earliest claim if several claims were merged).', 'drop', 'A raw date lets a tree memorize the calendar. The label is also built from these dates.'),
    ('DSCHRG_DT', 'discharge_date', 'Discharge date of the stay.', 'drop', 'Same problem as the admission date.'),
    ('READMIT_30', 'readmitted_30_days', '1 if the next inpatient admission is within 30 days of discharge, else 0.', 'target', 'This is the label.'),
    ('DAYS_TO_NEXT_ADMIT', 'days_to_next_admission', 'Days from this discharge to the next admission. Missing if there is no later admission.', 'drop', 'The label is exactly this number cut at 30. Training on it is leakage.'),
    ('PRVDR_NUM', 'hospital_id', 'Hospital (provider) id of the first claim in the stay.', 'drop', '2,666 hospitals. A train-only readmission rate for the hospital raised train AUC and lowered test AUC.'),
    ('CLM_DRG_CD', 'drg_code', 'Diagnosis-related group of the first claim: the billing category for why the patient was admitted.', 'drop', '739 codes. One-hot encoding and a smoothed train-only rate both failed to raise holdout AUC.'),
    ('DRG_UNGROUPED', 'drg_ungrouped', 'The DRG was missing or not a real group.', 'drop', 'True on about 0.6% of stays. Too rare for a stable split.'),
    ('ADMTNG_ICD9_DGNS_CD', 'admitting_diagnosis_code', 'Full ICD-9 admitting diagnosis.', 'drop', '2,259 codes, many of them rare. The 3-character category was tested instead and did not help.'),
    ('ICD9_DGNS_CD_1', 'principal_diagnosis_code', 'Full ICD-9 principal diagnosis.', 'drop', '2,698 codes. Same result as the admitting code.'),
    ('DX1_CAT', 'principal_diagnosis_category', 'First 3 characters of the principal ICD-9 code (4 characters when the code starts with E).', 'drop', "646 categories, and it matches the full code's prefix. Adding it did not raise holdout AUC."),
    ('ADMTNG_DX_CAT', 'admitting_diagnosis_category', 'Same grouping of the admitting diagnosis. It matches the principal category on only about 36% of stays.', 'drop', 'Still no holdout gain once the clinical flags and prior-use counts are in the model.'),
    ('N_DX', 'diagnosis_count', 'How many diagnosis code slots were filled on the first claim.', 'use', 'Small numeric summary of how many diagnoses were recorded. Known at discharge.'),
    ('N_PRCDR', 'procedure_count', 'How many procedure code slots were filled on the first claim.', 'use', 'Same idea for procedures. Known at discharge.'),
    ('TOTAL_PMT', 'total_payment', 'Sum of Medicare payments for the claims in the stay, in dollars.', 'use', 'Known once the stay is billed. Trees do not need this scaled. Drop it only if the model must run at admission, before payment is known.'),
    ('N_CLAIMS', 'claims_in_stay', 'How many inpatient claims were merged into this stay.', 'drop', '96.6% of stays are a single claim.'),
    ('ANY_PMT_NEGATIVE', 'any_negative_payment', 'At least one claim in the stay had a negative payment (an adjustment).', 'drop', 'True on about 0.09% of stays.'),
    ('ADMSN_BEFORE_STUDY', 'admitted_before_2008', 'The admission date is in late 2007, before the 2008 start of the beneficiary files.', 'drop', 'True on about 0.3% of stays.'),
    ('LOS_DAYS', 'length_of_stay_days', 'Discharge date minus admission date, in days. Same-day stays are 0.', 'use', 'Known at discharge and used by the forest. Drop it for an admission-time model.'),
    ('SEX', 'sex', 'Sex recorded on the beneficiary file. M or F.', 'use', 'Almost no mutual information with readmission in this sample. Kept because it is a standard demographic and costs one split.'),
    ('RACE', 'race', 'Race recorded on the beneficiary file: White, Black, Hispanic, or Other.', 'use', 'Same reason as sex.'),
    ('SP_STATE_CODE', 'state_code', 'SSA state code of the patient.', 'drop', '52 states. Adding it did not change holdout AUC.'),
    ('AGE', 'age_at_admission', 'Age in years at admission. Birth dates in this file are only known to the month.', 'use', 'The forest uses it. The linear correlation with the label is near zero; the tree can still split on age bands.'),
    ('ESRD', 'end_stage_renal_disease', '1 if the patient had end-stage renal disease in the discharge year.', 'use', 'About 25% of stays. A real clinical flag, not a near-constant.'),
    ('N_CHRONIC', 'chronic_condition_count', 'How many of the 11 chronic-condition flags are 1. It is exactly their sum.', 'drop', 'Redundant with the flags. A forest with the flags plus this count did not beat the flags alone.'),
    ('ZERO_COVERAGE', 'zero_coverage_months', '1 if every coverage column that year was 0.', 'drop', 'True on about 0.2% of stays.'),
    ('BENE_HI_CVRAGE_TOT_MONS', 'part_a_coverage_months', 'Months of Medicare Part A (hospital) coverage in the discharge year. 0 to 12.', 'drop', '98.3% of stays are 12. Almost no variation to split on.'),
    ('BENE_SMI_CVRAGE_TOT_MONS', 'part_b_coverage_months', 'Months of Medicare Part B (physician) coverage in the discharge year. 0 to 12.', 'drop', '97.5% of stays are 12.'),
    ('BENE_HMO_CVRAGE_TOT_MONS', 'hmo_coverage_months', 'Months of HMO coverage in the discharge year. 0 to 12.', 'use', 'Varies (about 71% are 0). Describes the kind of coverage, which is known for that year.'),
    ('PLAN_CVRG_MOS_NUM', 'part_d_coverage_months', 'Months of Medicare Part D (prescription drug) coverage in the discharge year. 0 to 12.', 'use', 'Varies (about 73% are 12).'),
    ('SP_ALZHDMTA', 'alzheimers', "1 if Alzheimer's or dementia was flagged for the discharge year.", 'use', 'One of the 11 chronic flags. See the leakage note under the dictionary.'),
    ('SP_CHF', 'heart_failure', '1 if heart failure was flagged for the discharge year.', 'use', 'Readmission is about 4.6% without this flag and about 11.5% with it.'),
    ('SP_CHRNKIDN', 'chronic_kidney_disease', '1 if chronic kidney disease was flagged for the discharge year.', 'use', 'Readmission is about 5.4% without this flag and about 12.4% with it. Highest flag importance.'),
    ('SP_CNCR', 'cancer', '1 if cancer was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('SP_COPD', 'copd', '1 if chronic obstructive pulmonary disease was flagged for the discharge year.', 'use', 'Readmission is about 6.2% without this flag and about 13.1% with it.'),
    ('SP_DEPRESSN', 'depression', '1 if depression was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('SP_DIABETES', 'diabetes', '1 if diabetes was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('SP_ISCHMCHT', 'ischemic_heart_disease', '1 if ischemic heart disease was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('SP_OSTEOPRS', 'osteoporosis', '1 if osteoporosis was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('SP_RA_OA', 'rheumatoid_or_osteoarthritis', '1 if rheumatoid arthritis or osteoarthritis was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('SP_STRKETIA', 'stroke_or_tia', '1 if stroke or transient ischemic attack was flagged for the discharge year.', 'use', 'One of the 11 chronic flags.'),
    ('OBS_HISTORY_DAYS', 'observed_history_days', 'How many days of claims we can see before this admission, capped at 365.', 'drop', 'Mostly a marker of whether the stay is early in the 2008–2010 file. Holdout AUC did not change when it was removed.'),
    ('PRIOR_IP_STAYS_365', 'prior_inpatient_stays_365d', 'Earlier hospital stays whose discharge was in the 365 days before this admission.', 'use', 'Readmission rises from about 8.5% with no prior stay to about 14.5% with 3 or more. Uses only earlier dates, so it is not leakage.'),
    ('PRIOR_OP_VISITS_365', 'prior_outpatient_visits_365d', 'Outpatient claims in the 365 days before admission.', 'use', 'Prior utilization. Only visits dated before the admission.'),
    ('PRIOR_OP_VISITS_30', 'prior_outpatient_visits_30d', 'Outpatient claims in the 30 days before admission.', 'use', 'Recent outpatient use. Correlation with the 365-day count is only about 0.42, so it is not a copy of that column.'),
    ('PRIOR_OP_PMT_365', 'prior_outpatient_payment_365d', 'Total outpatient Medicare payment in the 365 days before admission, in dollars.', 'use', 'The forest ranks this among the top numeric features.'),
    ('PRIOR_ER_VISITS_365', 'prior_er_visits_365d', 'Outpatient claims in the 365 days before admission that were emergency-room visits (HCPCS 99281–99285).', 'use', 'Prior emergency use. Only visits dated before the admission.'),
    ('N_CHRONIC_PREV_YEAR', 'chronic_condition_count_prior_year', 'How many of the 11 chronic conditions were flagged in the previous calendar year.', 'use', 'Leakage-safer illness burden. Missing when the patient has no prior-year record. The forest gives this column the largest importance.'),
]

RENAME = {orig: name for orig, name, *_ in ATTRIBUTES}

TARGET = "readmitted_30_days"
GROUP = "patient_id"

CHRONIC_FLAGS = [
    "alzheimers", "heart_failure", "chronic_kidney_disease", "cancer", "copd",
    "depression", "diabetes", "ischemic_heart_disease", "osteoporosis",
    "rheumatoid_or_osteoarthritis", "stroke_or_tia",
]

# The 27 features recommended in feature_selection.ipynb.
RECOMMENDED = [
    "age_at_admission", "sex", "race",
    "length_of_stay_days", "diagnosis_count", "procedure_count", "total_payment",
    "end_stage_renal_disease",
    "hmo_coverage_months", "part_d_coverage_months",
    "prior_inpatient_stays_365d", "prior_outpatient_visits_365d", "prior_outpatient_visits_30d",
    "prior_outpatient_payment_365d", "prior_er_visits_365d",
    "chronic_condition_count_prior_year",
    *CHRONIC_FLAGS,
]

# Same features without the same-year chronic flags (possible leakage; report both).
RECOMMENDED_NO_FLAGS = [c for c in RECOMMENDED if c not in CHRONIC_FLAGS]

# Known only at discharge, not at admission. Drop these for an admission-time model.
DISCHARGE_TIME_FEATURES = ["length_of_stay_days", "total_payment"]

REPO_ROOT = Path(__file__).resolve().parents[2]


def find_cleaned_dir() -> Path:
    """Return the folder holding the cleaned Parquet tables.

    Checks $CMS_OUTPUT_DIR first, then cleaned_data/ at the repo root, then
    notebooks/cleaned_data/ (where data-cleaning.ipynb writes when Jupyter runs it
    from the notebooks folder).
    """
    candidates = []
    if os.environ.get("CMS_OUTPUT_DIR"):
        candidates.append(Path(os.environ["CMS_OUTPUT_DIR"]))
    candidates += [
        REPO_ROOT / "cleaned_data",
        REPO_ROOT / "notebooks" / "cleaned_data",
        Path("cleaned_data"),
    ]
    for c in candidates:
        if (c / "readmit_df.parquet").exists():
            return c
    raise FileNotFoundError(
        "readmit_df.parquet not found. Run notebooks/data-cleaning.ipynb first "
        "(see docs/DATA.md), or set CMS_OUTPUT_DIR to the folder that holds it. "
        f"Looked in: {', '.join(str(c) for c in candidates)}"
    )


def load_table(name: str) -> pd.DataFrame:
    """Load one cleaned table by name, e.g. "ip_stays" or "bene_static"."""
    return pd.read_parquet(find_cleaned_dir() / f"{name}.parquet")


def load_readmit(renamed: bool = True) -> pd.DataFrame:
    """Load the modeling table: one row per eligible hospital stay.

    renamed=True (default) uses the readable names from ATTRIBUTES, which is what
    the feature-selection and model notebooks use.
    """
    df = load_table("readmit_df")
    if renamed:
        missing = set(df.columns) - set(RENAME)
        if missing:
            raise KeyError(f"Columns not in ATTRIBUTES (update data.py): {sorted(missing)}")
        df = df.rename(columns=RENAME)
    return df


def patient_split(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 0):
    """Split stays so each patient is entirely in train or entirely in test.

    With the defaults this is the exact split used in feature_selection.ipynb,
    so scores stay comparable with the checkpoint results.
    """
    from sklearn.model_selection import GroupShuffleSplit

    group_col = GROUP if GROUP in df.columns else "DESYNPUF_ID"
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(splitter.split(df, groups=df[group_col]))
    return df.iloc[train_idx], df.iloc[test_idx]
