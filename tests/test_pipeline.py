from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from used_car_intelligence.pipeline import clean_data


def test_clean_data_adds_features_and_removes_invalid_rows():
    frame = pd.DataFrame({
        "brand": [" Ford ", "Ford"], "model": ["Focus", "Focus"],
        "year": [2018, 1900], "price": [12000, 10], "transmission": ["Manual", "Manual"],
        "mileage": [20000, -1], "fuelType": ["Petrol", "Petrol"], "tax": [145, 0],
        "mpg": [50.0, 1.0], "engineSize": [1.5, 0.0],
    })
    clean, quality = clean_data(frame)
    assert len(clean) == 1
    assert clean.loc[0, "brand"] == "Ford"
    assert "vehicle_age" in clean.columns
    assert quality.invalid_rows_removed == 1
