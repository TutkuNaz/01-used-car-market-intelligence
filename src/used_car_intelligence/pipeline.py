from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

LISTING_YEAR = 2020
NUMERIC_FEATURES = ["year", "mileage", "tax", "mpg", "engineSize", "vehicle_age", "miles_per_year"]
CATEGORICAL_FEATURES = ["brand", "model", "transmission", "fuelType"]
TARGET = "price"
REQUIRED_COLUMNS = {
    "brand",
    "model",
    "year",
    "price",
    "transmission",
    "mileage",
    "fuelType",
    "tax",
    "mpg",
    "engineSize",
}


@dataclass(frozen=True)
class DataQuality:
    rows_raw: int
    rows_clean: int
    duplicates_removed: int
    null_cells_raw: int
    invalid_rows_removed: int


def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, DataQuality]:
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise ValueError(f"Input data is missing required columns: {', '.join(missing)}")

    raw = df.copy()
    data = df.copy()
    text_cols = ["brand", "model", "transmission", "fuelType"]
    for col in text_cols:
        data[col] = data[col].astype("string").str.strip()

    numeric_cols = ["year", "price", "mileage", "tax", "mpg", "engineSize"]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    before_dupes = len(data)
    data = data.drop_duplicates().copy()
    duplicates_removed = before_dupes - len(data)

    valid = (
        data["year"].between(1990, LISTING_YEAR)
        & data["price"].between(500, 200_000)
        & data["mileage"].between(0, 300_000)
        & data["mpg"].between(5, 200)
        & data["engineSize"].between(0.5, 8.0)
    )
    invalid_rows_removed = int((~valid).sum())
    data = data.loc[valid].copy()
    data["vehicle_age"] = LISTING_YEAR - data["year"]
    data["miles_per_year"] = np.where(
        data["vehicle_age"] > 0,
        data["mileage"] / data["vehicle_age"],
        data["mileage"],
    )
    data["price_per_10k_miles"] = data["price"] / np.maximum(data["mileage"], 1) * 10_000
    data = data.reset_index(drop=True)

    quality = DataQuality(
        rows_raw=len(raw),
        rows_clean=len(data),
        duplicates_removed=duplicates_removed,
        null_cells_raw=int(raw.isna().sum().sum()),
        invalid_rows_removed=invalid_rows_removed,
    )
    return data, quality


def write_sqlite(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        df.to_sql("used_cars", connection, if_exists="replace", index=False)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_used_cars_brand ON used_cars(brand)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_used_cars_year ON used_cars(year)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_used_cars_model ON used_cars(model)")


def _format_markdown_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows returned._"
    columns = [str(column) for column in frame.columns]
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = [
        "| " + " | ".join(_format_markdown_value(value) for value in row) + " |"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join([header, divider, *rows])


def write_sql_report(database_path: Path, query_path: Path, output_path: Path) -> None:
    """Execute the repository SQL queries and materialize their results as Markdown."""
    sections: list[str] = []
    script = query_path.read_text(encoding="utf-8")
    with sqlite3.connect(database_path) as connection:
        for index, block in enumerate(script.split(";"), start=1):
            statement = block.strip()
            if not statement:
                continue
            title = next(
                (
                    line.removeprefix("--").strip()
                    for line in statement.splitlines()
                    if line.strip().startswith("--")
                ),
                f"Query {index}",
            )
            result = pd.read_sql_query(statement, connection)
            sections.append(f"## {title}\n\n{_markdown_table(result)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "# Executed SQL results\n\n"
        "Generated by the reproducible analysis pipeline from the cleaned SQLite dataset.\n\n"
        + "\n\n".join(sections)
        + "\n",
        encoding="utf-8",
    )


def _preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=2)),
    ])
    return ColumnTransformer([
        ("num", numeric, NUMERIC_FEATURES),
        ("cat", categorical, CATEGORICAL_FEATURES),
    ])


def train_models(df: pd.DataFrame, random_state: int = 42) -> tuple[dict, Pipeline, pd.DataFrame]:
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=random_state
    )

    estimators = {
        "Median baseline": DummyRegressor(strategy="median"),
        "Linear regression": LinearRegression(),
        "Random forest": RandomForestRegressor(
            n_estimators=400,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
    }
    results: dict[str, dict[str, float]] = {}
    fitted: dict[str, Pipeline] = {}
    predictions = pd.DataFrame({"actual": y_test.reset_index(drop=True)})

    for name, estimator in estimators.items():
        model = Pipeline([("preprocess", _preprocessor()), ("model", estimator)])
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        results[name] = {
            "mae": float(mean_absolute_error(y_test, pred)),
            "rmse": float(mean_squared_error(y_test, pred) ** 0.5),
            "r2": float(r2_score(y_test, pred)),
        }
        fitted[name] = model
        predictions[name] = pred

    return results, fitted["Random forest"], predictions


def feature_importance(model: Pipeline, top_n: int = 15) -> pd.DataFrame:
    prep = model.named_steps["preprocess"]
    names = prep.get_feature_names_out()
    values = model.named_steps["model"].feature_importances_
    frame = pd.DataFrame({"feature": names, "importance": values})
    frame["feature"] = (
        frame["feature"]
        .str.replace("num__", "", regex=False)
        .str.replace("cat__", "", regex=False)
    )
    return frame.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)


