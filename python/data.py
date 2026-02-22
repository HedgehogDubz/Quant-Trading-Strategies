import yfinance as yf
import mplfinance as mpf
import pyarrow as pa
import pandas as pd
import rolling_average_wrapper as raw


TICKER = "AAPL"

df = yf.download(TICKER, period="5d", interval="1h")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

print(df.head(20))
df.to_csv(f"save_csv/{TICKER}_5m.csv")
df.to_parquet(f"save_parquet/{TICKER}_5m.parquet")

# Plot candlestick chart
mpf.plot(df, type='candle', style='charles', title='AAPL 5-min', volume=True)

print(f"C++ test: 5 + 3 = {raw.add(5, 3)}")