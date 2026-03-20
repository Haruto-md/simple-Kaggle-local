"""Configuration management for competitions with environment auto-detection."""

from pathlib import Path
from typing import Optional
from .paths import IS_KAGGLE, KAGGLE_INPUT_DIR, LOCAL_INPUT_DIR, OUTPUT_DIR


class CompetitionConfig:
    """
    Base configuration class for Kaggle competitions.
    Automatically switches paths between local and Kaggle environments.
    
    Usage:
        cfg = CompetitionConfig(
            comp_name="leonardo-airborne-object-recognition-challenge",
            classes=["Aircraft", "Helicopter", "Drone", ...],
            data_format="coco"  # or "csv", "xml", etc.
        )
        
        train_dir = cfg.train_dir  # Works in both environments!
        test_dir = cfg.test_dir
    """
    
    def __init__(
        self,
        comp_name: str,
        classes: list,
        comp_type: str = "competition",
        weights_dataset: Optional[str] = None,
    ):
        """
        Initialize competition configuration.
        
        Args:
            comp_name: Competition folder name (e.g., "titanic", "leonardo-...")
            classes: List of class names (excluding background for detection tasks)
            comp_type: "competition" or "dataset"
            weights_dataset: Optional Kaggle dataset name for pre-trained weights
        """
        self.comp_name = comp_name
        self.classes = classes
        self.comp_type = comp_type
        self.weights_dataset = weights_dataset
        self.is_kaggle = IS_KAGGLE
        
        # Set paths based on environment
        if IS_KAGGLE:
            if comp_type == "competition":
                self.comp_dir = Path(f"/kaggle/input/competitions/{comp_name}")
            else:
                self.comp_dir = Path(f"/kaggle/input/{comp_name}")
            self.work_dir = Path("/kaggle/working")
        else:
            self.comp_dir = KAGGLE_INPUT_DIR / comp_name
            self.work_dir = OUTPUT_DIR
        
        # Standard competition paths
        self.train_dir = self.comp_dir / "train"
        self.test_dir = self.comp_dir / "test"
        self.train_csv = self.comp_dir / "train.csv"
        self.test_csv = self.comp_dir / "test.csv"
        self.sample_sub = self.comp_dir / "sample_submission.csv"
        
        # Output paths
        self.submission_path = self.work_dir / "submission.csv"
        self.model_path = self.work_dir / "model.pth"
        self.predictions_path = self.work_dir / "predictions.pkl"
        self.checkpoint_dir = self.work_dir / "checkpoints"
    
    def create_dirs(self):
        """Create necessary directories (local only)."""
        if not IS_KAGGLE:
            self.train_dir.mkdir(parents=True, exist_ok=True)
            self.test_dir.mkdir(parents=True, exist_ok=True)
            self.work_dir.mkdir(parents=True, exist_ok=True)
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def get_weights_path(self, dataset_owner: Optional[str] = None, notebook_name: Optional[str] = None) -> Path:
        """
        Get path to pre-trained weights (Kaggle dataset or local cache).
        
        Args:
            dataset_owner: Kaggle username (e.g., "pestipeti")
            notebook_name: Notebook name containing weights
        
        Returns:
            Path to weights file or directory
        """
        if IS_KAGGLE:
            if dataset_owner and notebook_name:
                return Path(f"/kaggle/input/notebooks/{dataset_owner}/{notebook_name}")
            elif self.weights_dataset:
                return Path(f"/kaggle/input/{self.weights_dataset}")
            else:
                # Default Kaggle weights location
                return Path("/kaggle/input")
        else:
            # Local: store in input/local/weights/
            weights_dir = LOCAL_INPUT_DIR / "weights"
            weights_dir.mkdir(parents=True, exist_ok=True)
            return weights_dir
    
    def __repr__(self):
        return (
            f"CompetitionConfig(\n"
            f"  comp_name={self.comp_name}\n"
            f"  comp_dir={self.comp_dir}\n"
            f"  train_dir={self.train_dir}\n"
            f"  test_dir={self.test_dir}\n"
            f"  work_dir={self.work_dir}\n"
            f"  classes={self.classes}\n"
            f"  environment={'Kaggle' if IS_KAGGLE else 'Local'}\n"
            f")"
        )


class LeonardoConfig(CompetitionConfig):
    """Specialized config for Leonardo Airborne Object Recognition Challenge."""
    
    CLASSES = [
        "Aircraft",
        "Helicopter",
        "Drone",
        "GroundVehicle",
        "Ship",
        "Human",
        "Obstacle",
    ]
    
    def __init__(self, weights_dataset: Optional[str] = None):
        """
        Initialize Leonardo competition configuration.
        
        Args:
            weights_dataset: Optional Kaggle dataset name for Faster R-CNN weights
        """
        super().__init__(
            comp_name="leonardo-airborne-object-recognition-challenge",
            classes=self.CLASSES,
            comp_type="competition",
            weights_dataset=weights_dataset,
        )
        
        # Faster R-CNN specific paths
        self.annotations_dir = self.train_dir / "annotations"
        self.images_dir = self.train_dir / "images"
        self.test_images_dir = self.test_dir / "images"
        
        # Model-specific outputs
        self.model_path = self.work_dir / "fasterrcnn_model.pth"
        self.predictions_json = self.work_dir / "predictions.json"


# Backward compatibility: Create default instances for quick access
leonardo_cfg = LeonardoConfig()
