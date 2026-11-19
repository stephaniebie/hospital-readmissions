# Team, tasks, and timeline

Last updated 2026-11-19 from the team's *Project Checkpoint To Do* doc (split on the 11/15 call), the Discord chat, and Canvas. If something changes, edit this file in your PR so it stays the single place to check.

## Members

| Member | Section | GitHub |
|---|---|---|
| Ryan Kerwick | CSCI 4502 | RyanKerwick |
| Tanmayee Potu | CSCI 4502 | |
| Jeremy Varghese | CSCI 5502 | Jeva2021 |
| Stephanie Bie | CSCI 5502 | stephaniebie |

4502 and 5502 students are graded separately, and the report must list each member's section.

## Open tasks: finish by **Saturday 11/28**

| Task | Owners | Where it goes | Notes |
|---|---|---|---|
| Add new datasets + preprocessing | Stephanie, Jeremy | new notebook + `docs/DATA.md` | Likely the real-world CMS readmission data (state/hospital level) the professor asked for; see [PROJECT.md](PROJECT.md#feedback-to-address) |
| Tune & compare models (decision tree vs. random forest) | Ryan, Tanmayee | `notebooks/model_tuning.ipynb` | Start from the checkpoint baseline; address the `observed_history_days` problem and report with and without same-year chronic flags |
| Create clustering model | Ryan, Tanmayee | `notebooks/clustering.ipynb` | Silhouette score + readmission rate per cluster (from the proposal) |
| Summarize & interpret findings | *unassigned* | report draft | Pick an owner |

## Before the presentation (12/3)

| Task | Owners |
|---|---|
| Final report (expand the checkpoint report, about 10 pages, ACM format) | *unassigned*: each person writes their own sections |
| Final slides | *unassigned* |
| Code + results zip with README | *unassigned* (this repo is most of it) |

See [FINAL_DELIVERABLES.md](FINAL_DELIVERABLES.md) for what each one needs.

## Timeline

| Date | What |
|---|---|
| 9/18 | Proposal report + slides (done) |
| 10/27–10/29 | Checkpoint meeting; checkpoint report + slides submitted 10/30 (done) |
| 11/19 | Final-presentation scheduling survey submitted by Ryan (all 12/3 slots) |
| 11/21–11/29 | Stephanie out of town |
| 11/23–11/27 | Fall break |
| **Sat 11/28** | **Modeling, clustering, and new-dataset work done** |
| 12/1 | End of Phase 6 (Analysis) in our proposal plan |
| **Thu 12/3** | **Final project presentation** (slot TBD from the survey) |
| After 12/3 | Polish slides + report from feedback, then submit slides, report, and code zip on Canvas (due date not posted yet) |

Availability notes from Discord: Ryan can't do 12/2 (work); Tanmayee works 12/1; Stephanie is busy weekdays until about 9 pm.

## Who did what so far

The final report needs an "individual contributions" appendix with at least one item per person. Add to this list as you finish things.

| Phase | Ryan | Tanmayee | Jeremy | Stephanie |
|---|---|---|---|---|
| Proposal | Proposal report doc; asked the TA about using synthetic data (DE-SynPUF) | Proposed the hospital-readmissions topic | Proposal slides edits | Brainstorming doc |
| 1 Exploration | | Data understanding (assigned with Jeremy) | Data understanding (assigned with Tanmayee) | `eda.ipynb`; checkpoint Exploration section |
| 2 Data preparation | `data-cleaning.ipynb` (claims to stays, readmission label, leakage control); checkpoint Data Preparation section, figures, and slide | | | Preprocessing (assigned with Ryan); repo setup |
| 3 Classification / features | | Baseline decision tree; checkpoint Decision Tree section | `feature_selection.ipynb` (column dictionary, 27 features, random-forest comparison); checkpoint Feature Selection section | Attribute descriptors; added the CMS data guide |
| Checkpoint | Notes on the professor's feedback (Discord, 10/29) | | | Checkpoint report and slides docs |

*Compiled from the To Do doc, the git history, and the Drive and Discord activity. Fix anything that's wrong or missing.*
