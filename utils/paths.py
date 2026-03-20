"""Environment detection and path management."""

import os
from pathlib import Path

# Detect if running in Kaggle kernel
IS_KAGGLE = "KAGGLE_KERNEL_INTEGRATIONS_METADATA" in os.environ

# Base directories
if IS_KAGGLE:
    INPUT_DIR = Path("/kaggle/input")
    OUTPUT_DIR = Path("/kaggle/working")
    KAGGLE_INPUT_DIR = Path("/kaggle/input")
    LOCAL_INPUT_DIR = Path("/kaggle/input")
else:
    # ローカル環境
    PROJECT_ROOT = Path(__file__).parent.parent
    INPUT_DIR = PROJECT_ROOT / "input"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    KAGGLE_INPUT_DIR = INPUT_DIR / "kaggle"
    LOCAL_INPUT_DIR = INPUT_DIR / "local"

# Create directories if they don't exist (ローカル環境のみ)
if not IS_KAGGLE:
    KAGGLE_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
