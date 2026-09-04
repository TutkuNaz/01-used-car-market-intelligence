# Data provenance

## Primary dataset

**100,000 UK Used Car Data Set** by Aditya Desai (Kaggle), based on scraped UK used-car listings.

- Source: https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes
- License: **CC0 1.0 / Public Domain** as displayed by Kaggle.
- Core fields: `model`, `year`, `price`, `transmission`, `mileage`, `fuelType`, `tax`, `mpg`, `engineSize`.
- This repository adds `brand` while consolidating manufacturer files.
- Retrieval workflow: `python scripts/download_data.py`.
- Raw data are deliberately excluded from Git history even though CC0 permits redistribution. This keeps clones small and makes source provenance explicit.

## Development validation

The repository was quality-checked in the build environment with a 299-row development snapshot derived from the same schema. Figures and metrics committed in `reports/` are explicitly labeled as **development validation outputs** and must not be interpreted as full-dataset statistics. Running the documented download and analysis commands regenerates all outputs from the full source dataset.
