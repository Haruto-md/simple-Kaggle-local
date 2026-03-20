from pathlib import Path
import json
import os
import random
import shutil
import time
from typing import Optional
from zipfile import ZipFile

import requests
from requests.exceptions import HTTPError
from tqdm import tqdm


def _has_kaggle_credentials() -> bool:
    kaggle_dir = Path.home() / ".kaggle"
    access_token = kaggle_dir / "access_token"
    kaggle_json = kaggle_dir / "kaggle.json"

    return any(
        [
            bool(
                Path(os.environ.get("KAGGLE_CONFIG_DIR", "")).exists()
                if os.environ.get("KAGGLE_CONFIG_DIR")
                else False
            ),
            bool(os.environ.get("KAGGLE_API_TOKEN")),
            bool(os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY")),
            access_token.exists(),
            kaggle_json.exists(),
        ]
    )


def _auth_help_message(competition_name: str) -> str:
    return (
        "Kaggle authentication is not configured. Use one of these options:\n"
        "1. export KAGGLE_API_TOKEN=...\n"
        "2. Create ~/.kaggle/access_token\n"
        "3. Create ~/.kaggle/kaggle.json (chmod 600 ~/.kaggle/kaggle.json)\n\n"
        "Then accept competition rules in browser:\n"
        f"https://www.kaggle.com/competitions/{competition_name}\n"
    )


def _get_kaggle_auth() -> tuple[str, str]:
    """Return Kaggle username/key from env or kaggle.json."""
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if username and key:
        return username, key

    config_dir = Path(os.environ.get("KAGGLE_CONFIG_DIR", Path.home() / ".kaggle"))
    kaggle_json_path = config_dir / "kaggle.json"
    if kaggle_json_path.exists():
        data = json.loads(kaggle_json_path.read_text(encoding="utf-8"))
        json_user = data.get("username")
        json_key = data.get("key")
        if json_user and json_key:
            return str(json_user), str(json_key)

    raise RuntimeError("KAGGLE_USERNAME/KAGGLE_KEY were not found.")


def _download_competition_archive(
    competition_name: str,
    archive_path: Path,
    max_retries: int = 6,
    split_size_mb: int = 4096,
) -> list[Path]:
    """Download competition archive in one streaming request with 429 retry."""
    username, key = _get_kaggle_auth()
    url = (
        "https://www.kaggle.com/api/v1/competitions/data/download-all/"
        f"{competition_name}"
    )

    part_path = archive_path.with_suffix(archive_path.suffix + ".part")
    delay = 2.0
    split_size_bytes = max(split_size_mb, 1) * 1024 * 1024

    for attempt in range(max_retries + 1):
        segment_paths: list[Path] = []
        try:
            with requests.get(url, auth=(username, key), stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))

                with tqdm(
                    total=total if total > 0 else None,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="Download",
                ) as pbar:
                    segment_index = 1
                    segment_bytes = 0
                    current_segment = archive_path.with_suffix(
                        archive_path.suffix + f".part{segment_index:03d}"
                    )
                    segment_paths.append(current_segment)
                    f = open(current_segment, "wb")
                    try:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if not chunk:
                                continue

                            if segment_bytes + len(chunk) > split_size_bytes and segment_bytes > 0:
                                f.close()
                                segment_index += 1
                                segment_bytes = 0
                                current_segment = archive_path.with_suffix(
                                    archive_path.suffix + f".part{segment_index:03d}"
                                )
                                segment_paths.append(current_segment)
                                f = open(current_segment, "wb")

                            f.write(chunk)
                            segment_bytes += len(chunk)
                            pbar.update(len(chunk))
                    finally:
                        f.close()

            return segment_paths
        except HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code != 429 or attempt == max_retries:
                raise

            if part_path.exists():
                part_path.unlink(missing_ok=True)
            for segment_path in segment_paths:
                segment_path.unlink(missing_ok=True)

            sleep_seconds = delay + random.uniform(0, 0.5)
            print(
                f"\nRate limited on archive download. "
                f"Retrying in {sleep_seconds:.1f}s ({attempt + 1}/{max_retries})..."
            )
            time.sleep(sleep_seconds)
            delay = min(delay * 2, 30)

    raise RuntimeError("Unexpected retry failure on archive download.")


def _merge_archive_segments(segment_paths: list[Path], archive_path: Path) -> None:
    if not segment_paths:
        raise RuntimeError("No archive segments to merge.")

    with open(archive_path, "wb") as merged:
        for segment_path in sorted(segment_paths):
            with open(segment_path, "rb") as segment_file:
                shutil.copyfileobj(segment_file, merged)

    for segment_path in segment_paths:
        segment_path.unlink(missing_ok=True)


def _extract_zip(archive_path: Path, output_path: Path) -> int:
    with ZipFile(archive_path, "r") as zf:
        members = zf.infolist()
        file_members = [m for m in members if not m.is_dir()]

        with tqdm(total=len(file_members), desc="Extract", unit="files") as pbar:
            for member in members:
                zf.extract(member, path=output_path)
                if not member.is_dir():
                    pbar.update(1)

        return len(file_members)


def download_competition_data(
    competition_name: str,
    target_dir: Optional[str] = None,
    force_download: bool = False,
    split_size_mb: int = 4096,
) -> Path:
    if target_dir is None:
        target_dir = competition_name

    output_path = Path("kaggle/input/competitions") / target_dir
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Downloading competition '{competition_name}'...")
    print(f"Target: {output_path}\n")

    try:
        if not _has_kaggle_credentials():
            raise RuntimeError(_auth_help_message(competition_name))

        archive_path = output_path / f"{competition_name}.zip"
        if archive_path.exists() and not force_download:
            print(f"Using existing archive: {archive_path}")
        else:
            print("Downloading full archive in one request...")
            segment_paths = _download_competition_archive(
                competition_name,
                archive_path,
                split_size_mb=split_size_mb,
            )
            print(f"Merging {len(segment_paths)} archive segments...")
            _merge_archive_segments(segment_paths, archive_path)

        if not archive_path.exists() or archive_path.stat().st_size == 0:
            raise RuntimeError(f"Archive is missing or empty: {archive_path}")

        print("Extracting ZIP...")
        file_count = _extract_zip(archive_path, output_path)
        if file_count == 0:
            raise RuntimeError(f"Extraction completed but no files found in: {output_path}")

        print(f"Extracted files: {file_count}")
        print(f"\n✓ Successfully downloaded to {output_path}")
        return output_path

    except RuntimeError:
        raise

    except HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        if status_code in (401, 403):
            raise RuntimeError(
                f"Failed to download competition '{competition_name}'.\n"
                f"HTTP {status_code}: Unauthorized/Forbidden.\n\n"
                + _auth_help_message(competition_name)
            ) from e
        if status_code == 429:
            raise RuntimeError(
                f"Failed to download competition '{competition_name}'.\n"
                "HTTP 429: Too Many Requests. Please wait and retry."
            ) from e
        raise RuntimeError(
            f"Failed to download competition '{competition_name}'.\n"
            f"Error: {e}\n"
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Failed to download competition '{competition_name}'.\n"
            f"Error: {e}\n"
        ) from e