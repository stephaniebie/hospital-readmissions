# Agent guide (Claude Code, Codex, etc.)

CSCI 4502/5502 Data Mining team project: predict 30-day hospital readmission on CMS DE-SynPUF synthetic Medicare claims (decision tree vs. random forest) and cluster patients into risk profiles. Read `README.md`, then `docs/PROJECT.md`, before changing anything.

## Layout
- `notebooks/`: one notebook per task. `data-cleaning.ipynb` builds the cleaned Parquet tables; `feature_selection.ipynb` defines column names and the 27 features; `model_tuning.ipynb` and `clustering.ipynb` are the current work.
- `src/hospital_readmissions/data.py`: shared loader (`load_readmit`), column dictionary (`ATTRIBUTES`), feature lists (`RECOMMENDED`, `RECOMMENDED_NO_FLAGS`), and the patient split (`patient_split`). Import from here instead of re-implementing.
- `scripts/get_data.py`: downloads the raw CSVs into `archive/`.
- `docs/`: project plan, decisions, data dictionary, team tasks, final-deliverable requirements.

## Rules that protect the results
- **Never commit data** (`archive/`, `cleaned_data/`, `*.csv`, `*.parquet`) or credentials.
- **Split by patient** (`patient_split`, or `GroupKFold` on `patient_id`). A row-level split leaks the same patient into train and test.
- **No leakage:** never use `days_to_next_admission`, IDs, raw dates, or annual payment totals as features. Fit scalers, encoders, imputers, and resamplers on training data only.
- Accuracy is misleading (~90% by always predicting "no"). Use ROC-AUC, F1, precision, recall, average precision.
- Report models with and without the same-year chronic flags (possible leakage).
- Keep comparisons on the default split (`random_state=0`) so numbers match the checkpoint.
- Don't rewrite another member's notebook; add a new one or put shared code in `src/`.
- Explain *why* in markdown cells. The report is graded on reasoning, and these notebooks are submitted as evidence.

## Setup
```bash
pip install -e .[dev]
python scripts/get_data.py
# run notebooks/data-cleaning.ipynb once (see docs/DATA.md)
```
