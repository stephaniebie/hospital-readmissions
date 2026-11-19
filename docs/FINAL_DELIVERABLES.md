# Final deliverables

The course project is **40% of the grade**. Requirements below come from the Nov 12 lecture on final projects (Canvas hasn't posted the final assignments yet; update this file when it does). Use it as a checklist.

## 1. Presentation: Thursday 12/3 (slot TBD)

- **Coordinate timing.** At checkpoints, one or two people running long squeezed out the later speakers. Agree on minutes per person and rehearse once.
- Decide who presents which part.
- Give an overview and the **key points**. The report, code, and results back up the details.
- After the meeting, polish the slides and report using the feedback, then submit.

## 2. Final report: expand the checkpoint report

- **ACM format** (same template as before). No hard page limit; about **10 pages** is the guideline.
- **Informative title**, every member's name, and their **section (4502 / 5502)**.
- Tell one storyline from start to finish.

| Section | What the professor wants |
|---|---|
| Abstract | Short executive summary: the problem, methods, and key insights/contributions |
| Introduction | Motivation first (why this problem matters), then what we did. Polish it to reflect our final results |
| Related work | Expand it, cite **recent** work, and say how our work **differs and builds on it** |
| Methodology | The whole pipeline: data, preliminary analysis, preprocessing, methods. For every method say **why** we chose it, its pros and cons, and why it fits this data. Don't just list methods |
| Evaluation | Results shown clearly (figures, tables, curves). Metrics that fit the use case, **plus efficiency/scalability**. **Interpret** every result: expected or surprising? Why did method A beat B? |
| Discussion | Limitations, what worked and what didn't, challenges, direction changes, real-world use ("so what?"), future work grounded in our results. The professor's favorite section; put effort in |
| Conclusion | Restate the key results; think "the 3 messages we want remembered" |
| References | Up to date and complete: authors, title, venue, year, pages, URL |
| Appendix | (a) Statement that this is our work, **naming any AI tools and what we used them for**; (b) **individual contributions**, at least one bullet per member (start from [TEAM.md](TEAM.md#who-did-what-so-far)) |

## 3. Code + results zip

One zip file containing:
- **A README** saying what's in the zip.
- **Source code** (notebooks, scripts, `src/`) with short comments or docs on what each piece does. They won't run it, so it has to be readable.
- **Supporting results:** detailed outputs behind the report's claims (per-model metrics, execution traces, screenshots, extra plots).
- **Don't include** raw or cleaned data, compiled files, or executables.

This repo is most of the zip already. Before submitting: `git archive` (or zip the repo minus `archive/`, `cleaned_data/`, `venv/`), add a `results/` folder of key outputs, and update the README.

## Checkpoint feedback to fold in

See [PROJECT.md → Feedback to address](PROJECT.md#feedback-to-address): real-world or more recent data, the 30-day window choice, EDA visuals, reasoning behind preparation steps, class imbalance, usefulness.
