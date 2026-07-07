import hashlib

import pandas as pd

DIRECT_PII_COLUMNS = ["host_name"]


def pseudonymize_value(value, salt="qbc12"):
    raw = f"{salt}_{value}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def handle_pii(df):
    df = df.copy()

    for col in DIRECT_PII_COLUMNS:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    if "host_id" in df.columns:
        df["host_key"] = df["host_id"].apply(lambda x: pseudonymize_value(x))
        df.drop(columns=["host_id"], inplace=True)

    return df
