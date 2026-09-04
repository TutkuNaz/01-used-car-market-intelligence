from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "used_cars_clean.csv"
METRICS = ROOT / "reports" / "metrics.json"

st.set_page_config(page_title="Used Car Market Intelligence", layout="wide")
st.title("Used Car Market Intelligence")
st.caption("Pricing, mileage, vehicle age and model-performance exploration")

if not DATA.exists():
    st.error("Processed data not found. Run scripts/download_data.py and scripts/run_analysis.py first.")
    st.stop()

df = pd.read_csv(DATA)
metrics = json.loads(METRICS.read_text()) if METRICS.exists() else {}
brands = sorted(df["brand"].dropna().unique())
selected = st.sidebar.multiselect("Brands", brands, default=brands)
filtered = df[df["brand"].isin(selected)] if selected else df.iloc[0:0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", f"{len(filtered):,}")
c2.metric("Median price", f"£{filtered['price'].median():,.0f}" if len(filtered) else "—")
c3.metric("Median mileage", f"{filtered['mileage'].median():,.0f}" if len(filtered) else "—")
c4.metric("Models", f"{filtered['model'].nunique():,}")

left, right = st.columns(2)
with left:
    by_brand = filtered.groupby("brand", as_index=False)["price"].median().sort_values("price")
    st.plotly_chart(px.bar(by_brand, x="price", y="brand", orientation="h", title="Median price by brand"), use_container_width=True)
with right:
    st.plotly_chart(px.scatter(filtered, x="mileage", y="price", color="brand", hover_data=["model", "year"], title="Price vs mileage"), use_container_width=True)

age = filtered.groupby("vehicle_age", as_index=False)["price"].median()
st.plotly_chart(px.line(age, x="vehicle_age", y="price", markers=True, title="Median price by vehicle age"), use_container_width=True)

if metrics.get("model_results"):
    model_frame = pd.DataFrame(metrics["model_results"]).T.reset_index(names="model")
    st.subheader("Model validation")
    st.dataframe(model_frame.round(3), use_container_width=True)
    st.caption("Committed metrics may be development-validation outputs; see README for scope.")
