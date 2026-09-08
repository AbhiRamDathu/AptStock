import time
import numpy as np
import pandas as pd
import torch


def create_sales_data(
    num_skus=500,
    days=180,
    seed=42
):
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

            quantity = max(
                0,
                demand + noise
            )

            data.append(
                {
                    "date": date,
                    "sku": f"SKU-{sku_id:05d}",
                    "quantity": quantity,
                }
            )

    return pd.DataFrame(data)


def cpu_workload(df):
    start = time.perf_counter()

    results = []

    for sku, group in df.groupby("sku"):
        daily = (
            group.groupby("date")["quantity"]
            .sum()
            .sort_index()
            .values
        )

        mean = np.mean(daily)
        std = np.std(daily)

        forecast = np.full(
            15,
            mean
        )

        safety_stock = 1.65 * std

        results.append(
            {
                "sku": sku,
                "forecast": forecast.sum(),
                "safety_stock": safety_stock,
            }
        )

    elapsed = time.perf_counter() - start

    return results, elapsed


def amd_workload(df):
    start = time.perf_counter()

    device = torch.device("cuda")

    grouped = []

    for sku, group in df.groupby("sku"):
        values = (
            group.groupby("date")["quantity"]
            .sum()
            .sort_index()
            .values
        )

        grouped.append(values)

    matrix = torch.tensor(
        np.asarray(grouped),
        dtype=torch.float32,
        device=device
    )

    mean = matrix.mean(dim=1)
    std = matrix.std(dim=1)

    forecast = mean.unsqueeze(1).repeat(1, 15)

    safety_stock = 1.65 * std

    torch.cuda.synchronize()

    elapsed = time.perf_counter() - start

    return forecast.sum(dim=1), safety_stock, elapsed


def main():

    print("=" * 70)
    print("APTSTOCK AMD ROCm FORECASTING BENCHMARK")
    print("=" * 70)

    print("PyTorch:", torch.__version__)
    print("ROCm:", torch.version.hip)
    print("GPU:", torch.cuda.get_device_name(0))

    print("\nGenerating workload...")

    df = create_sales_data(
        num_skus=500,
        days=180
    )

    print("SKUs:", df["sku"].nunique())
    print("Days:", df["date"].nunique())
    print("Rows:", len(df))

    print("\nRunning CPU baseline...")

    cpu_results, cpu_time = cpu_workload(df)

    print(
        f"CPU time: {cpu_time:.4f} seconds"
    )

    print("\nRunning AMD GPU workload...")

    torch.cuda.synchronize()

    gpu_forecast, gpu_safety, gpu_time = amd_workload(df)

    torch.cuda.synchronize()

    print(
        f"AMD GPU time: {gpu_time:.4f} seconds"
    )

    speedup = (
        cpu_time / gpu_time
        if gpu_time > 0
        else 0
    )

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"CPU time:       {cpu_time:.4f}s")
    print(f"AMD GPU time:   {gpu_time:.4f}s")
    print(f"Speedup:        {speedup:.2f}x")
    print(f"GPU:            {torch.cuda.get_device_name(0)}")
    print(f"ROCm:           {torch.version.hip}")

    print("=" * 70)


if __name__ == "__main__":
    main()
