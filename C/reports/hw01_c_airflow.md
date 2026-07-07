# HW01-C — Airflow Scheduled Pipeline

**Author:** Parham Rahimi

## Note on credentials

My student ID was not in the credentials list provided on Quera.
The bootcamp admin instructed me to use a random credential from the list.
I'm using the `student_nazanin_hesari` database account (ID 1648).

## DAG

**DAG ID:** `qbc12_hw01_parham_rahimi_airbnb_pipeline`

**Airflow URL:** http://185.50.38.163:33013

## Pipeline flow

```
read_config → refresh_summary → validate_summary → choose_report_path
                                                          ↓
                                    ┌───────────────── branch ─────────────────┐
                                    ↓                                            ↓
                           write_success_report                       write_failure_report
```

## What each task does

| Task | Description |
|------|-------------|
| `read_config` | Reads DB credentials from Airflow Variables with fallback defaults |
| `refresh_summary` | Drops and recreates `student_nazanin_hesari.mv_airbnb_neighbourhood_summary` with 2 indexes |
| `validate_summary` | Checks: row_count > 0, null_neighbourhoods = 0, bad_prices = 0, bad_availability = 0 |
| `choose_report_path` | TaskFlow `@task.branch` — routes to success or failure |
| `write_success_report` | Logs passed checks |
| `write_failure_report` | Logs failures, then raises ValueError |

## Airflow Variables required

| Key | Value |
|-----|-------|
| `qbc12_db_host` | `185.50.38.163` |
| `qbc12_db_port` | `32112` |
| `qbc12_db_name` | `qbc12_airbnb` |
| `qbc12_db_user` | `student_nazanin_hesari` |
| `qbc12_db_password` | (from credentials file) |

Variables have fallback defaults so the DAG works even without them set.

## How to run

1. Deploy DAG to Airflow at http://185.50.38.163:33013
2. Find `qbc12_hw01_parham_rahimi_airbnb_pipeline`
3. Unpause and trigger manually
4. Check Graph view and logs

## Screenshots

- `screenshots/airflow_dag_graph.png` — DAG graph view
- `screenshots/airflow_success_run.png` — Successful run