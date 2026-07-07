-- Drop existing materialized view if any
DROP MATERIALIZED VIEW IF EXISTS "student_nazanin_hesari".mv_airbnb_neighbourhood_summary CASCADE;

-- Create materialized view for dashboard
CREATE MATERIALIZED VIEW "student_nazanin_hesari".mv_airbnb_neighbourhood_summary AS
WITH calendar_30 AS (
    SELECT
        cd.listing_id,
        AVG(cd.price) AS avg_calendar_price_30,
        AVG(CASE WHEN cd.available THEN 1.0 ELSE 0.0 END) AS availability_30_rate
    FROM core.calendar_day cd
    WHERE cd.date >= (SELECT MAX(cd2.date) - INTERVAL '30 days' FROM core.calendar_day cd2)
    GROUP BY cd.listing_id
),
review_counts AS (
    SELECT
        rv.listing_id,
        COUNT(*) AS total_reviews
    FROM core.review rv
    GROUP BY rv.listing_id
)
SELECT
    nb.name AS neighbourhood,
    COUNT(lst.listing_id) AS num_listings,
    ROUND(AVG(lst.listing_price), 2) AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lst.listing_price) AS median_price,
    ROUND(AVG(lst.minimum_nights), 2) AS avg_minimum_nights,
    COALESCE(SUM(rc.total_reviews), 0) AS total_reviews,
    ROUND(COALESCE(SUM(rc.total_reviews), 0)::NUMERIC / COUNT(lst.listing_id), 2) AS reviews_per_listing,
    ROUND(AVG(COALESCE(c30.availability_30_rate, 0)), 4) AS availability_30_rate,
    ROUND(AVG(COALESCE(c30.avg_calendar_price_30, 0)), 2) AS avg_calendar_price_30
FROM core.listing lst
INNER JOIN core.neighbourhood nb ON lst.neighbourhood_id = nb.neighbourhood_id
LEFT JOIN calendar_30 c30 ON lst.listing_id = c30.listing_id
LEFT JOIN review_counts rc ON lst.listing_id = rc.listing_id
GROUP BY nb.name
ORDER BY num_listings DESC;

-- Index for dashboard filtering
CREATE INDEX IF NOT EXISTS idx_mv_airbnb_neighbourhood
    ON "student_nazanin_hesari".mv_airbnb_neighbourhood_summary (neighbourhood);

-- Index for sorting
CREATE INDEX IF NOT EXISTS idx_mv_airbnb_num_listings
    ON "student_nazanin_hesari".mv_airbnb_neighbourhood_summary (num_listings DESC);
