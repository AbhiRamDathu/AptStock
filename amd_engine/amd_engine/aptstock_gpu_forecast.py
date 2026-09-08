import time
import numpy as np
import pandas as pd
import torch


def create_sales_data(num_skus=500, days=180, seed=42):
    rng = np.random.default_rng(seed)

    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=days,
        freq="D"
    )

    data = []

    for sku_id in range(num_skus):
        base_demand = rng.uniform(5, 100)
        trend = rng.uniform(-0.05, 0.15)

        for day_index, date in enumerate(dates):
            weekly = 1.0 + 0.20 * np.sin(
                2 * np.pi * day_index / 7
            )

            demand = (
                base_demand
                * weekly
                * (1 + trend * day_index / days)
            )

            noise = rng.normal(0, base_demand * 0.10)

            quantity = max(0, demand + noise)

            data.append({
                "date": date,
                "sku": f"SKU-{sku_id:05d}",
                "quantity": quantity
            })

    return pd.DataFrame(data)


def gpu_workload(df):
    device = torch.device("cuda")

    grouped = []

    for _, group in df.groupby("sku"):
        daily = (
            group.groupby("date")["quantity"]
            .sum()
            .sort_index()
            .values
        )

        grouped.append(daily)

    matrix = torch.tensor(
        np.asarray(grouped),
        dtype=torch.float32,
        device=device
    )

    torch.cuda.synchronize()
    start = time.perf_counter()

    mean = matrix.mean(dim=1)
    std = matrix.std(dim=1)

    forecast = mean * 15
    safety_stock = 1.65 * std

    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    return forecast, safety_stock, elapsed


def main():
    print("=" * 70)
    print("APTSTOCK AMD GPU FORECASTING ENGINE")
    print("=" * 70)

    print("PyTorch:", torch.__version__)
    print("ROCm:", torch.version.hip)
    print("GPU:", torch.cuda.get_device_name(0))

    df = create_sales_data(
        num_skus=500,
        days=180
    )

    print("SKUs:", df["sku"].nunique())
    print("Days:", df["date"].nunique())
    print("Rows:", len(df))

    print("\nRunning AMD GPU workload...")

    forecast, safety_stock, gpu_time = gpu_workload(df)

    print("\nGPU benchmark complete.")
    print(f"GPU time: {gpu_time:.6f} seconds")

    print("\nSample results:")

    for i in range(5):
        print({
            "sku": f"SKU-{i:05d}",
            "forecast_units": float(forecast[i]),
            "safety_stock": float(safety_stock[i])
        })

    print("\n" + "=" * 70)
    print("AMD GPU RUN COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()