"""
Download CICIoT2023 dataset from Kaggle.
Requires: pip install kaggle + ~/.kaggle/kaggle.json configured.

Alternatively, download manually from the Google Drive link in README.md
and place the CSV files in data/.
"""

import os
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KAGGLE_DATASET = "madhavmalhotra/unb-cic-iot-dataset-2023"


def download_kaggle():
    DATA_DIR.mkdir(exist_ok=True)

    csv_files = list(DATA_DIR.glob("*.csv"))
    if csv_files:
        print(f"[OK] Found {len(csv_files)} CSV files in {DATA_DIR}. Skipping download.")
        return

    print(f"[INFO] Downloading {KAGGLE_DATASET} into {DATA_DIR} ...")
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "-p", str(DATA_DIR), "--unzip"],
            check=True,
        )
        print("[OK] Download complete.")
    except FileNotFoundError:
        print("[ERROR] kaggle CLI not found. Install with: pip install kaggle")
        print("        Then place your API token in ~/.kaggle/kaggle.json")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Download failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_kaggle()
