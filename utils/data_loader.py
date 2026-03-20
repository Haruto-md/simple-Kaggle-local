"""Unified data loading interface for both local and Kaggle environments."""

import pandas as pd
from pathlib import Path
from typing import Union, List, Optional
from .paths import KAGGLE_INPUT_DIR, LOCAL_INPUT_DIR


class CompetitionDataLoader:
    """
    Unified interface for loading data from kaggle or local directories.
    
    Usage:
        loader = CompetitionDataLoader("my-dataset")  # from input/kaggle/my-dataset
        df = loader.load_csv("train.csv")
        
        # Or from local
        loader = CompetitionDataLoader("train_data", source="local")
        df = loader.load_csv("data.csv")
    """
    
    def __init__(self, dataset_name: str, source: str = "kaggle"):
        """
        Initialize CompetitionDataLoader.
        
        Args:
            dataset_name: Name of the dataset directory
            source: "kaggle" or "local"
        """
        if source not in ["kaggle", "local"]:
            raise ValueError(f"source must be 'kaggle' or 'local', got {source}")
        
        self.source = source
        self.dataset_name = dataset_name
        
        if source == "kaggle":
            self.data_dir = KAGGLE_INPUT_DIR / dataset_name
        else:
            self.data_dir = LOCAL_INPUT_DIR / dataset_name
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self.data_dir}")
    
    def load_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        """Load CSV file from dataset directory."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        return pd.read_csv(filepath, **kwargs)
    
    def load_parquet(self, filename: str, **kwargs) -> pd.DataFrame:
        """Load Parquet file from dataset directory."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        return pd.read_parquet(filepath, **kwargs)
    
    def load_json(self, filename: str, **kwargs) -> Union[dict, list]:
        """Load JSON file from dataset directory."""
        import json
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, 'r') as f:
            return json.load(f, **kwargs)
    
    def list_files(self, pattern: str = "*") -> List[Path]:
        """List files in the dataset directory."""
        return list(self.data_dir.glob(pattern))
    
    def get_path(self, filename: str = "") -> Path:
        """Get the full path to a file in the dataset directory."""
        if filename:
            return self.data_dir / filename
        return self.data_dir


class OutputWriter:
    """Helper for writing outputs consistently."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize OutputWriter.
        
        Args:
            output_dir: Output directory path. If None, uses configured OUTPUT_DIR
        """
        from .paths import OUTPUT_DIR
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_csv(self, df: pd.DataFrame, filename: str, **kwargs) -> Path:
        """Save DataFrame as CSV."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, **kwargs)
        print(f"✓ Saved to {filepath}")
        return filepath
    
    def save_parquet(self, df: pd.DataFrame, filename: str, **kwargs) -> Path:
        """Save DataFrame as Parquet."""
        filepath = self.output_dir / filename
        df.to_parquet(filepath, **kwargs)
        print(f"✓ Saved to {filepath}")
        return filepath
    
    def save_json(self, data: Union[dict, list], filename: str, **kwargs) -> Path:
        """Save data as JSON."""
        import json
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, **kwargs)
        print(f"✓ Saved to {filepath}")
        return filepath
    
    def get_path(self, filename: str = "") -> Path:
        """Get the full path for output file."""
        if filename:
            return self.output_dir / filename
        return self.output_dir
