# Data provenance

## Primary dataset

The project uses the **100,000 UK Used Car Data Set** by Aditya Desai on Kaggle, based on historical UK used-car listings.

- Source: https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes
- License: CC0 1.0 / Public Domain, as displayed by Kaggle
- Core fields: model, year, price, transmission, mileage, fuelType, tax, mpg, engineSize
- Repository-added field: brand, derived while consolidating manufacturer files
- Retrieval command: python scripts/download_data.py

Raw files are excluded from Git to keep clones small and make the retrieval boundary explicit. Review the upstream source and license before redistribution.

## Reproducibility

Running python scripts/download_data.py followed by python scripts/run_analysis.py rebuilds the cleaned CSV, SQLite database, SQL report, model diagnostics, metrics, and SVG figures. The small report assets committed to the repository are an illustrative project snapshot; newly generated statistics reflect the exact upstream files available at retrieval time.
