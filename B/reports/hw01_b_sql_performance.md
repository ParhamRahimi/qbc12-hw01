# HW01-B — SQL Performance Report

## Schema

- **Database**: qbc12_airbnb (PostgreSQL 16)
- **Student schema**: `student_nazanin_hesari`
- **Core tables**: listing (10,480), calendar_day (3,825,200), review (501,084),
  neighbourhood, host

## Baseline Query

```sql
WITH calendar_30 AS (
    SELECT listing_id,
           AVG(price) AS avg_calendar_price_30,
           AVG(CASE WHEN available THEN 1.0 ELSE 0.0 END) AS availability_30_rate
    FROM core.calendar_day
    WHERE date >= (SELECT MAX(date) - INTERVAL '30 days' FROM core.calendar_day)
    GROUP BY listing_id
),
review_counts AS (
    SELECT listing_id, COUNT(*) AS total_reviews
    FROM core.review
    GROUP BY listing_id
)
SELECT n.name AS neighbourhood,
       COUNT(l.listing_id) AS num_listings,
       ROUND(AVG(l.listing_price), 2) AS avg_price,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.listing_price) AS median_price,
       ROUND(AVG(l.minimum_nights), 2) AS avg_minimum_nights,
       COALESCE(SUM(r.total_reviews), 0) AS total_reviews,
       ROUND(COALESCE(SUM(r.total_reviews), 0)::NUMERIC / COUNT(l.listing_id), 2)
           AS reviews_per_listing,
       ROUND(AVG(COALESCE(c.availability_30_rate, 0)), 4) AS availability_30_rate
FROM core.listing l
INNER JOIN core.neighbourhood n ON l.neighbourhood_id = n.neighbourhood_id
LEFT JOIN calendar_30 c ON l.listing_id = c.listing_id
LEFT JOIN review_counts r ON l.listing_id = r.listing_id
GROUP BY n.name
ORDER BY num_listings DESC
```

## EXPLAIN ANALYZE Findings

See `reports/baseline_explain_analyze.txt` and `reports/explain_notes.md`.

Key findings:
- Calendar_day scan over 3.8M rows drives latency
- Review aggregation scans 501K rows per run
- Full table scans without covering indexes

## Optimization

Created `student_nazanin_hesari.mv_airbnb_neighbourhood_summary`
with two indexes (neighbourhood, num_listings DESC).
Dashboard reads from this single small table instead of joining 4 tables.

## Latency Comparison

| Query | Best (s) | Avg (s) |
|-------|----------|---------|
| Baseline direct query | 0.3966 | 0.4501 |
| Materialized view read | 0.0868 | 0.1083 |

**Speedup**: 4.57x

## Metabase Dashboard

Dashboard: **QBC12 HW01 - nazanin_hesari - Airbnb Ops**

URL: http://185.50.38.163:33012

5 cards using `student_nazanin_hesari.mv_airbnb_neighbourhood_summary`:
1. Listings by neighbourhood (bar chart)
2. Average price by neighbourhood (bar chart)
3. Review activity by neighbourhood (bar chart)
4. Availability rate by neighbourhood (bar chart)
5. Top neighbourhoods table

Save in Personal Collection.
