import torch
import time

print("=" * 60)
print("AptStock AMD Environment Test")
print("=" * 60)

print("PyTorch:", torch.__version__)
print("ROCm:", torch.version.hip)
print("GPU available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("AMD ROCm GPU is NOT available.")

print("GPU:", torch.cuda.get_device_name(0))

x = torch.randn(4096, 4096, device="cuda")
y = torch.randn(4096, 4096, device="cuda")

torch.cuda.synchronize()
start = time.perf_counter()

z = x @ y

torch.cuda.synchronize()
elapsed = time.perf_counter() - start

print("Matrix multiplication time:", elapsed)
print("AMD GPU test: PASS")
print("=" * 60)
