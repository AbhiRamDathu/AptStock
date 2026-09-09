import time
import numpy as np
import pandas as pd
import torch


FORECAST_DAYS = 15
SAFETY_STOCK_Z = 1.65
NUM_SKUS = 500
DAYS = 180
REPEATS = 5


def create_sales_data(
    num_skus=NUM_SKUS,
    days=DAYS,
    seed=42,
):
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
                + 0.20
                * np.sin(2 * np.pi * day_index / 7)
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


def prepare_matrix(df):

    grouped = []

    for _, group in df.groupby("sku"):

        daily = (
            group
            .groupby("date")["quantity"]
            .sum()
            .sort_index()
            .values
            .astype(np.float32)
        )

        grouped.append(daily)

    return np.asarray(
        grouped,
        dtype=np.float32,
    )


def cpu_workload(matrix):

    start = time.perf_counter()

    mean = matrix.mean(axis=1)

    std = matrix.std(
        axis=1,
        ddof=0,
    )

    forecast = mean * FORECAST_DAYS

    safety_stock = (
        SAFETY_STOCK_Z * std
    )

    elapsed = (
        time.perf_counter() - start
    )

    return (
        forecast,
        safety_stock,
        elapsed,
    )


def gpu_workload(matrix):

    device = torch.device("cuda")

    gpu_matrix = torch.from_numpy(
        matrix
    ).to(device)

    torch.cuda.synchronize()

    start = time.perf_counter()

    mean = gpu_matrix.mean(
        dim=1
    )

    std = gpu_matrix.std(
        dim=1,
        unbiased=False,
    )

    forecast = (
        mean * FORECAST_DAYS
    )

    safety_stock = (
        SAFETY_STOCK_Z * std
    )

    torch.cuda.synchronize()

    elapsed = (
        time.perf_counter() - start
    )

    return (
        forecast.cpu().numpy(),
        safety_stock.cpu().numpy(),
        elapsed,
    )


def main():

    print("=" * 70)
    print("APTSTOCK CPU vs AMD ROCm BENCHMARK")
    print("=" * 70)

    print(
        f"SKUs:          {NUM_SKUS}"
    )

    print(
        f"History days:  {DAYS}"
    )

    print(
        f"Forecast days: {FORECAST_DAYS}"
    )

    print(
        f"Rows:          {NUM_SKUS * DAYS}"
    )

    print(
        f"Repeats:       {REPEATS}"
    )

    print()

    df = create_sales_data()

    matrix = prepare_matrix(df)

    print(
        "Prepared matrix:",
        matrix.shape
    )

    print("\nRunning CPU...")

    cpu_times = []

    for _ in range(REPEATS):

        (
            cpu_forecast,
            cpu_safety,
            cpu_time,
        ) = cpu_workload(matrix)

        cpu_times.append(cpu_time)

    cpu_time = min(cpu_times)

    print(
        f"Best CPU time: {cpu_time:.6f}s"
    )

    print("\nChecking AMD GPU...")

    if not torch.cuda.is_available():

        print(
            "ERROR: CUDA/ROCm GPU not available."
        )

        print(
            "Run this benchmark inside "
            "AMD Developer Cloud."
        )

        return

    print(
        "PyTorch:",
        torch.__version__
    )

    print(
        "ROCm:",
        torch.version.hip
    )

    print(
        "GPU:",
        torch.cuda.get_device_name(0)
    )

    print("\nRunning AMD GPU...")

    gpu_times = []

    for _ in range(REPEATS):

        (
            gpu_forecast,
            gpu_safety,
            gpu_time,
        ) = gpu_workload(matrix)

        gpu_times.append(gpu_time)

    gpu_time = min(gpu_times)

    print(
        f"Best GPU time: {gpu_time:.6f}s"
    )

    speedup = (
        cpu_time / gpu_time
    )

    forecast_error = np.max(
        np.abs(
            cpu_forecast
            - gpu_forecast
        )
    )

    safety_error = np.max(
        np.abs(
            cpu_safety
            - gpu_safety
        )
    )

    print("\n" + "=" * 70)
    print("APTSTOCK BENCHMARK RESULT")
    print("=" * 70)

    print(
        f"CPU time:       {cpu_time:.6f}s"
    )

    print(
        f"AMD GPU time:   {gpu_time:.6f}s"
    )

    print(
        f"Speedup:        {speedup:.2f}x"
    )

    print(
        f"Max forecast error: "
        f"{forecast_error:.8f}"
    )

    print(
        f"Max safety error:   "
        f"{safety_error:.8f}"
    )

    print(
        f"GPU:            "
        f"{torch.cuda.get_device_name(0)}"
    )

    print(
        f"ROCm:           "
        f"{torch.version.hip}"
    )

    print("=" * 70)

    print("\nSample result:")

    for i in range(5):

        print(
            {
                "sku": f"SKU-{i:05d}",
                "forecast_units":
                    float(gpu_forecast[i]),
                "safety_stock":
                    float(gpu_safety[i]),
            }
        )


if __name__ == "__main__":
    main()