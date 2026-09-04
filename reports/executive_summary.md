# Executive Summary — Used Car Market Intelligence

## Scope
This build validates an end-to-end used-car pricing pipeline on a 299-row development snapshot that follows the schema of the CC0 UK used-car source. Full-source metrics are not claimed.

## Findings
- Validation median price: **£16,520**; median mileage: **28,277 miles**.
- SQL cohorts show average price falling from roughly **£22.1k** in the `<15k` mileage band to **£11.4k** in `50k+`, alongside higher average vehicle age.
- Random forest validation MAE: **£1,473**, versus **£4,401** for a median baseline.
- Mileage was the largest tree-model feature importance in this build.

## Decision Use
The project is suitable for market benchmarking and analyst review workflows. It should not be used as an automated vehicle valuation system without richer condition, trim, geography and realized-sales data.
