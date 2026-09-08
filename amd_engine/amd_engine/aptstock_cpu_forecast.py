import time
import numpy as np
import pandas as pd


FORECAST_DAYS = 15
SAFETY_STOCK_Z = 1.65


def create_sales_data(
    num_skus=500,
    days=180,
    seed=42,
):
    """
    Create deterministic synthetic retail demand data.

    This is only for benchmarking the forecasting engine.
    """

    rng = np.random.default_rng(seed)

    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=days,
        freq="D",
    )

    data = []

    for sku_id in range(num_skus):

        base_demand = rng.uniform(5, 100)
        trend = rng.uniform(-0.05, 0.15)

        for day_index, date in enumerate(dates):

            weekly = (
                1.0
                + 0.20 * np.sin(
                    2 * np.pi * day_index / 7
                )
            )

            demand = (
                base_demand
                * weekly
                * (1 + trend * day_index / days)
            )

            noise = rng.normal(
                0,
                base_demand * 0.10,
            )

            quantity = max(
                0,
                demand + noise,
            )

            data.append(
                {
                    "date": date,
                    "sku": f"SKU-{sku_id:05d}",
                    "quantity": quantity,
                }
            )

    return pd.DataFrame(data)


def cpu_forecast(df):
    """
    CPU reference implementation.

    IMPORTANT:
    The AMD GPU implementation must perform
    the same mathematical operations.
    """

    start = time.perf_counter()

    results = []

    for sku, group in df.groupby("sku"):

        daily = (
            group
            .groupby("date")["quantity"]
            .sum()
            .sort_index()
            .values
            .astype(np.float32)
        )

        mean_demand = np.mean(daily)

        std_demand = np.std(
            daily,
            ddof=0,
        )

        forecast = np.full(
            FORECAST_DAYS,
            mean_demand,
            dtype=np.float32,
        )

        safety_stock = (
            SAFETY_STOCK_Z
            * std_demand
        )

        results.append(
            {
                "sku": sku,
                "forecast_units": float(
                    forecast.sum()
                ),
                "safety_stock": float(
                    safety_stock
                ),
            }
        )

    elapsed = (
        time.perf_counter()
        - start
    )

    return results, elapsed


def main():

    print("=" * 70)
    print("APTSTOCK CPU FORECASTING BASELINE")
    print("=" * 70)

    print("\nGenerating workload...")

    df = create_sales_data(
        num_skus=500,
        days=180,
    )

    print(
        f"SKUs:  {df['sku'].nunique()}"
    )

    print(
        f"Days:  {df['date'].nunique()}"
    )

    print(
        f"Rows:  {len(df)}"
    )

    print("\nRunning CPU forecasting...")

    results, elapsed = cpu_forecast(df)

    print(
        f"Forecasts generated: {len(results)}"
    )

    print(
        f"CPU time: {elapsed:.4f} seconds"
    )

    print("\nSample result:")

    for result in results[:5]:
        print(result)

    print("\n" + "=" * 70)
    print("CPU BASELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()