-- Brand-level market position
WITH brand_summary AS (
    SELECT brand,
           COUNT(*) AS listings,
           ROUND(AVG(price), 0) AS avg_price,
           ROUND(AVG(mileage), 0) AS avg_mileage,
           ROUND(AVG(mpg), 1) AS avg_mpg
    FROM used_cars
    GROUP BY brand
)
SELECT *, DENSE_RANK() OVER (ORDER BY avg_price DESC) AS price_rank
FROM brand_summary
ORDER BY price_rank;

-- Vehicle-age depreciation view
SELECT vehicle_age,
       COUNT(*) AS listings,
       ROUND(AVG(price), 0) AS avg_price,
       ROUND(AVG(mileage), 0) AS avg_mileage
FROM used_cars
GROUP BY vehicle_age
HAVING COUNT(*) >= 3
ORDER BY vehicle_age;

-- Model ranking within brands after a minimum observation threshold
WITH model_summary AS (
    SELECT brand, model, COUNT(*) AS listings,
           ROUND(AVG(price), 0) AS avg_price,
           ROUND(AVG(mileage), 0) AS avg_mileage
    FROM used_cars
    GROUP BY brand, model
    HAVING COUNT(*) >= 5
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY brand ORDER BY avg_price DESC) AS rn
    FROM model_summary
)
SELECT * FROM ranked WHERE rn <= 3 ORDER BY brand, rn;

-- Mileage segmentation for pricing analysis
SELECT
    CASE
        WHEN mileage < 15000 THEN '<15k'
        WHEN mileage < 30000 THEN '15k-30k'
        WHEN mileage < 50000 THEN '30k-50k'
        ELSE '50k+'
    END AS mileage_band,
    COUNT(*) AS listings,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(AVG(vehicle_age), 1) AS avg_vehicle_age
FROM used_cars
GROUP BY mileage_band
ORDER BY avg_price DESC;
