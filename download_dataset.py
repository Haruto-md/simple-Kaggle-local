from utils.kaggle_download import download_competition_data

CMPETITION_NAME = "leonardo-airborne-object-recognition-challenge"

if __name__ == "__main__":
    try:
        download_competition_data(CMPETITION_NAME, target_dir=CMPETITION_NAME, force_download=False)
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")