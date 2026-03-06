"""
Download CICIoT2023 dataset from Kaggle using kagglehub.
Requires: pip install kagglehub tqdm

Downloads all CSV files and stores them in data/.
"""

import shutil
import sys
from pathlib import Path

from tqdm import tqdm

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KAGGLE_DATASET = "madhavmalhotra/unb-cic-iot-dataset"


def download():
    DATA_DIR.mkdir(exist_ok=True)

    csv_files = list(DATA_DIR.glob("*.csv"))
    if csv_files:
        print(f"[OK] Found {len(csv_files)} CSV files in {DATA_DIR}. Skipping download.")
        return

    try:
        import kagglehub
    except ImportError:
        print("[ERROR] kagglehub not installed. Run: pip install kagglehub")
        sys.exit(1)

    print(f"[INFO] Downloading '{KAGGLE_DATASET}' via kagglehub ...")
    cache_path = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    print(f"[INFO] Dataset cached at: {cache_path}")

    # Find all CSVs in the cached download
    cached_csvs = list(cache_path.rglob("*.csv"))
    if not cached_csvs:
        print("[ERROR] No CSV files found in downloaded dataset.")
        sys.exit(1)

    print(f"[INFO] Copying {len(cached_csvs)} CSV files to {DATA_DIR} ...")
    for src in tqdm(cached_csvs, desc="Copying", unit="file"):
        dst = DATA_DIR / src.name
        shutil.copy2(src, dst)

    print(f"[OK] {len(cached_csvs)} CSV files ready in {DATA_DIR}")


if __name__ == "__main__":
    download()
