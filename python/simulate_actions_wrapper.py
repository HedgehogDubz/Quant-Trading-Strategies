import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))  
import simulate_actions as sa

# ASSUME BUYS AND SELLS ARE IN ORDER SEQUENTIALLY
def profit_buy_sell(closing_prices, buys, sells):
    return sa.profit_buy_sell(closing_prices, buys, sells)

def profit_buy_sell_singles(closing_prices, buys_indexes, sells_indexes):
    # Convert pandas Series to list if needed
    prices_list = closing_prices.tolist() if hasattr(closing_prices, 'tolist') else list(closing_prices)
    return sa.profit_buy_sell_singles(prices_list, buys_indexes, sells_indexes)
    