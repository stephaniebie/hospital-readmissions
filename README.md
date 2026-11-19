# Hospital Readmission Prediction and Patient Profiling
CSCI 4502/5502 Data Mining (CU Boulder, Fall 2026) course project.

**Question:** What characteristics are most associated with hospital readmission, and can we accurately predict whether a patient will return within 30 days of discharge?

We predict 30-day readmission for Medicare hospital stays with a decision tree and a random forest, and we cluster patients to see whether some groups are readmitted more than others. Data: CMS 2008–2010 DE-SynPUF (synthetic Medicare claims), Sample 1.

> **New here? Read in this order:**
> 1. [`docs/TEAM.md`](docs/TEAM.md): who owns what right now, and the dates that matter
> 2. [`docs/PROJECT.md`](docs/PROJECT.md): the plan, the decisions we already made, and the results so far
> 3. [`docs/DATA.md`](docs/DATA.md): getting the data, the cleaned tables, and what every column means
> 4. [`docs/FINAL_DELIVERABLES.md`](docs/FINAL_DELIVERABLES.md): what the presentation, report, and code zip need

## Team

| Member | Section | GitHub | Current focus (due Sat 11/28) |
|---|---|---|---|
| Ryan Kerwick | 4502 | RyanKerwick | Tune & compare models; clustering model |
| Tanmayee Potu | 4502 | | Tune & compare models; clustering model |
| Jeremy Varghese | 5502 | Jeva2021 | New datasets + preprocessing |
| Stephanie Bie | 5502 | stephaniebie | New datasets + preprocessing |

**Final presentation: Thursday 12/3** (exact time slot TBD). Full timeline in [`docs/TEAM.md`](docs/TEAM.md).

## Quickstart

### 1. Clone and install
```bash
git clone https://github.com/stephaniebie/hospital-readmissions.git
cd hospital-readmissions
python -m venv venv
source venv/Scripts/activate        # Git Bash on Windows
# venv\Scripts\Activate.ps1         # PowerShell
# source venv/bin/activate          # macOS / Linux
pip install -e .[dev]
python -m ipykernel install --user --name=hospital-readmissions
```
`pip install -e .` also installs the shared helper package `hospital_readmissions` (in `src/`), which every notebook can import.

### 2. Get the data (about 220 MB, never committed)
```bash
python scripts/get_data.py          # downloads the 5 CSVs from Kaggle into archive/
```
Then run [`notebooks/data-cleaning.ipynb`](notebooks/data-cleaning.ipynb) once to build the cleaned Parquet tables (details and a headless command in [`docs/DATA.md`](docs/DATA.md)).

### 3. Load the modeling table in any notebook
```python
from hospital_readmissions.data import load_readmit, patient_split, RECOMMENDED, TARGET

df = load_readmit()                  # 63,874 stays x 49 columns, readable names
train, test = patient_split(df)      # same patient-level split as the checkpoint
X_train, y_train = train[RECOMMENDED], train[TARGET]
```

## Repository map

```
README.md                    you are here
AGENTS.md / CLAUDE.md        context for Claude Code / Codex
docs/
  TEAM.md                    owners, open tasks, timeline, contribution log
  PROJECT.md                 plan, decisions, results so far, feedback to address
  DATA.md                    dataset, cleaned tables, column dictionary
  FINAL_DELIVERABLES.md      presentation / report / code-zip checklist
  SynPUF_DUG.pdf             official CMS DE-SynPUF data user guide
notebooks/
  eda.ipynb                  Phase 1 exploration (Stephanie)
  data-cleaning.ipynb        Phase 2 preprocessing -> cleaned Parquet tables (Ryan)
  feature_selection.ipynb    Phase 3 column dictionary + 27-feature set (Jeremy)
  model_tuning.ipynb         Phase 5 tuning & comparison (Ryan, Tanmayee), scaffold
  clustering.ipynb           Phase 4 patient clustering (Ryan, Tanmayee), scaffold
scripts/
  get_data.py                download the raw CSVs
src/hospital_readmissions/
  data.py                    shared loader, column names, feature lists, patient split
```

Not in the repo yet: the baseline decision-tree notebook (checkpoint "Baseline Decision Tree" section). Whoever has it, please add it as `notebooks/decision_tree_baseline.ipynb`.

## How we work

- **Branch, then pull request.** `git checkout -b <your-name>/<topic>`, commit, push, open a PR into `main`. Small PRs merge fast; anyone can approve.
- **Pull before you start:** `git pull origin main`.
- **One notebook per task.** Two people editing the same `.ipynb` at once will conflict. Put shared code in `src/hospital_readmissions/` instead of copying it between notebooks.
- **Never commit data.** `archive/`, `data/`, `cleaned_data/`, `*.csv` and `*.parquet` are git-ignored.
- **Keep notebook outputs small.** Clear huge outputs (big tables, many plotly figures) before committing.
- **Use the shared split and features** (`patient_split`, `RECOMMENDED`) so everyone's numbers can be compared.
- **AI tools are allowed, but we must say how we used them** in the report appendix. Note it in your PR description as you go.

## Links

- Shared Google Drive folder: *Data Mining Project Hospital Readmissions* (proposal and checkpoint reports and slides, To Do doc)
- Dataset: https://www.kaggle.com/datasets/anikannal/cms-synthetic-data
- Possible real-world comparison data: https://data.cms.gov/provider-data/datasets?keyword%5B0%5D=Readmissions
- Team chat: Discord group "Data Mining Project"
