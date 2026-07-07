import pandas as pd

REQUIRED_LISTING_COLUMNS = [
    "listing_id", "neighbourhood", "price",
    "minimum_nights", "availability_365", "number_of_reviews",
]


def build_neighbourhood_summary(listings, segments):
    missing = [c for c in REQUIRED_LISTING_COLUMNS if c not in listings.columns]
    if missing:
        raise ValueError(f"Missing columns in listings: {missing}")

    summary = listings.groupby("neighbourhood").agg(
        num_listings=("listing_id", "count"),
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        avg_minimum_nights=("minimum_nights", "mean"),
        availability_365_avg=("availability_365", "mean"),
        total_reviews=("number_of_reviews", "sum"),
    ).reset_index()

    summary["reviews_per_listing"] = (
        summary["total_reviews"] / summary["num_listings"]
    ).round(1)

    for col in ["avg_price", "median_price", "avg_minimum_nights", "availability_365_avg"]:
        summary[col] = summary[col].round(1)

    summary = summary.merge(segments, on="neighbourhood", how="left")
    summary["tourism_segment"] = summary["tourism_segment"].fillna("unknown")
    summary["priority_level"] = summary["priority_level"].fillna("unknown")

    return summary
