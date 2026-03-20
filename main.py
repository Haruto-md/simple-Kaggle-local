"""
Leonardo Airborne Object Recognition Challenge - Setup Script

This script helps set up the competition environment for local development.
"""

from utils import (
    leonardo_cfg,
    is_kaggle_authenticated,
    download_competition_data,
    IS_KAGGLE,
)
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))



def setup_environment():
    """Set up the competition environment."""
    print("=" * 70)
    print("LEONARDO AIRBORNE OBJECT RECOGNITION CHALLENGE - SETUP")
    print("=" * 70)
    
    print(f"\nEnvironment: {'Kaggle Kernel' if IS_KAGGLE else 'Local Development'}")
    
    if IS_KAGGLE:
        print("\n✓ Running in Kaggle environment")
        print("  Data should be automatically mounted at /kaggle/input/")
        return
    
    # Local setup
    print("\n--- Local Setup ---")
    
    # Create directories
    print("\n1. Creating directories...")
    leonardo_cfg.create_dirs()
    print(f"   ✓ Train dir: {leonardo_cfg.train_dir}")
    print(f"   ✓ Test dir: {leonardo_cfg.test_dir}")
    print(f"   ✓ Work dir: {leonardo_cfg.work_dir}")
    
    # Check Kaggle authentication
    print("\n2. Checking Kaggle API authentication...")
    if is_kaggle_authenticated():
        print("   ✓ Kaggle authenticated")
        return download_leonardo_data()
    else:
        print("   ✗ Kaggle API not authenticated")
        print_manual_setup_instructions()
        return False


def download_leonardo_data():
    """Download Leonardo challenge data using Kaggle API."""
    print("\n3. Downloading Leonardo competition data...")
    try:
        download_competition_data("leonardo-airborne-object-recognition-challenge")
        print("   ✓ Data downloaded successfully!")
        return True
    except RuntimeError as e:
        print(f"   ✗ Download failed: {e}")
        print_manual_setup_instructions()
        return False


def print_manual_setup_instructions():
    """Print instructions for manual data setup."""
    print("\n" + "=" * 70)
    print("MANUAL SETUP INSTRUCTIONS")
    print("=" * 70)
    print(f"""
To set up Leonardo competition data manually:

1. Download the data from Kaggle:
   https://www.kaggle.com/competitions/leonardo-airborne-object-recognition-challenge/data

2. Extract the data

3. Create the expected directory structure:
   {leonardo_cfg.train_dir}/
   ├── images/           (training images)
   └── annotations/      (training annotations)
   
   {leonardo_cfg.test_dir}/
   └── images/           (test images)

4. Copy files to these directories

5. Verify the setup by running:
   python main.py --verify

Classes in this competition:
{chr(10).join(f"  - {cls}" for cls in leonardo_cfg.classes)}
""")


def verify_setup():
    """Verify that the competition data is properly set up."""
    print("\n--- Verifying Setup ---")
    
    checks = {
        "Train directory exists": leonardo_cfg.train_dir.exists(),
        "Test directory exists": leonardo_cfg.test_dir.exists(),
        "Train images exist": (leonardo_cfg.train_dir / "images").exists(),
        "Train CSV exists": leonardo_cfg.train_csv.exists(),
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✓ All checks passed! Ready to start development.")
    else:
        print("\n✗ Some checks failed. Follow the manual setup instructions above.")
    
    return all_passed


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Leonardo Challenge Setup Script"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify the setup, don't download"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        success = verify_setup()
        sys.exit(0 if success else 1)
    else:
        success = setup_environment()
        if not IS_KAGGLE:
            verify_setup()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
