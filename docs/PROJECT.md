# Project overview

Condensed from the proposal report (9/18), the checkpoint report and slides (10/30), and the professor's checkpoint feedback. The Google Docs in the team Drive folder have the full text.

## Goal

Predict whether a Medicare hospital stay is followed by another admission within **30 days of discharge**, find which patient characteristics matter most, and group patients into profiles to see whether some profiles are readmitted more often. Hospitals could use this to target follow-up care after discharge.

Related work tends to do either supervised prediction (Srinivasan et al. 2020, random forest, AUC 0.684; Emi-Johnson et al. 2025, with SHAP) or patient clustering (Villanueva-Rueda et al. 2025, k-means/PAM). **Our angle is doing both on the same data.** Full references are in the checkpoint report.

## Plan (six phases from the proposal)

| Phase | What | Status |
|---|---|---|
| 1 Exploration | Understand the data, first patterns, related work | Done (`eda.ipynb`) |
| 2 Data preparation | Clean, build the stay-level table and label | Done (`data-cleaning.ipynb`) |
| 3 Classification | Baseline, decision tree, random forest; feature selection | Baselines done (`feature_selection.ipynb`; decision-tree notebook not in repo yet) |
| 4 Clustering | Cluster patients, compare readmission rates across clusters | **In progress**: Ryan, Tanmayee |
| 5 Model evaluation | Compare, tune, and assess the models | **In progress**: Ryan, Tanmayee |
| 6 Analysis | Summarize and interpret findings | Open |

## How we evaluate (from the proposal)

- **Classification:** decision tree vs. random forest on a held-out test set of **unseen patients**. Main metrics are **ROC-AUC and F1**, plus precision, recall, and confusion matrices. Accuracy is misleading here: always predicting "no" scores about 90%.
- **Clustering:** **silhouette score** for cluster quality, and **readmission rate per cluster** to show whether profiles differ in risk.
- **Efficiency:** the professor wants an efficiency or scalability angle too (training time, complexity), not just accuracy.

## Decisions already made (don't silently undo these)

| Decision | Why | Where |
|---|---|---|
| Unit = one **hospital stay**, not one claim | Claims split across rows, or transfers between hospitals, would otherwise look like 1-day readmissions | data-cleaning §2 |
| Merge claims that overlap or start ≤ 1 day after the previous discharge | CMS transfer convention. This is a convention, not something the data proved | data-cleaning |
| `READMIT_30 = 1` if the next admission is ≤ 30 days after discharge | Standard CMS benchmark (Hospital Readmissions Reduction Program) | data-cleaning |
| Excluded 399 stays: 310 discharged after 12/1/2010, 89 where the patient died first | A "0" only counts if a readmission could have been observed | data-cleaning |
| Features use only information **before admission** (prior stays and visits counted before the admit date) | Avoid leakage | data-cleaning |
| Dropped annual payment totals | They include the readmission's own cost | data-cleaning |
| Added `chronic_condition_count_prior_year` | Same-year chronic flags overstate risk (1.6%→11.3% vs. 3.5%→10.0% across condition counts) | data-cleaning, Figure 2 |
| Scaling, imputation, encoding, and resampling happen **after** the split, fit on train only | Avoid leakage | all model notebooks |
| **Split by patient** (`GroupShuffleSplit`, 20% test, `random_state=0`) | One patient can have several stays | `hospital_readmissions.data.patient_split` |
| Use the **27 `RECOMMENDED` features** | Chosen by holdout AUC in feature selection | `hospital_readmissions.data.RECOMMENDED` |
| Leave out hospital id, DRG, diagnosis codes, state | High-cardinality columns that were memorized (train AUC up, test AUC down) or didn't help | feature_selection |

## Results so far (checkpoint)

**Data:** 63,874 eligible stays from 37,658 patients, 49 columns; **9.6% of stays readmitted** (per stay, not per patient). That's about half the ~19.6% reported for real Medicare (Jencks et al. 2009), and days-to-next-admission is nearly flat. In other words, the synthetic data's readmission signal is weak.

**Random forest, recommended 27 features** (fixed settings: 100 trees, max depth 12, min leaf 40, balanced class weights):
- Test ROC-AUC **0.701**, average precision **0.181** (base rate ≈ 0.096)
- Without the 11 same-year chronic flags: AUC **0.659**; with their sum instead of the flags: 0.692
- Adding a train-only hospital readmission rate: train AUC 0.834, test AUC 0.660 (memorizes)
- Top features: prior-year chronic count, then kidney disease, COPD, heart failure

**Baseline decision tree** (max depth 5, balanced class weights):
- Accuracy 54.9%, recall 72.1%, precision 13.7%, ROC-AUC 0.662
- **Problem:** `OBS_HISTORY_DAYS` (observed history) took about 63% of feature importance. It measures how much data exists, not the patient's health. Next step: drop it (it isn't in `RECOMMENDED`) and retrain

**Signals:** readmission rises from about 8.5% with no prior inpatient stay to about 14.5% with 3 or more; about 3.5% with 0–2 chronic conditions vs. about 10% with 7+; age shows almost no association.

## Next steps for modeling (from the checkpoint report)

1. Retrain the decision tree on `RECOMMENDED` (no observed history), then tune depth, leaf size, and class weights.
2. Tune the random forest (number of trees, depth, leaf size, `max_features`, class weights) with **cross-validation grouped by patient** (`GroupKFold`) on the training set only.
3. Tune the **decision threshold** to trade recall against precision; report the confusion matrix at the chosen threshold.
4. Report every model **with and without the same-year chronic flags** (`RECOMMENDED_NO_FLAGS`) because of possible leakage.
5. Decide whether `length_of_stay_days` and `total_payment` stay in. They're known at discharge (the usual time to score readmission risk) but not at admission.

## Feedback to address

From the professor at the checkpoint meeting (10/29, Ryan's notes):

- **Real-world data:** look into real data and better temporal coverage. The dataset is old (2008–2010); try to get recent data. (CMS Provider Data Catalog readmission datasets are state- or hospital-level, so they would need aggregation to compare.)
- **Usefulness:** when we finish, what other outcomes can we find? How would someone actually use this?
- **Is 30 days the right window?** Consider a week or other windows.
- **Back to EDA:** show visual results (distributions, outliers, correlations).
- **Preparation needs reasoning:** data has characteristic X, so we did Y, and it still fits our goal. Say what insights each step gave us.
- **Imbalance:** most stays aren't readmitted, so a constant guess is about 90% accurate. Think about balancing the data. Does that give new insights?
- **Explore the project from different angles.**

From the Nov 12 lecture on final reports: explain *why* for every choice, interpret every result (expected? surprising?), include efficiency, and write a real discussion section (limitations, what didn't work, future work, real-world use).
