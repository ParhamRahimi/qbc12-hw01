# HW01-B — SQL Performance Report

## Schema

- **Database**: qbc12_airbnb (PostgreSQL 16)
- **Student schema**: `student_nazanin_hesari`
- **Core tables**: listing (10,480), calendar_day (3,825,200), review (501,084),
  neighbourhood, host

## Baseline Query

Joins listing, neighbourhood, calendar_day (30-day and 365-day windows),
and review tables with three CTEs. See `sql/01_baseline_neighbourhood_summary.sql`.

## EXPLAIN ANALYZE

See `reports/baseline_explain_analyze.txt` and `reports/explain_notes.md`.

Key bottlenecks:
- Sequential scan over 3.8M calendar_day rows
- HashAggregate over 501K review rows per run
- No covering indexes for the join paths

## Optimization

Created materialized view `student_nazanin_hesari.mv_airbnb_neighbourhood_summary`
with 2 indexes (neighbourhood, num_listings DESC).

Dashboard reads a single pre-computed table instead of joining 4 tables.

## Latency Comparison

| Query | Best (s) | Avg (s) |
|-------|----------|---------|
| Baseline direct query | 0.4542 | 0.5097 |
| Materialized view read | 0.0803 | 0.1038 |

**Speedup**: 5.66x

## Metabase Dashboard

Dashboard: **QBC12 HW01 - nazanin_hesari - Airbnb Ops**

URL: http://185.50.38.163:33012 (login: nazanin_hesari@qbc12.local)

5 cards from `student_nazanin_hesari.mv_airbnb_neighbourhood_summary`:
1. Listings by neighbourhood (bar chart)
2. Average price by neighbourhood (bar chart)
3. Review activity by neighbourhood (bar chart)
4. Availability rate by neighbourhood (bar chart: availability_30_rate and availability_365_rate)
5. Top neighbourhoods table

Saved in Personal Collection.
