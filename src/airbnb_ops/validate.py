import pandas as pd

FORBIDDEN_COLUMNS = [
    "host_name", "host_id", "reviewer_name",
    "reviewer_id", "listing_url", "host_url",
]

REQUIRED_OUTPUT_COLUMNS = [
    "neighbourhood", "num_listings", "avg_price", "median_price",
    "avg_minimum_nights", "availability_365_avg", "total_reviews",
    "reviews_per_listing", "tourism_segment", "priority_level",
]


def validate_summary(summary):
    if summary.empty:
        raise ValueError("Output is empty")

    missing = [c for c in REQUIRED_OUTPUT_COLUMNS if c not in summary.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in FORBIDDEN_COLUMNS:
        if col in summary.columns:
            raise ValueError(f"PII leak: {col}")

    if summary["neighbourhood"].isnull().any():
        raise ValueError("Null neighbourhood found")

    if (summary["num_listings"] <= 0).any():
        raise ValueError("num_listings has zero or negative values")

    if (summary["avg_price"] < 0).any():
        raise ValueError("avg_price is negative")

    if ((summary["availability_365_avg"] < 0) | (summary["availability_365_avg"] > 365)).any():
        raise ValueError("availability_365_avg out of [0, 365] range")
