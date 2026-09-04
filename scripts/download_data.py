"""Download and consolidate the CC0 UK used-car dataset from Kaggle.

No Kaggle API token is required for the public dataset download endpoint used here.
Raw files are intentionally git-ignored; the consolidated output is data/raw/used_cars.csv.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import urllib.request
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/adityadesai13/used-car-dataset-ford-and-mercedes"
FILES = {
    "audi.csv": "Audi",
    "bmw.csv": "BMW",
    "ford.csv": "Ford",
    "hyundi.csv": "Hyundai",
    "merc.csv": "Mercedes",
    "skoda.csv": "Skoda",
    "toyota.csv": "Toyota",
    "vauxhall.csv": "Vauxhall",
    "vw.csv": "Volkswagen",
}


def download() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(DATASET_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - fixed trusted URL
        payload = response.read()

    frames: list[pd.DataFrame] = []
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        members = {Path(name).name.lower(): name for name in archive.namelist()}
        missing = [name for name in FILES if name not in members]
        if missing:
            raise RuntimeError(f"Expected files missing from Kaggle archive: {missing}")
        for filename, brand in FILES.items():
            with archive.open(members[filename]) as handle:
                frame = pd.read_csv(handle)
            frame.insert(0, "brand", brand)
            frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)
    output = RAW_DIR / "used_cars.csv"
    combined.to_csv(output, index=False)
    print(f"Wrote {len(combined):,} rows to {output}")
    return output


if __name__ == "__main__":
    download()
