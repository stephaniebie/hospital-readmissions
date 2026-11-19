# Data

## Source

**CMS 2008–2010 Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF), Sample 1**, from Kaggle: [anikannal/cms-synthetic-data](https://www.kaggle.com/datasets/anikannal/cms-synthetic-data). These are synthetic Medicare claims that look like real ones but are not real patients, so results don't generalize directly to real hospitals. The official CMS guide is [`SynPUF_DUG.pdf`](SynPUF_DUG.pdf).

We use 5 of the files:

| File | One row per | Raw rows | Used for |
|---|---|---|---|
| `DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv` (+ 2009, 2010) | patient per year | 343,644 (3 files) | Demographics, 11 chronic-condition flags, coverage months, death date |
| `DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv` | claim segment | 66,773 | Hospital stays and the readmission label |
| `DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv` | claim segment | 790,790 | Prior outpatient / ER use before each admission |

## Getting it

The raw data (about 220 MB) is **never committed**. Pick one option:

**A. Script (recommended)**
```bash
python scripts/get_data.py
```
This downloads the dataset with `kagglehub` and copies the 5 CSVs into `archive/` at the repo root. Kaggle may ask you to sign in: create a token at kaggle.com → Settings → API and set `KAGGLE_API_TOKEN`, or put `kaggle.json` in `~/.kaggle/`. Never commit tokens.

**B. Manually:** download the zip from the Kaggle page and put the 5 CSVs in `archive/`.

**Colab:** `data-cleaning.ipynb` detects Colab and downloads the data itself.

## Building the cleaned tables

`notebooks/data-cleaning.ipynb` reads the raw CSVs and writes the cleaned tables as Parquet (Parquet keeps the data types: ICD-9 codes keep leading zeros, dates stay dates).

- Input folder: `$CMS_DATA_DIR`, else `archive/` (it checks the repo root and the notebooks folder)
- Output folder: `$CMS_OUTPUT_DIR`, else `cleaned_data/` next to wherever the notebook runs (usually `notebooks/cleaned_data/`)

Run it in Jupyter or VS Code, or headless from the repo root:
```bash
jupyter nbconvert --to notebook --execute notebooks/data-cleaning.ipynb --output data-cleaning.ipynb --ExecutePreprocessor.timeout=1800
```
Don't commit the executed copy unless you meant to change the notebook.

`hospital_readmissions.data.load_readmit()` finds the output in `$CMS_OUTPUT_DIR`, `cleaned_data/`, or `notebooks/cleaned_data/`.

| Table | Rows | Cols | One row per |
|---|---|---|---|
| `bene_year.parquet` | 343,644 | 35 | patient per year |
| `bene_static.parquet` | 116,352 | 11 | patient |
| `ip_clean.parquet` | 66,705 | 44 | inpatient claim (segments merged) |
| `op_clean.parquet` | 779,537 | 16 | outpatient claim |
| `ip_stays.parquet` | 64,273 | 22 | hospital stay (transfers merged) |
| **`readmit_df.parquet`** | **63,874** | **49** | **eligible stay: the modeling table** |
| `cleaning_log.csv` | 19 | 6 | row counts before and after each cleaning step |

## Modeling table columns (`readmit_df`)

Readable names come from `feature_selection.ipynb` and are applied by `load_readmit()`. **use** = one of the 27 `RECOMMENDED` features. Same-year chronic flags may leak (CMS sets them for the whole year, which can include the readmission), so report models with and without them.

| Readable name | CMS name | Use? | Meaning |
|---|---|---|---|
| `readmitted_30_days` | `READMIT_30` | target | 1 if the next inpatient admission is within 30 days of discharge, else 0. |
| `age_at_admission` | `AGE` | use | Age in years at admission. Birth dates in this file are only known to the month. |
| `alzheimers` | `SP_ALZHDMTA` | use | 1 if Alzheimer's or dementia was flagged for the discharge year. |
| `cancer` | `SP_CNCR` | use | 1 if cancer was flagged for the discharge year. |
| `chronic_condition_count_prior_year` | `N_CHRONIC_PREV_YEAR` | use | How many of the 11 chronic conditions were flagged in the previous calendar year. |
| `chronic_kidney_disease` | `SP_CHRNKIDN` | use | 1 if chronic kidney disease was flagged for the discharge year. |
| `copd` | `SP_COPD` | use | 1 if chronic obstructive pulmonary disease was flagged for the discharge year. |
| `depression` | `SP_DEPRESSN` | use | 1 if depression was flagged for the discharge year. |
| `diabetes` | `SP_DIABETES` | use | 1 if diabetes was flagged for the discharge year. |
| `diagnosis_count` | `N_DX` | use | How many diagnosis code slots were filled on the first claim. |
| `end_stage_renal_disease` | `ESRD` | use | 1 if the patient had end-stage renal disease in the discharge year. |
| `heart_failure` | `SP_CHF` | use | 1 if heart failure was flagged for the discharge year. |
| `hmo_coverage_months` | `BENE_HMO_CVRAGE_TOT_MONS` | use | Months of HMO coverage in the discharge year. 0 to 12. |
| `ischemic_heart_disease` | `SP_ISCHMCHT` | use | 1 if ischemic heart disease was flagged for the discharge year. |
| `length_of_stay_days` | `LOS_DAYS` | use | Discharge date minus admission date, in days. Same-day stays are 0. |
| `osteoporosis` | `SP_OSTEOPRS` | use | 1 if osteoporosis was flagged for the discharge year. |
| `part_d_coverage_months` | `PLAN_CVRG_MOS_NUM` | use | Months of Medicare Part D (prescription drug) coverage in the discharge year. 0 to 12. |
| `prior_er_visits_365d` | `PRIOR_ER_VISITS_365` | use | Outpatient claims in the 365 days before admission that were emergency-room visits (HCPCS 99281–99285). |
| `prior_inpatient_stays_365d` | `PRIOR_IP_STAYS_365` | use | Earlier hospital stays whose discharge was in the 365 days before this admission. |
| `prior_outpatient_payment_365d` | `PRIOR_OP_PMT_365` | use | Total outpatient Medicare payment in the 365 days before admission, in dollars. |
| `prior_outpatient_visits_30d` | `PRIOR_OP_VISITS_30` | use | Outpatient claims in the 30 days before admission. |
| `prior_outpatient_visits_365d` | `PRIOR_OP_VISITS_365` | use | Outpatient claims in the 365 days before admission. |
| `procedure_count` | `N_PRCDR` | use | How many procedure code slots were filled on the first claim. |
| `race` | `RACE` | use | Race recorded on the beneficiary file: White, Black, Hispanic, or Other. |
| `rheumatoid_or_osteoarthritis` | `SP_RA_OA` | use | 1 if rheumatoid arthritis or osteoarthritis was flagged for the discharge year. |
| `sex` | `SEX` | use | Sex recorded on the beneficiary file. M or F. |
| `stroke_or_tia` | `SP_STRKETIA` | use | 1 if stroke or transient ischemic attack was flagged for the discharge year. |
| `total_payment` | `TOTAL_PMT` | use | Sum of Medicare payments for the claims in the stay, in dollars. |
| `patient_id` | `DESYNPUF_ID` | split only | Synthetic patient id. |
| `admission_date` | `ADMSN_DT` | drop | Admission date of the stay (earliest claim if several claims were merged). |
| `admitted_before_2008` | `ADMSN_BEFORE_STUDY` | drop | The admission date is in late 2007, before the 2008 start of the beneficiary files. |
| `admitting_diagnosis_category` | `ADMTNG_DX_CAT` | drop | Same grouping of the admitting diagnosis. It matches the principal category on only about 36% of stays. |
| `admitting_diagnosis_code` | `ADMTNG_ICD9_DGNS_CD` | drop | Full ICD-9 admitting diagnosis. |
| `any_negative_payment` | `ANY_PMT_NEGATIVE` | drop | At least one claim in the stay had a negative payment (an adjustment). |
| `chronic_condition_count` | `N_CHRONIC` | drop | How many of the 11 chronic-condition flags are 1. It is exactly their sum. |
| `claims_in_stay` | `N_CLAIMS` | drop | How many inpatient claims were merged into this stay. |
| `days_to_next_admission` | `DAYS_TO_NEXT_ADMIT` | drop | Days from this discharge to the next admission. Missing if there is no later admission. |
| `discharge_date` | `DSCHRG_DT` | drop | Discharge date of the stay. |
| `drg_code` | `CLM_DRG_CD` | drop | Diagnosis-related group of the first claim: the billing category for why the patient was admitted. |
| `drg_ungrouped` | `DRG_UNGROUPED` | drop | The DRG was missing or not a real group. |
| `hospital_id` | `PRVDR_NUM` | drop | Hospital (provider) id of the first claim in the stay. |
| `observed_history_days` | `OBS_HISTORY_DAYS` | drop | How many days of claims we can see before this admission, capped at 365. |
| `part_a_coverage_months` | `BENE_HI_CVRAGE_TOT_MONS` | drop | Months of Medicare Part A (hospital) coverage in the discharge year. 0 to 12. |
| `part_b_coverage_months` | `BENE_SMI_CVRAGE_TOT_MONS` | drop | Months of Medicare Part B (physician) coverage in the discharge year. 0 to 12. |
| `principal_diagnosis_category` | `DX1_CAT` | drop | First 3 characters of the principal ICD-9 code (4 characters when the code starts with E). |
| `principal_diagnosis_code` | `ICD9_DGNS_CD_1` | drop | Full ICD-9 principal diagnosis. |
| `state_code` | `SP_STATE_CODE` | drop | SSA state code of the patient. |
| `stay_id` | `STAY_ID` | drop | Id of this hospital stay. |
| `zero_coverage_months` | `ZERO_COVERAGE` | drop | 1 if every coverage column that year was 0. |

## Quirks to know about

- Claim length is capped at **35 days** in this synthetic data, so long stays have truncated admission dates (discharge dates, and therefore the label, are fine).
- Some payments are small negatives (refunds). They're flagged, not removed.
- `chronic_condition_count_prior_year` is missing for every 2008 discharge (there's no 2007 file). Leave it missing for trees.
- About 3.8% of patient-years have zero coverage months; they're flagged, not dropped.
