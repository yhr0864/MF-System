import serial
import time
import numpy as np
from typing import Union


def moving_average(data, window_size):
    """Smooth a list using a moving average."""
    if window_size < 1:
        raise ValueError("Window size must be at least 1.")

    if window_size % 2 == 0:
        raise ValueError("Window size must be an odd number to ensure symmetry.")

    kernel = np.ones(window_size) / window_size  # Create a smoothing kernel
    smoothed = np.convolve(data, kernel, mode="valid")  # Apply convolution

    # Pad the result to maintain the original size
    pad_size = (window_size - 1) // 2  # Number of elements to pad on each side
    smoothed_full = np.pad(smoothed, (pad_size, pad_size), mode="edge")

    return smoothed_full


class RequestFailed(Exception):
    pass


class UnexpectedResponse(Exception):
    pass


class ErrorOccurred(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass
