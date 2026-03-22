"""
compute_sample_quota.py
=======================
Stage 1 of the sampling pipeline.

Reads only the 'label' column from all 169 CICIoT2023 CSV files, counts rows
per category across the full dataset, then computes per-category and per-file
quotas that preserve the exact class proportions.

Output: ../data/processed/sample_config.json
"""

import json
import glob
from pathlib import Path

import pandas as pd

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
TARGET_ROWS = 1_000_000   # only hardcoded number — edit here to change sample size

DATA_DIR      = Path(__file__).resolve().parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
GLOB_PATTERN  = str(DATA_DIR / 'part-*.csv')

LABEL_MAP = {
    'DDoS-ICMP_Flood':          'DDoS',
    'DDoS-UDP_Flood':           'DDoS',
    'DDoS-TCP_Flood':           'DDoS',
    'DDoS-PSHACK_Flood':        'DDoS',
    'DDoS-SYN_Flood':           'DDoS',
    'DDoS-RSTFINFlood':         'DDoS',
    'DDoS-SynonymousIP_Flood':  'DDoS',
    'DDoS-ACK_Fragmentation':   'DDoS',
    'DDoS-UDP_Fragmentation':   'DDoS',
    'DDoS-ICMP_Fragmentation':  'DDoS',
    'DDoS-SlowLoris':           'DDoS',
    'DDoS-HTTP_Flood':          'DDoS',
    'DoS-UDP_Flood':            'DoS',
    'DoS-SYN_Flood':            'DoS',
    'DoS-TCP_Flood':            'DoS',
    'DoS-HTTP_Flood':           'DoS',
    'Recon-PingSweep':          'Recon',
    'Recon-OSScan':             'Recon',
    'Recon-PortScan':           'Recon',
    'VulnerabilityScan':        'Recon',
    'Recon-HostDiscovery':      'Recon',
    'SqlInjection':             'Web-based',
    'CommandInjection':         'Web-based',
    'Backdoor_Malware':         'Web-based',
    'Uploading_Attack':         'Web-based',
    'XSS':                      'Web-based',
    'BrowserHijacking':         'Web-based',
    'DictionaryBruteForce':     'BruteForce',
    'DNS_Spoofing':             'Spoofing',
    'MITM-ArpSpoofing':         'Spoofing',
    'Mirai-greIp':              'Mirai',
    'Mirai-greEth':             'Mirai',
    'Mirai-udpplain':           'Mirai',
    'BenignTraffic':            'Benign',
}

CONSTANT_COLS  = ['ece_flag_number', 'cwr_flag_number', 'Telnet', 'SMTP', 'IRC', 'DHCP']
DROP_CORR_COLS = ['Srate']


# ──────────────────────────────────────────────────────────────
# Step functions
# ──────────────────────────────────────────────────────────────

def count_categories(files: list[str]) -> dict[str, int]:
    """
    Read only the 'label' column from each file and accumulate row counts
    per category across all files.

    Parameters
    ----------
    files : list of str
        Sorted list of CSV file paths.

    Returns
    -------
    dict mapping category name → total row count.
    """
    counts: dict[str, int] = {}

    for i, path in enumerate(files):
        chunk = pd.read_csv(path, usecols=['label'])
        chunk['category'] = chunk['label'].map(LABEL_MAP)

        for cat, n in chunk['category'].value_counts(dropna=True).items():
            counts[cat] = counts.get(cat, 0) + int(n)

        if (i + 1) % 20 == 0 or (i + 1) == len(files):
            print(f'  Counted {i + 1}/{len(files)} files ...')

    return counts


def compute_targets(counts: dict[str, int], target_rows: int) -> tuple[dict[str, float], dict[str, int]]:
    """
    Compute per-category proportions and integer targets that sum exactly to
    target_rows. Rounding remainder is assigned to the largest class.

    Parameters
    ----------
    counts : dict
        Category → full-dataset row count.
    target_rows : int
        Desired total sample size.

    Returns
    -------
    proportions : dict {category: float}
    targets     : dict {category: int}  — sums exactly to target_rows.
    """
    total = sum(counts.values())
    proportions = {cat: n / total for cat, n in counts.items()}

    targets = {cat: round(target_rows * p) for cat, p in proportions.items()}

    # Fix rounding so sum == target_rows exactly
    diff = target_rows - sum(targets.values())
    if diff != 0:
        largest = max(targets, key=targets.__getitem__)
        targets[largest] += diff

    return proportions, targets


