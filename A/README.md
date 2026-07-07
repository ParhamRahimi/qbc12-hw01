# HW01-A — Dockerized Airbnb Ops Pipeline

A small Python package that reads raw Airbnb listing data, handles PII, generates a neighbourhood-level summary, and runs the same workflow inside Docker.

## Pipeline

```
Raw CSV → PII Handling → Neighbourhood Summary → Validation → Report
```

## Requirements

- Python 3.10+
- Docker (optional, for containerized runs)

## Quick Start

### Local

```bash
pip install -e .
airbnb-ops run
```

### Docker

```bash
docker compose build
docker compose run --rm airbnb-ops
```

### DVC

```bash
dvc repro
```

## Outputs

| File | Description |
|------|-------------|
| `data/processed/airbnb_neighbourhood_summary.csv` | Aggregated neighbourhood stats |
| `reports/hw01_a_run_report.md` | Pipeline run report |

## Package Structure

```
src/airbnb_ops/
├── config.py      # Path configuration
├── extract.py     # CSV reader
├── pii.py         # PII removal & pseudonymization
├── transform.py   # GroupBy aggregation & segment join
├── validate.py    # Output validation
└── cli.py         # Typer CLI
```

## Author

Parham Rahimi — QBC12 MLOps Homework 01-A