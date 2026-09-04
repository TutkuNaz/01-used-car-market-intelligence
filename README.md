# Used Car Market Intelligence

A reproducible analysis of used-car pricing, mileage and depreciation patterns using Python, SQL and machine learning.

## Objective

The project examines how vehicle age, mileage and model characteristics relate to listing prices, with a focus on resale-value benchmarking and fleet-oriented decision support.

Key questions:

- How does price change across age and mileage bands?
- Which brands and models occupy different price positions within comparable cohorts?
- How much predictive signal is available from basic vehicle attributes?
- Where do simple pricing models perform well or poorly?

## Data

Primary source: **100,000 UK Used Car Data Set** on Kaggle.

- Source: https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes
- License: **CC0 1.0 / Public Domain**
- Main fields: `brand`, `model`, `year`, `price`, `transmission`, `mileage`, `fuelType`, `tax`, `mpg`, `engineSize`
- Raw data are not stored in Git. Run `python scripts/download_data.py` to retrieve the source files.

The repository includes a small development-validation run to verify the full pipeline. Reported model metrics in this README refer to that validation run, not to the complete Kaggle dataset.

See [`data/README.md`](data/README.md) for provenance and data-handling details.

## Approach

1. Consolidate manufacturer-level source files.
2. Standardize categorical and numeric fields.
3. Remove duplicates and invalid records.
4. Engineer `vehicle_age`, `miles_per_year` and mileage-normalized pricing features.
5. Materialize the cleaned data in SQLite.
6. Analyze price and mileage segments with SQL.
7. Compare a median baseline, linear regression and random forest.
8. Export model metrics, feature importance, visualizations and dashboard assets.

## Stack

Python · pandas · NumPy · scikit-learn · SQLite · SQL · Matplotlib · Plotly · Streamlit · pytest · GitHub Actions

## Analysis

![Median price by brand](reports/figures/median_price_by_brand.svg)

![Price versus mileage](reports/figures/price_vs_mileage.svg)

![Median price by vehicle age](reports/figures/depreciation_curve.svg)

In the development-validation sample:

- median listing price: **£16,520**;
- median mileage: **28,277 miles**;
- average price declined from roughly **£22.1k** below 15k miles to **£11.4k** above 50k miles;
- vehicle age increased across the same mileage bands, so mileage should not be interpreted independently from age.

Brand-level medians are descriptive of the observed sample and should not be treated as universal resale rankings.

## SQL

The SQL layer covers:

- brand price rankings with `DENSE_RANK()`;
- age-cohort analysis;
- model ranking within brands using `ROW_NUMBER()`;
- mileage-band pricing segmentation.

Executed results are available in [`reports/sql_results.md`](reports/sql_results.md).

## Modeling

All models use the same train/test split.

| Model | Test MAE | RMSE | R² |
|---|---:|---:|---:|
| Median baseline | £4,401 | £5,764 | -0.071 |
| Linear regression | £1,617 | £2,157 | 0.850 |
| Random forest | **£1,473** | **£2,040** | **0.866** |

![Model comparison](reports/figures/model_mae.svg)

![Feature importance](reports/figures/feature_importance.svg)

On the validation split, the random forest reduced MAE by approximately **67%** relative to the median baseline. Feature importance is used as a predictive diagnostic and is not interpreted causally.

## Business Interpretation

- Age and mileage should be evaluated together when comparing resale position.
- Brand averages are most useful when vehicles are compared within similar age and mileage cohorts.
- Model predictions are better suited to benchmarking and review than automated purchase or sale decisions.
- A production valuation model would benefit from trim, condition, service history, geography and realized transaction prices.

## Dashboard

The Streamlit application in [`dashboard/app.py`](dashboard/app.py) supports interactive filtering and model-result review.

```bash
streamlit run dashboard/app.py
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_data.py
python scripts/run_analysis.py
pytest -q
```

## Repository Layout

```text
01-used-car-market-intelligence/
├── data/
├── notebooks/
├── scripts/
├── src/used_car_intelligence/
├── sql/
├── dashboard/
├── reports/
├── tests/
└── .github/workflows/ci.yml
```

## Limitations

- Listing price is not realized transaction price.
- The source is historical and does not represent the current market.
- Trim, vehicle condition, service history and geography are limited or absent.
- Published model metrics are from the development-validation sample.
- Random train/test splitting measures fit within the observed population rather than future-market performance.

## License

The source dataset is published as **CC0 / Public Domain**. Repository code and original written material are MIT licensed.
