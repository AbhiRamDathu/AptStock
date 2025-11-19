import pandas as pd


def preprocess_sales(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["sku", "store", "date"])
    # Resample to daily, forward fill missing days
    df = (
        df.set_index("date")
        .groupby(["sku", "store"])
        .apply(lambda g: g.resample("D").sum().fillna(method="ffill"))
        .reset_index()
    )
    return df
