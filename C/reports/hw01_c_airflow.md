# HW01-C — Airflow Scheduled Pipeline

## DAG

**DAG ID:** `qbc12_hw01_nazanin_hesari_airbnb_pipeline`

**Airflow URL:** http://185.50.38.163:33013

**Login:** nazanin_hesari / Airflow password from credentials file

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
| `read_config` | Reads DB credentials from Airflow Variables (`qbc12_db_host`, `qbc12_db_port`, `qbc12_db_name`, `qbc12_db_user`, `qbc12_db_password`) |
| `refresh_summary` | Drops and recreates `student_nazanin_hesari.mv_airbnb_neighbourhood_summary` with 2 indexes |
| `validate_summary` | Checks: row_count > 0, null_neighbourhoods = 0, bad_prices = 0, bad_availability = 0 |
| `choose_report_path` | TaskFlow `@task.branch` — routes to success or failure |
| `write_success_report` | Logs passed checks |
| `write_failure_report` | Logs failures, then raises ValueError |

## Airflow Variables required

Set these in Airflow (Admin → Variables):

- `qbc12_db_host`
- `qbc12_db_port`
- `qbc12_db_name`
- `qbc12_db_user`
- `qbc12_db_password`

## How to run

1. Log in to Airflow at http://185.50.38.163:33013
2. Find `qbc12_hw01_nazanin_hesari_airbnb_pipeline`
3. Unpause it
4. Trigger manually (play button)
5. Check Graph view and logs

## Screenshots

- `screenshots/airflow_dag_graph.png` — DAG graph view showing all tasks
- `screenshots/airflow_success_run.png` — Successful run with green tasks