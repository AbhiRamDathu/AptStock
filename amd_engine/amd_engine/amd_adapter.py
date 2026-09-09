import torch


FORECAST_DAYS = 15
SAFETY_STOCK_Z = 1.65


def amd_forecast_from_matrix(demand_matrix):
    """
    AMD/ROCm acceleration layer.

    demand_matrix:
        NumPy array shaped (SKUs, historical_days)

    Returns:
        forecast_units
        safety_stock
        elapsed_seconds
    """

    if not torch.cuda.is_available():
        raise RuntimeError(
            "AMD ROCm GPU not available. "
            "Run this module inside AMD Developer Cloud."
        )

    device = torch.device("cuda")

    matrix = torch.as_tensor(
        demand_matrix,
        dtype=torch.float32,
        device=device,
    )

    # Synchronize before timing GPU work.
    torch.cuda.synchronize()

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()

    mean_demand = matrix.mean(dim=1)
    std_demand = matrix.std(dim=1, unbiased=False)

    forecast_units = mean_demand * FORECAST_DAYS
    safety_stock = SAFETY_STOCK_Z * std_demand

    end.record()

    torch.cuda.synchronize()

    elapsed_seconds = start.elapsed_time(end) / 1000.0

    return (
        forecast_units,
        safety_stock,
        elapsed_seconds,
    )


def get_amd_runtime_info():

    if not torch.cuda.is_available():
        return {
            "available": False,
            "device": None,
            "pytorch": torch.__version__,
            "rocm": torch.version.hip,
        }

    return {
        "available": True,
        "device": torch.cuda.get_device_name(0),
        "pytorch": torch.__version__,
        "rocm": torch.version.hip,
    }
