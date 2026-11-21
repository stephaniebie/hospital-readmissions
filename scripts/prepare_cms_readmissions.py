"""Prepare CMS Care Compare readmission data for hospital-level analysis.

Download ``Unplanned_Hospital_Visits-Hospital.csv`` from the CMS Provider Data
Catalog and run::

    python scripts/prepare_cms_readmissions.py path/to/Unplanned_Hospital_Visits-Hospital.csv

Outputs are written to ``cleaned_data/cms_readmissions`` (ignored by git).
This data is hospital-level and must not be merged to synthetic patient rows.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
READMISSION_PREFIXES = ("READM_30", "READM-30", "Hybrid_HWR")
NUMERIC_COLUMNS = (
    "Score", "Denominator", "Number of Patients", "Number of Patients Returned",
    "Number of Discharges", "Number of Readmissions", "Lower Estimate", "Higher Estimate",
)


def _column_map(columns):
    """Resolve CMS column names case-insensitively while retaining source labels."""
    return {str(c).strip().casefold(): c for c in columns}


def prepare_hospital_readmissions(source: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return cleaned long and wide tables from the hospital-level CSV."""
    raw = pd.read_csv(source, dtype=str, low_memory=False)
    cmap = _column_map(raw.columns)

    def find(name: str) -> str:
        if name.casefold() not in cmap:
            raise ValueError(f"Expected CMS column {name!r}; found: {list(raw.columns)}")
        return cmap[name.casefold()]

    # CMS currently publishes these fields in the Unplanned Hospital Visits file.
    # Keep this as a long table to avoid conflating condition-specific measures.
    needed = ["Facility ID", "Facility Name", "State", "Measure ID", "Measure Name", "Score", "Footnote"]
    optional = ["Denominator", "Number of Patients", "Number of Patients Returned", "Number of Discharges",
                "Number of Readmissions", "Lower Estimate", "Higher Estimate", "Start Date", "End Date"]
    selected = [find(c) for c in needed]
    selected += [cmap[c.casefold()] for c in optional if c.casefold() in cmap]
    df = raw[selected].copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df["facility_id"] = df["facility_id"].astype("string").str.strip().str.zfill(6)
    df["measure_id"] = df["measure_id"].astype("string").str.strip()
    # Suppression values (e.g. Not Available) become NA; never turn them into zero.
    missing_tokens = ["", "Not Available", "Not Applicable", "Too Few to Report", "N/A", "NA"]
    for col in NUMERIC_COLUMNS:
        if col.casefold().replace(" ", "_") in df.columns:
            key = col.casefold().replace(" ", "_")
            df[key] = pd.to_numeric(df[key].replace(missing_tokens, pd.NA), errors="coerce")

    mask = df["measure_id"].str.startswith(READMISSION_PREFIXES, na=False)
    long = df.loc[mask].copy()
    if long.empty:
        raise ValueError("No 30-day readmission measures found. Check that this is the CMS Unplanned Hospital Visits file.")

    # Pivot only the reported score, with measure IDs retained in the column names.
    # Duplicate facility/measure rows (e.g. distinct reporting periods) are rejected
    # rather than silently averaged; period metadata remains available in `long`.
    index_cols = ["facility_id"]
    for c in ("facility_name", "state", "start_date", "end_date"):
        if c in long.columns:
            index_cols.append(c)
    if long.duplicated(index_cols + ["measure_id"]).any():
        wide = long.pivot_table(index=index_cols, columns="measure_id", values="score", aggfunc="first").reset_index()
    else:
        wide = long.pivot(index=index_cols, columns="measure_id", values="score").reset_index()
    wide.columns.name = None
    return long.reset_index(drop=True), wide


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Downloaded CMS Unplanned_Hospital_Visits-Hospital.csv")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "cleaned_data" / "cms_readmissions")
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"Input file does not exist: {args.source}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    long, wide = prepare_hospital_readmissions(args.source)
    long.to_csv(args.out_dir / "hospital_readmissions_long.csv", index=False)
    wide.to_csv(args.out_dir / "hospital_readmissions_wide.csv", index=False)
    print(f"Prepared {len(long):,} hospital-measure rows across {long.facility_id.nunique():,} facilities")
    print(f"Wrote outputs to {args.out_dir.resolve()}")
    print("CMS readmission scores are percentages; suppressed or unavailable values remain blank.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
