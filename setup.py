"""
setup.py — One-time project setup
===================================
Run this once before launching the Streamlit app:
    python setup.py

Steps:
  1. Generate the synthetic dataset (data/train.csv)
  2. Install Python dependencies
  3. Train all ML models and save to /models/
"""

import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║        Sales Forecasting System — Project Setup              ║
╚══════════════════════════════════════════════════════════════╝

Dataset Reference:
  This project uses a synthetic dataset modeled after the
  publicly available Kaggle Superstore Sales dataset.

  Title   : Store Sales - Time Series Forecasting
  URL     : https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting
  Author  : Rohit Sahoo
  License : CC0 - Public Domain

  The synthetic data replicates the same schema, category
  hierarchy, regional structure, and seasonal patterns as
  the original Kaggle dataset.
"""

print(BANNER)

# ── Step 1: Generate dataset ────────────────────────────────────────────────
print("═" * 64)
print("STEP 1: Generating synthetic dataset …")
print("═" * 64)

from data.generate_data import generate_dataset
generate_dataset(n_rows=10_000, output_path=os.path.join(ROOT, "data", "train.csv"))

# ── Step 2: Install dependencies ─────────────────────────────────────────────
print("\n" + "═" * 64)
print("STEP 2: Installing Python dependencies …")
print("═" * 64)
req_file = os.path.join(ROOT, "requirements.txt")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file, "-q"])
print("✅ Dependencies installed.")

# ── Step 3: Train models ──────────────────────────────────────────────────────
print("\n" + "═" * 64)
print("STEP 3: Training ML models …")
print("═" * 64)
train_script = os.path.join(ROOT, "src", "train_models.py")
subprocess.check_call([sys.executable, train_script])

# ── Done ──────────────────────────────────────────────────────────────────────
print("\n" + "═" * 64)
print("✅  SETUP COMPLETE!")
print("═" * 64)
print("\nRun the app with:")
print("  streamlit run Home.py\n")
