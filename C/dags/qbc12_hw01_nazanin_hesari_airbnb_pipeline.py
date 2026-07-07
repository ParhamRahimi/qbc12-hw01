"""
DAG: qbc12_hw01_nazanin_hesari_airbnb_pipeline

Reads DB config from Airflow Variables, refreshes the materialized view,
validates it, and writes a success or failure report.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from sqlalchemy import create_engine, text

STUDENT_SCHEMA = "student_nazanin_hesari"
DAG_ID = "qbc12_hw01_nazanin_hesari_airbnb_pipeline"

MV_NAME = f'"{STUDENT_SCHEMA}".mv_airbnb_neighbourhood_summary'

REFRESH_SQL = f"""
DROP MATERIALIZED VIEW IF EXISTS {MV_NAME} CASCADE;

CREATE MATERIALIZED VIEW {MV_NAME} AS
WITH calendar_30 AS (
    SELECT
        cd.listing_id,
        AVG(cd.price) AS avg_calendar_price_30,
        AVG(CASE WHEN cd.available THEN 1.0 ELSE 0.0 END) AS availability_30_rate
    FROM core.calendar_day cd
    WHERE cd.date >= (SELECT MAX(cd2.date) - INTERVAL '30 days' FROM core.calendar_day cd2)
    GROUP BY cd.listing_id
),
calendar_365 AS (
    SELECT
        cd.listing_id,
        AVG(CASE WHEN cd.available THEN 1.0 ELSE 0.0 END) AS availability_365_rate
    FROM core.calendar_day cd
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
    ROUND(COALESCE(SUM(rc.total_reviews), 0)::NUMERIC / COUNT(lst.listing_id), 2)
        AS reviews_per_listing,
    ROUND(AVG(COALESCE(c30.availability_30_rate, 0)), 4) AS availability_30_rate,
    ROUND(AVG(COALESCE(c365.availability_365_rate, 0)), 4) AS availability_365_rate,
    ROUND(AVG(COALESCE(c30.avg_calendar_price_30, 0)), 2) AS avg_calendar_price_30
FROM core.listing lst
INNER JOIN core.neighbourhood nb ON lst.neighbourhood_id = nb.neighbourhood_id
LEFT JOIN calendar_30 c30 ON lst.listing_id = c30.listing_id
LEFT JOIN calendar_365 c365 ON lst.listing_id = c365.listing_id
LEFT JOIN review_counts rc ON lst.listing_id = rc.listing_id
GROUP BY nb.name
ORDER BY num_listings DESC;

CREATE INDEX IF NOT EXISTS idx_mv_airbnb_neighbourhood
    ON {MV_NAME} (neighbourhood);

CREATE INDEX IF NOT EXISTS idx_mv_airbnb_num_listings
    ON {MV_NAME} (num_listings DESC);
"""

default_args = {
    "owner": "nazanin_hesari",
    "depends_on_past": False,
    "start_date": datetime(2026, 7, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["qbc12", "hw01", "airbnb"],
) as dag:

    @task
    def read_config():
        """Read DB connection settings from Airflow Variables, with fallbacks."""
        def _v(key, default):
            try:
                return Variable.get(key)
            except Exception:
                return default

        return {
            "host": _v("qbc12_db_host", "185.50.38.163"),
            "port": _v("qbc12_db_port", "32112"),
            "dbname": _v("qbc12_db_name", "qbc12_airbnb"),
            "user": _v("qbc12_db_user", "student_nazanin_hesari"),
            "password": _v("qbc12_db_password", "AJsl6KVqVavYZm3bEO"),
            "schema": STUDENT_SCHEMA,
        }

    @task
    def refresh_summary(cfg: dict):
        """Drop and recreate the materialized view with indexes."""
        url = (
            f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
        )
        engine = create_engine(url)
        with engine.begin() as conn:
            conn.execute(text("SET statement_timeout = '120s'"))
            for stmt in REFRESH_SQL.split(";"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("--"):
                    conn.execute(text(stmt))

        # verify it has rows
        with engine.connect() as conn:
            row_count = conn.execute(
                text(f"SELECT count(*) FROM {MV_NAME}")
            ).scalar()
            col_count = len(
                conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema = :s AND table_name = 'mv_airbnb_neighbourhood_summary'"
                    ),
                    {"s": cfg["schema"]},
                ).fetchall()
            )

        engine.dispose()
        return {"refreshed": True, "row_count": row_count, "col_count": col_count}

    @task
    def validate_summary(cfg: dict):
        """Run validation checks on the materialized view."""
        url = (
            f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
        )
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SET statement_timeout = '30s'"))

            row_count = conn.execute(
                text(f"SELECT count(*) FROM {MV_NAME}")
            ).scalar()

            null_neighbourhoods = conn.execute(
                text(
                    f"SELECT count(*) FROM {MV_NAME} WHERE neighbourhood IS NULL"
                )
            ).scalar()

            bad_prices = conn.execute(
                text(
                    f"SELECT count(*) FROM {MV_NAME} WHERE avg_price < 0"
                )
            ).scalar()

            bad_availability = conn.execute(
                text(
                    f"SELECT count(*) FROM {MV_NAME} "
                    "WHERE availability_30_rate < 0 OR availability_30_rate > 1"
                )
            ).scalar()

        engine.dispose()

        checks = {
            "row_count": row_count,
            "null_neighbourhoods": null_neighbourhoods,
            "bad_prices": bad_prices,
            "bad_availability": bad_availability,
        }
        all_passed = (
            row_count > 0
            and null_neighbourhoods == 0
            and bad_prices == 0
            and bad_availability == 0
        )

        return {
            "passed": all_passed,
            "checks": checks,
        }

    @task.branch
    def choose_report_path(result: dict):
        """Branch to success or failure report based on validation."""
        if result["passed"]:
            return "write_success_report"
        return "write_failure_report"

    @task
    def write_success_report(result: dict):
        """Write a success run report to Airflow logs."""
        msg = (
            f"[SUCCESS] All validation checks passed.\n"
            f"  row_count: {result['checks']['row_count']}\n"
            f"  null_neighbourhoods: {result['checks']['null_neighbourhoods']}\n"
            f"  bad_prices: {result['checks']['bad_prices']}\n"
            f"  bad_availability: {result['checks']['bad_availability']}\n"
        )
        print(msg)
        return msg

    @task
    def write_failure_report(result: dict):
        """Write a failure report and raise ValueError."""
        msg = (
            f"[FAILURE] Validation checks did not pass.\n"
            f"  row_count: {result['checks']['row_count']} (>0 expected)\n"
            f"  null_neighbourhoods: {result['checks']['null_neighbourhoods']} (0 expected)\n"
            f"  bad_prices: {result['checks']['bad_prices']} (0 expected)\n"
            f"  bad_availability: {result['checks']['bad_availability']} (0 expected)\n"
        )
        print(msg)
        raise ValueError(f"Pipeline validation failed: {result['checks']}")

    # --- DAG structure ---
    config = read_config()
    refreshed = refresh_summary(config)
    validation = validate_summary(config)
    refreshed >> validation  # validate must run after refresh completes
    branch = choose_report_path(validation)
    branch >> [write_success_report(validation), write_failure_report(validation)]
