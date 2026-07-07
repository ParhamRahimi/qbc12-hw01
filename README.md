# QBC12 — MLOps Homework 01

Parham Rahimi

## Overview

This repository contains three sections of a data pipeline homework:

| Part | Folder | Topic |
|------|--------|-------|
| A | `A/` | Dockerized Python package — PII handling, neighbourhood summary, DVC |
| B | `B/` | SQL performance analysis — baseline query, EXPLAIN ANALYZE, materialized view |
| C | `C/` | Airflow DAG — scheduled pipeline with branching and validation |

## Structure

```
A/
├── src/airbnb_ops/    # Python package (config, extract, pii, transform, validate, cli)
├── data/raw/          # Sample CSV inputs
├── data/processed/    # Pipeline output
├── reports/           # Run report
├── Dockerfile         # Container build
├── docker-compose.yml # Volume mounts
└── dvc.yaml           # DVC stage

B/
├── sql/               # 01_baseline query, 02_materialized view creation
├── reports/           # EXPLAIN plan, observations, performance report
└── screenshots/       # Metabase dashboard screenshots

C/
├── dags/              # Airflow DAG file
├── reports/           # Airflow run report
└── screenshots/       # Airflow graph and success run screenshots
```

## Note on Credentials

My student ID was not in the credentials list on Quera. The bootcamp admin instructed
me to use a random credential from the list. Database connections in Parts B and C use
the `student_nazanin_hesari` account. No passwords are included in this repository.