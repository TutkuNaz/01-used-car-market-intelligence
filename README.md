# Used Car Market Intelligence

Pricing, mileage, depreciation-pattern and resale-value analysis for the UK used-car market, with SQL analysis, a reproducible Python pipeline and a price-prediction benchmark.

> **Build status:** pipeline, tests, SQL, notebooks, figures and dashboard were validated end-to-end. The committed analytical outputs were generated on a **299-row development validation snapshot** of the source schema because the full remote dataset could not be downloaded inside the build runtime. Full-source statistics are deliberately not fabricated; `scripts/download_data.py` retrieves the complete CC0 dataset and regenerates the outputs.

## Overview

This project treats used-car pricing as a fleet economics problem rather than only a regression exercise. Vehicle acquisition cost matters, but so do mileage exposure, age, segment mix and expected resale position when vehicles leave a fleet.

## Business Problem

A mobility or fleet operator evaluating vehicles needs a repeatable way to answer:

- How does listing price vary with age and mileage?
- Which brands and models occupy different resale-price positions?
- How much predictive signal is available from basic vehicle attributes?
- Where does a simple price model make large errors, and therefore require caution?

The dataset contains public used-car listings only. It is not a transaction ledger and does not measure realized resale proceeds.

## Dataset

Primary source: **100,000 UK Used Car Data Set** on Kaggle.

- Source: https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes
- License: **CC0 1.0 / Public Domain**
- Fields used: `brand`, `model`, `year`, `price`, `transmission`, `mileage`, `fuelType`, `tax`, `mpg`, `engineSize`
- Raw data are not committed. Run `python scripts/download_data.py`.

See [`data/README.md`](data/README.md) for provenance and validation-scope details.

## Key Questions

1. How sharply does price position change across age and mileage bands?
2. Which brands have higher median listing prices in the observed sample?
3. Which models rank highest within each brand after a minimum sample threshold?
4. Can a transparent baseline be materially improved with linear and tree-based models?
5. Which features contribute most to the tree model's predictions?

## Methodology

1. Download and consolidate manufacturer files.
2. Standardize text and numeric types.
3. Remove exact duplicates and clearly invalid ranges.
4. Create `vehicle_age`, `miles_per_year` and a mileage-normalized pricing feature.
5. Materialize a SQLite analytical table.
6. Run SQL CTE/window/segmentation analyses.
7. Compare a median baseline, linear regression and random forest.
8. Save test metrics, feature importance, figures and dashboard outputs.

## Tech Stack

Python · pandas · NumPy · scikit-learn · SQLite · SQL · Matplotlib · Plotly · Streamlit · pytest · GitHub Actions

## Data Cleaning

The development validation run contained **299 rows**, **0 duplicate rows**, **0 null cells** and **0 rows outside the explicit validity rules**. Those are validation-snapshot metrics, not claims about the full Kaggle dataset.

Validation rules are implemented in [`src/used_car_intelligence/pipeline.py`](src/used_car_intelligence/pipeline.py), not hidden in notebook cells.

## Exploratory Data Analysis

![Median price by brand](reports/figures/median_price_by_brand.png)

![Price versus mileage](reports/figures/price_vs_mileage.png)

![Median price by vehicle age](reports/figures/depreciation_curve.png)

## Key Insights — Development Validation

- Median listing price in the validation snapshot was **£16,520** at a median mileage of **28,277 miles**.
- Mercedes had the highest observed brand median (**£19,470**) and Hyundai the lowest (**£11,055**) among the six brands present in the validation snapshot. This is a sample-composition result, not a universal brand-resale ranking.
- Average prices in the SQL mileage segments declined from about **£22.1k below 15k miles** to **£11.4k above 50k miles**, while average vehicle age increased at the same time. Mileage and age therefore should not be interpreted independently without modeling controls.
- The tree model assigns the largest feature importance to mileage in this validation run. Feature importance is predictive attribution, not a causal depreciation estimate.

## SQL Analysis

The SQL layer uses real analytical queries with CTEs, `CASE WHEN`, aggregation and window functions. Executed outputs are committed in [`reports/sql_results.md`](reports/sql_results.md).

Examples include:

- brand price ranking with `DENSE_RANK()`;
- vehicle-age cohorts;
- top models within each brand using `ROW_NUMBER()`;
- mileage-band pricing segmentation.

## Machine Learning

The same train/test split is used for all models.

| Model | Test MAE | RMSE | R² |
|---|---:|---:|---:|
| Median baseline | £4,401 | £5,764 | -0.071 |
| Linear regression | £1,617 | £2,157 | 0.850 |
| Random forest | **£1,473** | **£2,040** | **0.866** |

![Model comparison](reports/figures/model_mae.png)

![Feature importance](reports/figures/feature_importance.png)

These figures validate the pipeline on the development snapshot only. The repository intentionally avoids presenting them as full-dataset performance.

## Results

The validation run demonstrates that structured vehicle attributes can materially outperform a naive median-price baseline. The random forest reduced MAE by roughly **67%** versus the median baseline on the fixed validation split.

## Business Recommendations

- Use age and mileage together when evaluating expected resale position; they are strongly entangled in listing data.
- Compare models within similar age/mileage cohorts instead of using raw brand averages for procurement decisions.
- Treat predicted price as a benchmark or review signal, not an automated purchase/sale decision.
- Add service history, trim, location and realized transaction prices before using the model for operational valuation.

## Dashboard

A Streamlit application is available in [`dashboard/app.py`](dashboard/app.py). A build-validated interactive Plotly version is also included at [`dashboard/dashboard.html`](dashboard/dashboard.html).

Run Streamlit with:

```bash
streamlit run dashboard/app.py
```

## Repository Structure

```text
01-used-car-market-intelligence/
├── README.md
├── data/README.md
├── notebooks/
├── scripts/
├── src/used_car_intelligence/
├── sql/
├── dashboard/
├── reports/
│   └── figures/
├── tests/
└── .github/workflows/ci.yml
```

## How to Run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_data.py
python scripts/run_analysis.py
pytest -q
streamlit run dashboard/app.py
```

## Data License

The source dataset is marked **CC0 / Public Domain** by Kaggle. Repository source code and original written material are MIT licensed. The raw dataset remains outside Git history for repository hygiene and reproducibility.

## Limitations

- Listing price is not realized sale price.
- Dataset vintage is historical and does not represent the 2026 market.
- Trim, condition, service history and local market supply are limited or absent.
- The committed model metrics are from a 299-row development validation snapshot, not the complete source dataset.
- Random train/test splitting evaluates predictive fit in the same listing population; it is not a future-market backtest.

## Future Improvements

- Re-run and publish a versioned full-dataset benchmark in an environment with direct Kaggle access.
- Add geographically explicit market features where licensing permits.
- Use grouped or temporal validation if reliable listing dates become available.
- Add model calibration/error slices by brand, model and mileage cohort.
