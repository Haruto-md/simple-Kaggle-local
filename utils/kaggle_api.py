"""Kaggle API wrapper for downloading datasets."""

import os
import subprocess
from pathlib import Path
from .paths import KAGGLE_INPUT_DIR, IS_KAGGLE
from typing import Optional


def _load_env_file():
    """Load .env file into environment variables."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def _get_kaggle_env() -> dict:
    """Get Kaggle environment variables for subprocess calls."""
    # Load .env first
    _load_env_file()
    
    env = os.environ.copy()
    
    # Map KAGGLE_API_TOKEN to KAGGLE_KEY if needed
    if "KAGGLE_API_TOKEN" in env and "KAGGLE_KEY" not in env:
        env["KAGGLE_KEY"] = env["KAGGLE_API_TOKEN"]
    
    return env


def _setup_kaggle_credentials() -> bool:
    """
    Setup Kaggle credentials from .env file.
    Creates ~/.config/kaggle/kaggle.json if token exists in .env
    
    Returns:
        True if credentials were set up successfully
    """
    import json
    
    _load_env_file()
    
    token = os.getenv("KAGGLE_API_TOKEN")
    if not token:
        return False
    
    # Create ~/.config/kaggle/ directory
    kaggle_dir = Path.home() / ".config" / "kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    
    # Create kaggle.json from token
    # Token format: KGAT_username_random
    credentials = {
        "username": "kaggle_user",
        "key": token
    }
    
    kaggle_json = kaggle_dir / "kaggle.json"
    with open(kaggle_json, 'w') as f:
        json.dump(credentials, f)
    
    # Set permissions (Kaggle API requires 600)
    kaggle_json.chmod(0o600)
    
    return True


def _check_kaggle_auth() -> bool:
    """Check if Kaggle API credentials are available."""
    # Load from .env first
    _load_env_file()
    
    # Check for Kaggle credentials
    has_token = os.getenv("KAGGLE_API_TOKEN")
    
    if has_token:
        # Try to setup credentials file
        _setup_kaggle_credentials()
        return True
    
    # Fall back to kaggle.json
    kaggle_json = Path.home() / ".config" / "kaggle" / "kaggle.json"
    return kaggle_json.exists()


def download_dataset_by_id(dataset_id: str, target_dir: Optional[str]=None) -> Path:
    """
    Download a Kaggle dataset by ID using Kaggle API.
    
    Args:
        dataset_id: Kaggle dataset ID (e.g., "owner/dataset-name")
        target_dir: Target directory name within input/kaggle/ (default: dataset name)
    
    Returns:
        Path to downloaded dataset
    
    Raises:
        RuntimeError: If kaggle CLI is not installed or credentials are missing
        subprocess.CalledProcessError: If download fails
    """
    if IS_KAGGLE:
        raise RuntimeError(
            "Cannot download datasets in Kaggle kernel. "
            "Dataset should already be mounted at /kaggle/input/"
        )
    
    if not _check_kaggle_auth():
        raise RuntimeError(
            "Kaggle API credentials not found.\n"
            "To enable automatic downloads:\n"
            "  1. Create .env file with: KAGGLE_API_TOKEN=your_token\n"
            "  2. Get token from: https://www.kaggle.com/settings/account\n\n"
            "Alternatively, download data manually and place it in:\n"
            f"  {KAGGLE_INPUT_DIR / (target_dir or dataset_id.split('/')[-1])}"
        )
    
    # Setup credentials file from .env
    _setup_kaggle_credentials()
    
    if target_dir is None:
        target_dir = dataset_id.split("/")[1]
    
    output_path = KAGGLE_INPUT_DIR / target_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading dataset '{dataset_id}' to {output_path}...")
    print("(This may take a while - progress will be shown below...)")
    
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset_id, "-p", str(output_path), "--unzip"],
            check=True,
            text=True,
            env=_get_kaggle_env(),
            timeout=3600  # 1 hour timeout
        )
        print(f"✓ Successfully downloaded to {output_path}")
        return output_path
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Download timeout (1 hour exceeded).\n"
            "The dataset is too large for automatic download.\n"
            f"Please download manually and extract to: {output_path}"
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Kaggle CLI is not installed. Install it with: pip install kaggle"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to download dataset '{dataset_id}'.\n"
            f"This may be due to:\n"
            f"  1. Dataset is very large (use manual download)\n"
            f"  2. Invalid Kaggle token\n"
            f"  3. Kaggle account restrictions"
        )


def download_competition_data(competition_name: str, target_dir: Optional[str] = None) -> Path:
    """
    Download competition data from Kaggle.
    
    Args:
        competition_name: Competition name (e.g., "titanic", "leonardo-airborne-...")
        target_dir: Target directory name (default: competition name)
    
    Returns:
        Path to downloaded data
    
    Example:
        >>> # Download Leonardo challenge data
        >>> download_competition_data("leonardo-airborne-object-recognition-challenge")
        Path('input/kaggle/leonardo-airborne-object-recognition-challenge')
    """
    if IS_KAGGLE:
        raise RuntimeError(
            "Cannot download in Kaggle kernel. "
            "Competition data should be mounted at /kaggle/input/"
        )
    
    if not _check_kaggle_auth():
        raise RuntimeError(
            "Kaggle API credentials not found.\n"
            "To enable automatic downloads:\n"
            "  1. Create .env file with: KAGGLE_API_TOKEN=your_token\n"
            "  2. Get token from: https://www.kaggle.com/settings/account\n\n"
            "Alternatively, download the competition manually and place it in:\n"
            f"  {KAGGLE_INPUT_DIR / (target_dir or competition_name)}"
        )
    
    # Setup credentials file from .env
    _setup_kaggle_credentials()
    
    if target_dir is None:
        target_dir = competition_name
    
    output_path = KAGGLE_INPUT_DIR / target_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading competition '{competition_name}' data to {output_path}...")
    print("(This may take a while - dataset is large. Progress will be shown below...)")
    
    try:
        # Download with real-time output (not captured)
        result = subprocess.run(
            ["kaggle", "competitions", "download", "-c", competition_name, "-p", str(output_path)],
            check=True,
            text=True,
            env=_get_kaggle_env(),
        )
        print(f"✓ Successfully downloaded to {output_path}")
        return output_path
    except FileNotFoundError:
        raise RuntimeError("Kaggle CLI is not installed. Install it with: pip install kaggle")

def is_kaggle_authenticated() -> bool:
    """
    Check if Kaggle API credentials are available.
    
    Returns:
        True if credentials exist, False otherwise
    """
    return _check_kaggle_auth()
