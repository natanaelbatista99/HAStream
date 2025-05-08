import torch

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version (torch):", torch.version.cuda)
print("cuDNN enabled:", torch.backends.cudnn.enabled)

if torch.cuda.is_available():
    print("Device name:", torch.cuda.get_device_name(0))
