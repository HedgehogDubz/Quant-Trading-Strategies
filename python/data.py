import yfinance as yf
import mplfinance as mpf
import pyarrow as pa
import pandas as pd
import matplotlib.pyplot as plt
import rolling_average_wrapper as raw
import simulate_actions_wrapper as saw


TICKER = "TSLA"

df = yf.download(TICKER, period="30d", interval="1d")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

ts = df.index
closing_prices = df["Close"]


# Control - buy and hold profit
control_profit = closing_prices.iloc[-1] - closing_prices.iloc[0]

# Debug: Print the actual dates and prices
print(f"First date: {df.index[0]}, Price: ${closing_prices.iloc[0]:.2f}")
print(f"Last date: {df.index[-1]}, Price: ${closing_prices.iloc[-1]:.2f}")
print(f"Control profit: ${control_profit:.2f}, percent: {control_profit / closing_prices.iloc[0] * 100:.2f}%")



# from C++ module rolling average
rolling_avg = raw.get(closing_prices, 3)
ra_switch_slope_switch = raw.get_slope_switch(rolling_avg)
ra_switch_buys = raw.get_buys(rolling_avg)
ra_switch_sells = raw.get_sells(rolling_avg)

ra_switch_profit = saw.profit_buy_sell_singles(closing_prices, ra_switch_buys, ra_switch_sells)
print(f"Rolling average switch profit: ${ra_switch_profit:.2f}, percent: {ra_switch_profit / closing_prices.iloc[0] * 100:.2f}%")




fig, axes = mpf.plot(df, type='candle', style='charles', title=f'{TICKER} Rolling Average', volume=True, returnfig=True)
ax_price = axes[0]

x_index = range(len(rolling_avg))
ax_price.plot(x_index, rolling_avg, label=f'5-period RA switch: ${ra_switch_profit:.2f}', color='orange', linewidth=2)

# Add control profit as a text label
ax_price.text(0.02, 0.98, f'Buy & Hold: ${control_profit:.2f}',
              transform=ax_price.transAxes,
              verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax_price.legend()

for b in ra_switch_buys:
    ax_price.axvline(b, color='green', linestyle='-', linewidth=1.5, alpha=0.7)

for s in ra_switch_sells:
    ax_price.axvline(s, color='red', linestyle='-', linewidth=1.5, alpha=0.7)


plt.show()  # Commented out for debugging

