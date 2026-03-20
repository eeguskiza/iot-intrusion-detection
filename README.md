# IoT Intrusion Detection — Multi-Class Classification on CICIoT2023

Multi-class classification of network traffic in IoT environments using the [CICIoT2023](https://www.unb.ca/cic/datasets/iotdataset-2023.html) dataset, published by the Canadian Institute for Cybersecurity (CIC) at the University of New Brunswick.

**Authors:** Alexander Jauregui Orue, Eneko Alvarez Mendia, Erik Eguskiza Aranda

## Overview

The dataset contains ~46.7M network traffic records captured from a topology of 105 real IoT devices, with 46 numerical features per record. Each sample is labelled as benign traffic or one of 33 attack types grouped into 7 categories (DDoS, DoS, Recon, Web-based, Brute Force, Spoofing, Mirai). The dataset exhibits severe class imbalance (5751:1 ratio between majority and minority classes).

This project focuses on the 8-class category classification task, applying preprocessing, imbalance mitigation, and ensemble learning methods with hyperparameter optimization via Optuna.

## Repository Structure

```
iot-intrusion-detection/
├── data/                  # Dataset (not tracked by git)
├── notebooks/             # Jupyter notebooks (main deliverable)
├── scripts/               # Utility scripts
├── .gitignore
└── README.md
```

## Dataset

Download the dataset from **[Google Drive (public link)](https://drive.google.com/drive/folders/1MGxaiRKDMAt1TTeemXwLCGfygF-GjZE8?usp=sharing)** and place the CSV files in the `data/` directory.

Alternatively, run the download script:

```bash
python scripts/download_data.py
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Notebooks

| Notebook | Description |
|---|---|
| `00_data_exploration.ipynb` | Pure EDA: class distribution, data quality, outliers, correlations |
| `01_data_loading_sampling.ipynb` | Full load, stratified sampling, preprocessing, 70/15/15 split → parquet |
| `02_imbalance_analysis.ipynb` | Imbalance analysis, SMOTE, undersampling, class_weight comparison |
| `03_model_comparison.ipynb` | Ensemble methods (Bagging, Boosting, Stacking), Optuna HPT with MedianPruner |
| `04_results_discussion.ipynb` | Comparison tables, confusion matrices, lessons learned |

## Tech Stack

- Python 3.11, scikit-learn, XGBoost (GPU), imbalanced-learn, Optuna
- Hardware: Ryzen 7 9800X3D, 32GB RAM, RTX 5070 Ti (16GB VRAM)
