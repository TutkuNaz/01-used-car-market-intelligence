from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from used_car_intelligence.pipeline import clean_data, run


def _sample_frame(rows: int = 72) -> pd.DataFrame:
    brands = ["Ford", "BMW", "Toyota"]
    models = ["Focus", "Fiesta", "3 Series", "1 Series", "Corolla", "Yaris"]
    records = []
    for index in range(rows):
        records.append(
            {
                "brand": brands[index % len(brands)],
                "model": models[index % len(models)],
                "year": 2010 + index % 10,
                "price": 8_000 + index * 175 + (index % 3) * 900,
                "transmission": "Manual" if index % 2 else "Automatic",
                "mileage": 8_000 + index * 1_150,
                "fuelType": "Petrol" if index % 3 else "Diesel",
                "tax": 120 + index % 5 * 10,
                "mpg": 42 + index % 12,
                "engineSize": 1.2 + (index % 5) * 0.3,
            }
        )
    return pd.DataFrame.from_records(records)


def test_clean_data_adds_features_and_removes_invalid_rows():
    frame = pd.DataFrame(
        {
            "brand": [" Ford ", "Ford"],
            "model": ["Focus", "Focus"],
            "year": [2018, 1900],
            "price": [12000, 10],
            "transmission": ["Manual", "Manual"],
            "mileage": [20000, -1],
            "fuelType": ["Petrol", "Petrol"],
            "tax": [145, 0],
            "mpg": [50.0, 1.0],
            "engineSize": [1.5, 0.0],
        }
    )
    clean, quality = clean_data(frame)
    assert len(clean) == 1
    assert clean.loc[0, "brand"] == "Ford"
    assert "vehicle_age" in clean.columns
    assert quality.invalid_rows_removed == 1


def test_clean_data_reports_missing_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        clean_data(pd.DataFrame({"price": [12_000]}))


def test_run_creates_reproducible_outputs_from_a_fresh_directory(tmp_path: Path):
    raw_path = tmp_path / "fixture.csv"
    _sample_frame().to_csv(raw_path, index=False)
    (tmp_path / "sql").mkdir()
    source_sql = ROOT / "sql" / "business_analysis.sql"
    (tmp_path / "sql" / "business_analysis.sql").write_text(
        source_sql.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    summary = run(raw_path, tmp_path)

    assert summary["data_quality"]["rows_clean"] == 72
    assert (tmp_path / "data" / "processed" / "used_cars_clean.csv").is_file()
    assert (tmp_path / "data" / "processed" / "used_cars.sqlite").is_file()
    assert (tmp_path / "reports" / "sql_results.md").is_file()
    assert (tmp_path / "reports" / "metrics.json").is_file()
    assert (tmp_path / "reports" / "model_predictions.csv").is_file()
    assert len(list((tmp_path / "reports" / "figures").glob("*.svg"))) == 5
