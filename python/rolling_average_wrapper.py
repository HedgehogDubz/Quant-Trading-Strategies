import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))  
import rolling_average as ra


def get(closing_prices, window_size):
    prices_list = closing_prices.tolist() if hasattr(closing_prices, 'tolist') else list(closing_prices)
    return ra.get_rolling_average(prices_list, window_size)

def get_slope_switch(rolling_average):
    return ra.get_slope_switch(rolling_average)

def get_buys(rolling_average):
    return ra.get_rolling_average_buys(rolling_average)

def get_sells(rolling_average):
    return ra.get_rolling_average_sells(rolling_average)
