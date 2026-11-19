"""Download the CMS DE-SynPUF Sample 1 CSVs used by this project into archive/.

Usage (from the repo root, with the venv active):
    python scripts/get_data.py               # copy into ./archive
    python scripts/get_data.py --dest PATH   # copy somewhere else

kagglehub downloads to its own cache (~/.cache/kagglehub) and this script copies
the 5 files the project uses into the destination. If Kaggle asks for credentials,
create an API token at kaggle.com -> Settings -> API and set KAGGLE_API_TOKEN, or
put kaggle.json in ~/.kaggle/. Never commit tokens or data.
"""
import argparse
import shutil
import sys
from pathlib import Path

DATASET = "anikannal/cms-synthetic-data"
FILES = [
    "DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv",
    "DE1_0_2009_Beneficiary_Summary_File_Sample_1.csv",
    "DE1_0_2010_Beneficiary_Summary_File_Sample_1.csv",
    "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv",
    "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv",
]
REPO_ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dest", type=Path, default=REPO_ROOT / "archive")
    args = parser.parse_args()
    dest = args.dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)

    missing = [f for f in FILES if not (dest / f).exists()]
    if not missing:
        print(f"All {len(FILES)} files already in {dest}")
        return 0

    import kagglehub  # imported late so --help works without it

    print(f"Downloading {DATASET} with kagglehub (first time is ~200 MB)...")
    cache = Path(kagglehub.dataset_download(DATASET))
    found = {p.name: p for p in cache.rglob("*.csv")}

    for name in missing:
        if name not in found:
            print(f"ERROR: {name} not in the Kaggle download at {cache}", file=sys.stderr)
            return 1
        shutil.copy2(found[name], dest / name)
        print(f"  copied {name}")

    print(f"Done. Raw data is in {dest}")
    print("Next: run notebooks/data-cleaning.ipynb (see docs/DATA.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
