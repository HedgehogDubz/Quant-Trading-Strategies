import sys
import os

# Add lib directory to path for C++ modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))

# Now import the C++ module
import rolling_average as ra

def moving_average(data, window_size):
    return data.rolling(window=window_size).mean()

def add(a, b):
    return ra.add(a, b)