def compute_quotas(targets: dict[str, int], n_files: int) -> dict[str, int]:
    """
    Divide per-category targets evenly across files.

    Minimum quota is 1 for any category whose target implies at least
    one row per file on average.

    Parameters
    ----------
    targets : dict {category: int}
    n_files : int

    Returns
    -------
    dict {category: int}  — rows to draw per file per category.
    """
    quotas: dict[str, int] = {}
    for cat, target in targets.items():
        q = target // n_files
        if q == 0 and target >= n_files:
            q = 1
        elif q == 0 and target > 0:
            q = 1          # at least 1 so minority classes are not zeroed out
        quotas[cat] = q
    return quotas


def print_summary(
    counts:       dict[str, int],
    proportions:  dict[str, float],
    targets:      dict[str, int],
    quotas:       dict[str, int],
    total_rows:   int,
    n_files:      int,
) -> None:
    """Print a formatted summary table to stdout."""
    header = f"{'Category':<18} {'Full N':>12} {'Proportion':>12} {'Target N':>10} {'Per-file quota':>14}"
    print()
    print(header)
    print('-' * len(header))
    for cat in sorted(counts, key=counts.__getitem__, reverse=True):
        print(
            f"{cat:<18} {counts[cat]:>12,} {proportions[cat]:>12.4%} "
            f"{targets[cat]:>10,} {quotas[cat]:>14,}"
        )
    print()
    print(f"  Full dataset rows : {total_rows:,}")
    print(f"  Files             : {n_files}")
    print(f"  TARGET_ROWS       : {TARGET_ROWS:,}")
    print(f"  Achieved total    : {sum(targets.values()):,}")
    print()


def save_config(
    counts:      dict[str, int],
    proportions: dict[str, float],
    targets:     dict[str, int],
    quotas:      dict[str, int],
    total_rows:  int,
    n_files:     int,
    out_path:    Path,
) -> None:
    """
    Serialise all sampling parameters to a JSON file.

    Parameters
    ----------
    out_path : Path
        Destination file (created or overwritten).
    """
    config = {
        "target_rows":              TARGET_ROWS,
        "n_files":                  n_files,
        "total_rows_full_dataset":  total_rows,
        "category_counts_full":     counts,
        "category_proportions":     proportions,
        "category_targets":         targets,
        "quota_per_file":           quotas,
    }
    out_path.write_text(json.dumps(config, indent=2))
    print(f'  Config saved → {out_path}')


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

def main() -> None:
    """Run all five stages and write sample_config.json."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(GLOB_PATTERN))
    if not files:
        raise FileNotFoundError(f'No CSV files found matching {GLOB_PATTERN}')
    n_files = len(files)
    print(f'\nFound {n_files} CSV files under {DATA_DIR}\n')

    # ── Stage 1: count ──────────────────────────────────────
    print('Stage 1 — counting categories ...')
    counts = count_categories(files)
    total_rows = sum(counts.values())

    # ── Stage 2: proportions & targets ──────────────────────
    print('\nStage 2 — computing targets ...')
    proportions, targets = compute_targets(counts, TARGET_ROWS)

    # ── Stage 3: per-file quotas ─────────────────────────────
    print('Stage 3 — computing per-file quotas ...')
    quotas = compute_quotas(targets, n_files)

    # ── Stage 4: summary ─────────────────────────────────────
    print_summary(counts, proportions, targets, quotas, total_rows, n_files)

    # ── Stage 5: save ────────────────────────────────────────
    out_path = PROCESSED_DIR / 'sample_config.json'
    save_config(counts, proportions, targets, quotas, total_rows, n_files, out_path)


if __name__ == '__main__':
    main()
