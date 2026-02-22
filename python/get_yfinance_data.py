import yfinance as yf
import mplfinance as mpf
import pyarrow as pa
import moving_average as ma

df = yf.download("AAPL", period="5d", interval="5m")
print(df.head(20))
df.to_csv("save_csv/AAPL_5m.csv")
df.to_parquet("save_paraquet/AAPL_5m.parquet")
print(ma.add(5,3))