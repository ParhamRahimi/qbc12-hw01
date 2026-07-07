# EXPLAIN ANALYZE Observations — Baseline Query

## Query
The baseline query joins core.listing (10,480 rows), core.neighbourhood,
core.calendar_day (3,825,200 rows), and core.review (501,084 rows).

## Observations

1. **Sequential scan on calendar_day**: The CTE scanning calendar_day for the
   last 30 days performs a full scan over 3.8M rows. An index on (date, listing_id)
   would allow an index-only scan for the 30-day window.

2. **HashAggregate on review**: The review_counts CTE groups 501K rows by
   listing_id. A hash aggregate is used, which is appropriate given the cardinality,
   but could benefit from an index on (listing_id) for the initial scan.

3. **Nested Loop join for listing-to-calendar**: The left join from listing to
   calendar_30 uses a Nested Loop. With ~10K listings, this is manageable, but
   pre-aggregating calendar data would eliminate the repeated scan entirely.

## Summary
The main bottleneck is the calendar_day scan. Materializing the calendar and review
aggregations upfront eliminates redundant computation and makes dashboards fast.