def save_figures(
    df: pd.DataFrame,
    model_results: dict,
    importance: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    brand = df.groupby("brand", observed=True)["price"].median().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    brand.plot(kind="barh", ax=ax)
    ax.set(title="Median used-car price by brand", xlabel="Median listing price (£)", ylabel="Brand")
    fig.tight_layout()
    fig.savefig(output_dir / "median_price_by_brand.svg", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for brand_name, group in df.groupby("brand", observed=True):
        ax.scatter(group["mileage"], group["price"], alpha=0.6, s=24, label=brand_name)
    ax.set(title="Listing price versus mileage", xlabel="Mileage (miles)", ylabel="Price (£)")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(output_dir / "price_vs_mileage.svg", bbox_inches="tight")
    plt.close(fig)

    dep = df.groupby("vehicle_age", observed=True)["price"].median().reset_index()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(dep["vehicle_age"], dep["price"], marker="o")
    ax.set(title="Median price by vehicle age", xlabel="Vehicle age at listing (years)", ylabel="Median price (£)")
    fig.tight_layout()
    fig.savefig(output_dir / "depreciation_curve.svg", bbox_inches="tight")
    plt.close(fig)

    metrics = pd.DataFrame(model_results).T.sort_values("mae")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(metrics.index, metrics["mae"])
    ax.set(title="Price model comparison", xlabel="Test MAE (£)", ylabel="Model")
    fig.tight_layout()
    fig.savefig(output_dir / "model_mae.svg", bbox_inches="tight")
    plt.close(fig)

    imp = importance.sort_values("importance")
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.barh(imp["feature"], imp["importance"])
    ax.set(title="Random-forest feature importance", xlabel="Importance", ylabel="Feature")
    fig.tight_layout()
    fig.savefig(output_dir / "feature_importance.svg", bbox_inches="tight")
    plt.close(fig)


def summarize(df: pd.DataFrame, quality: DataQuality, model_results: dict, importance: pd.DataFrame) -> dict:
    brand_stats = (
        df.groupby("brand", observed=True)
        .agg(
            listings=("price", "size"),
            median_price=("price", "median"),
            median_mileage=("mileage", "median"),
            median_mpg=("mpg", "median"),
        )
        .sort_values("median_price", ascending=False)
    )
    age_stats = df.groupby("vehicle_age", observed=True)["price"].median().sort_index()
    first_age = int(age_stats.index.min())
    last_age = int(age_stats.index.max())
    return {
        "data_quality": quality.__dict__,
        "median_price": float(df["price"].median()),
        "median_mileage": float(df["mileage"].median()),
        "brand_count": int(df["brand"].nunique()),
        "model_count": int(df["model"].nunique()),
        "highest_median_price_brand": str(brand_stats.index[0]),
        "highest_median_price": float(brand_stats.iloc[0]["median_price"]),
        "lowest_median_price_brand": str(brand_stats.index[-1]),
        "lowest_median_price": float(brand_stats.iloc[-1]["median_price"]),
        "age_range": [first_age, last_age],
        "median_price_youngest_age": float(age_stats.loc[first_age]),
        "median_price_oldest_age": float(age_stats.loc[last_age]),
        "model_results": model_results,
        "top_features": importance.to_dict(orient="records"),
    }


def run(raw_path: Path, project_root: Path) -> dict:
    df = load_data(raw_path)
    clean, quality = clean_data(df)

    processed_dir = project_root / "data" / "processed"
    reports_dir = project_root / "reports"
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    processed_csv = processed_dir / "used_cars_clean.csv"
    database_path = processed_dir / "used_cars.sqlite"
    clean.to_csv(processed_csv, index=False)
    write_sqlite(clean, database_path)
    write_sql_report(
        database_path,
        project_root / "sql" / "business_analysis.sql",
        reports_dir / "sql_results.md",
    )

    model_results, rf_model, predictions = train_models(clean)
    predictions.to_csv(reports_dir / "model_predictions.csv", index=False)
    importance = feature_importance(rf_model)
    importance.to_csv(reports_dir / "feature_importance.csv", index=False)
    save_figures(clean, model_results, importance, reports_dir / "figures")
    summary = summarize(clean, quality, model_results, importance)
    (reports_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary
