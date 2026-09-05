# Used Car Market Intelligence

[![CI](https://github.com/atasardacagan/01-used-car-market-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/atasardacagan/01-used-car-market-intelligence/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A reproducible Python, SQL, and machine-learning analysis of historical UK used-car pricing, mileage, and depreciation patterns.

Part of the [Automotive Open Data Hub](https://github.com/atasardacagan/automotive-data-portfolio), a curated collection of automotive datasets and reproducible starter analyses.

## What this project answers

- How do listing prices change across vehicle-age and mileage cohorts?
- Which brands and models occupy different price positions within comparable samples?
- How much predictive signal is available from common listing attributes?
- Where do straightforward pricing models outperform a median baseline?

## Data

Primary source: [100,000 UK Used Car Data Set](https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes), published on Kaggle under CC0 1.0 / Public Domain.

The source provides manufacturer-level CSV files with model, year, price, transmission, mileage, fuel type, tax, fuel economy, and engine size. Raw files are downloaded locally and are not committed to Git. See [data/README.md](data/README.md) for provenance and handling details.

## Analytical workflow

1. Download and consolidate the manufacturer source files.
2. Validate the required schema, normalize values, and remove invalid rows and exact duplicates.
3. Engineer vehicle age, miles per year, and mileage-normalized price features.
4. Materialize the cleaned data in both CSV and indexed SQLite formats.
5. Execute the version-controlled business queries and export their results to Markdown.
6. Compare a median baseline, linear regression, and random forest on one deterministic split.
7. Export metrics, predictions, feature importance, and SVG figures.

## Example outputs

![Median price by brand](reports/figures/median_price_by_brand.svg)

![Price versus mileage](reports/figures/price_vs_mileage.svg)

![Median price by vehicle age](reports/figures/depreciation_curve.svg)

The committed assets are an illustrative development snapshot. Brand medians are descriptive of the observed data and are not universal resale rankings. Age and mileage are correlated, so neither should be interpreted independently or causally.

## SQL analysis

The SQLite layer includes brand price rankings, age-cohort analysis, within-brand model rankings, and mileage-band segmentation. The pipeline executes [sql/business_analysis.sql](sql/business_analysis.sql) and regenerates [reports/sql_results.md](reports/sql_results.md), so the published SQL output remains tied to executable queries.

## Modeling

All models use the same deterministic train/test split. The repository compares a robust baseline with linear and nonlinear estimators and records MAE, RMSE, and R². Feature importance is provided as a predictive diagnostic, not a causal explanation.

![Model comparison](reports/figures/model_mae.svg)

![Feature importance](reports/figures/feature_importance.svg)

Use the estimates for benchmarking and analyst review rather than automated purchase or sale decisions. A production valuation system would also require trim, condition, service history, geography, time-aware validation, and realized transaction prices.

## Run locally

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python scripts/download_data.py
    python scripts/run_analysis.py
    python -m pytest -q

Windows activation: .venv\Scripts\activate

The analysis command creates missing output directories automatically and writes:

- data/processed/used_cars_clean.csv
- data/processed/used_cars.sqlite
- reports/sql_results.md
- reports/metrics.json
- reports/model_predictions.csv
- reports/feature_importance.csv
- five SVG figures in reports/figures

## Dashboard

Launch the Streamlit explorer after generating the processed data:

    streamlit run dashboard/app.py

## Repository layout

    01-used-car-market-intelligence/
    ├── data/                 # provenance plus local raw/processed boundaries
    ├── notebooks/            # exploratory analysis
    ├── scripts/              # data retrieval and pipeline entry point
    ├── src/used_car_intelligence/
    ├── sql/                  # executable business queries
    ├── dashboard/            # Streamlit application
    ├── reports/              # compact reference outputs
    ├── tests/                # unit and fresh-directory integration tests
    └── .github/              # CI and dependency updates

## Reproducibility and limitations

- The upstream data are historical listings, not current market quotes or realized transactions.
- Raw files are intentionally excluded; upstream availability and content can change.
- A random split measures fit within the observed population, not future-market performance.
- Missing trim, condition, service-history, and geographic variables constrain interpretation.
- CI tests Python 3.11 and 3.12, including a complete synthetic-data run from a fresh directory.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for the validation checklist. Report vulnerabilities privately using [SECURITY.md](SECURITY.md).

## License

Repository code and original written material are MIT licensed. The upstream dataset is separately published as CC0 / Public Domain; consult the source page for its current terms.
