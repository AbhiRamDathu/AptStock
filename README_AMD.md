# AptStock — AMD ROCm Acceleration

## Overview

AptStock is an AI-powered inventory intelligence platform for retailers.

It forecasts product demand and helps retailers make replenishment decisions,
with the goal of reducing stockouts and excess inventory.

## AMD Acceleration

The AMD acceleration layer is implemented separately from the production
forecasting API.

The AMD engine uses PyTorch with ROCm on AMD Instinct GPUs.

The same forecasting mathematics are used for CPU and GPU execution so that
performance comparisons remain meaningful.

## Benchmark Workload

Synthetic retail demand data:

- 500 SKUs
- 180 historical days
- 15-day forecast horizon
- 90,000 demand records

For each SKU:

1. Calculate historical mean demand.
2. Calculate demand standard deviation.
3. Generate the 15-day forecast.
4. Calculate safety stock.

## CPU vs AMD GPU

The benchmark measures:

- CPU execution time
- AMD GPU execution time
- speedup
- PyTorch version
- ROCm version
- AMD GPU model

The AMD benchmark will be executed on AMD Developer Cloud using an AMD
Instinct GPU.

## Reproducibility

The benchmark is deterministic and uses a fixed random seed.

The production AptStock forecasting API remains separate from the AMD
benchmark/acceleration layer.

## Status

CPU benchmark: completed.

AMD ROCm benchmark: pending AMD Developer Cloud access.