import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import simulate_actions_wrapper as saw
from algorithms import ALGORITHM_REGISTRY

st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 300px;
        max-width: 300px;
        background-color: white;
    }
    [data-testid="stSidebar"] {
        background-color: white;
    }
    [data-testid="stSidebar"] * {
        color: #262730 !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #262730 !important;
    }
    [data-testid="stSidebar"] label {
        color: #262730 !important;
    }
    [data-testid="stSidebar"] input[type="text"] {
        border: 2px solid #DDDDDD !important;
        border-radius: 6px !important;
        padding: 4px !important;
    }
    [data-testid="stSidebar"] input[type="text"]:focus {
        border-color: #ff4444 !important;
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)

if 'live_data' not in st.session_state:
    st.session_state.live_data = None
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'last_interval' not in st.session_state:
    st.session_state.last_interval = None
if 'last_lookback' not in st.session_state:
    st.session_state.last_lookback = None

st.title("Trading Strategy Dashboard")

st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="TSLA").upper()
date_mode = st.sidebar.radio("Date Mode", ["Period", "Custom Period", "Custom Range", "Live"])

if date_mode == "Period":
    period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h", "1d"], index=5)
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            st.error(f"No data available for {ticker} with period={period} and interval={interval}")
            st.stop()
    except Exception as e:
        st.error(f"Error downloading data: {str(e)}")
        st.stop()
elif date_mode == "Custom Period":
    # add outline to the text input
    period = st.sidebar.text_input("Period", value="1mo")
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h", "1d"], index=5)
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            st.error(f"No data available for {ticker} with period={period} and interval={interval}")
            st.stop()
    except Exception as e:
        st.error(f"Error downloading data: {str(e)}")
        st.stop()
elif date_mode == "Custom Range":
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start Date", value=datetime.now() - timedelta(days=365))
    end_date = col2.date_input("End Date", value=datetime.now())
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h", "1d"], index=5)
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
        if df.empty:
            st.error(f"No data available for {ticker} from {start_date} to {end_date} with interval={interval}")
            st.stop()
    except Exception as e:
        st.error(f"Error downloading data: {str(e)}")
        st.stop()
else:
    lookback_options = {"15 minutes": 15, "30 minutes": 30, "1 hour": 60, "2 hours": 120, "4 hours": 240, "1 day": 1440, "2 days": 2880, "5 days": 7200}
    lookback_label = st.sidebar.selectbox("Period", list(lookback_options.keys()), index=2)
    lookback_minutes = lookback_options[lookback_label]
    interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"], index=1)
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=60, value=5)
    
    if st.session_state.last_ticker != ticker or st.session_state.last_interval != interval or st.session_state.last_lookback != lookback_minutes:
        st.session_state.live_data = None
        st.session_state.last_ticker = ticker
        st.session_state.last_interval = interval
        st.session_state.last_lookback = lookback_minutes
    
    if st.session_state.live_data is not None and not st.session_state.live_data.empty:
        lookback_days = max(1, int(lookback_minutes / 1440) + 1)
        download_period = f"{lookback_days}d" if lookback_days <= 5 else "5d"

        latest_df = yf.download(ticker, period=download_period, interval=interval, progress=False)
        if isinstance(latest_df.columns, pd.MultiIndex):
            latest_df.columns = latest_df.columns.get_level_values(0)
        if not latest_df.empty and latest_df.index.tz is not None:
            latest_df.index = latest_df.index.tz_convert('America/New_York')

        if not latest_df.empty and len(latest_df) > 0:
            last_cached_time = st.session_state.live_data.index[-1]
            new_bars = latest_df[latest_df.index > last_cached_time]
            if not new_bars.empty:
                df = pd.concat([st.session_state.live_data, new_bars])
                cutoff_time = df.index[-1] - timedelta(minutes=lookback_minutes)
                df = df[df.index >= cutoff_time]
                st.session_state.live_data = df
                st.sidebar.success(f"Added {len(new_bars)} new bar(s)")
            else:
                df = st.session_state.live_data
                st.sidebar.info("No new data yet")
        else:
            df = st.session_state.live_data
    else:
        df = None
        lookback_days = max(1, int(lookback_minutes / 1440) + 1)
        download_period = f"{lookback_days}d" if lookback_days <= 5 else "5d"

        try:
            df = yf.download(ticker, period=download_period, interval=interval, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty:
                cutoff_time = df.index[-1] - timedelta(minutes=lookback_minutes)
                df = df[df.index >= cutoff_time]
                st.sidebar.info(f"Initial load: {len(df)} bars (fetched {download_period})")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
            df = pd.DataFrame()

        if df.empty:
            try:
                end_time = datetime.now()
                start_time = end_time - timedelta(minutes=lookback_minutes)
                df = yf.download(ticker, start=start_time, end=end_time, interval=interval, progress=False)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                if not df.empty:
                    cutoff_time = df.index[-1] - timedelta(minutes=lookback_minutes)
                    df = df[df.index >= cutoff_time]
                    st.sidebar.info(f"Initial load (fallback): {len(df)} bars")
            except Exception as e:
                st.sidebar.error(f"Fallback error: {e}")
        
        if df is not None and not df.empty:
            if hasattr(df.index, 'tz') and df.index.tz is not None:
                df.index = df.index.tz_convert('America/New_York')
            st.session_state.live_data = df
        else:
            st.sidebar.warning("No data available")
            df = pd.DataFrame()
    
    st.sidebar.info(f"Live mode - Auto-refresh every {refresh_rate}s")

if date_mode != "Live" and isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

if df.empty:
    st.error(f"No data available for {ticker}")
    if date_mode == "Live":
        st.info("**Tip**: Market may be closed. Try 'Period' mode.")
    st.stop()

closing_prices = df["Close"]
opening_prices = df["Open"]
high_prices = df["High"]
low_prices = df["Low"]

st.sidebar.header("Algorithm Settings")

algorithm_configs = {}
for algo in ALGORITHM_REGISTRY:
    st.sidebar.subheader(algo['name'])
    enabled = st.sidebar.checkbox(f"Enable {algo['name']}", value=(algo['id'] == 'rolling_average'), key=f"enable_{algo['id']}")

    if enabled:
        params = {}
        for param_name, param_config in algo['params'].items():
            if param_config['type'] == 'slider':
                params[param_name] = st.sidebar.slider(
                    param_config['label'],
                    min_value=param_config['min'],
                    max_value=param_config['max'],
                    value=param_config['default'],
                    key=f"{algo['id']}_{param_name}"
                )

        algorithm_configs[algo['id']] = {
            'enabled': True,
            'params': params,
            'algo': algo
        }

st.sidebar.subheader("Chart Settings")
show_candles = st.sidebar.checkbox("Show Candlesticks", value=False)
show_volume = st.sidebar.checkbox("Show Volume", value=True)
show_buys = st.sidebar.checkbox("Show Buy Signals", value=True)
show_sells = st.sidebar.checkbox("Show Sell Signals", value=True)

control_profit = closing_prices.iloc[-1] - closing_prices.iloc[0]
control_percent = (control_profit / closing_prices.iloc[0]) * 100


results = {}
all_algorithm_results = {}

for algo_id, config in algorithm_configs.items():
    algo = config['algo']
    params = config['params']

    result = algo['function'](closing_prices, opening_prices, high_prices, low_prices, **params)

    all_algorithm_results[algo_id] = {
        'name': algo['name'],
        'buys': result['buys'],
        'sells': result['sells'],
        'overlay_lines': result.get('overlay_lines', []),
        'separate_lines': result.get('separate_lines', []),
        'params': params
    }

    profit = 0.0
    percent = 0.0

    if len(result['buys']) > 0 and len(result['sells']) > 0:
        profit = saw.profit_buy_sell_singles(closing_prices, result['buys'], result['sells'])
        percent = (profit / closing_prices.iloc[0]) * 100

    results[algo_id] = {
        'name': algo['name'],
        'profit': profit,
        'percent': percent,
        'buys': result['buys'],
        'sells': result['sells'],
        'overlay_lines': result.get('overlay_lines', []),
        'separate_lines': result.get('separate_lines', []),
        'points': result['points'],
        'colors': algo['colors'],
        'y_range': result.get('y_range'),
        'reference_lines': result.get('reference_lines', [])
    }


total_algos = len(ALGORITHM_REGISTRY)
cols = st.columns(total_algos + 1)

with cols[0]:
    st.metric(
        label="Buy & Hold Profit",
        value=f"${control_profit:.2f}",
        delta=f"{control_percent:.2f}%"
    )

for idx, algo in enumerate(ALGORITHM_REGISTRY):
    algo_id = algo['id']
    if algo_id in results:
        result = results[algo_id]
        with cols[idx + 1]:
            st.metric(
                label=result['name'],
                value=f"${result['profit']:.2f}",
                delta=f"{result['percent']:.2f}%",
                delta_color="normal" if result['profit'] > control_profit else "inverse"
            )

st.subheader(f"{ticker} Price Chart")

overlay_results = {k: v for k, v in results.items() if len(v.get('overlay_lines', [])) > 0}
oscillator_results = {k: v for k, v in results.items() if len(v.get('separate_lines', [])) > 0}

num_oscillators = len(oscillator_results)
total_rows = 1 + (1 if show_volume else 0) + num_oscillators

row_heights = []
subplot_titles = []
specs = []

row_heights.append(0.5)
specs.append([{"secondary_y": False}])

if show_volume:
    row_heights.append(0.15)
    specs.append([{"secondary_y": False}])

for algo_id in oscillator_results.keys():
    row_heights.append(0.2)
    specs.append([{"secondary_y": False}])

if sum(row_heights) > 0:
    row_heights = [h / sum(row_heights) for h in row_heights]

use_categorical = interval in ['1m', '5m', '15m', '30m', '1h']
if use_categorical:
    x_data = list(range(len(df)))
    x_labels = [idx.strftime('%Y-%m-%d %H:%M') if hasattr(idx, 'strftime') else str(idx) for idx in df.index]
else:
    x_data = df.index
    x_labels = None

fig = make_subplots(
    rows=total_rows,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    row_heights=row_heights,
    specs=specs
)

if show_candles:
    fig.add_trace(
        go.Candlestick(
            x=x_data,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
else:
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=df['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.3)'
        ),
        row=1, col=1
    )

for algo_id, result in overlay_results.items():
    for line in result.get('overlay_lines', []):
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=line['data'],
                mode='lines',
                name=f"{result['name']} - {line['name']}",
                line=dict(color=line['color'], width=2)
            ),
            row=1, col=1
        )

    if show_buys and len(result['buys']) > 0:
        for i in result['buys']:
            if use_categorical:
                x_pos = i + 0.5
            else:
                if i < len(df) - 1:
                    time_delta = (df.index[i + 1] - df.index[i]) / 2
                    x_pos = df.index[i] + time_delta
                else:
                    time_delta = (df.index[-1] - df.index[-2]) / 2
                    x_pos = df.index[i] + time_delta

            line_style = 'solid' if result['colors']['line_style'] == 'solid' else 'dot'
            fig.add_vline(
                x=x_pos,
                line=dict(color='green', width=1.5, dash=line_style),
                opacity=0.7,
                row=1, col=1
            )

    if show_sells and len(result['sells']) > 0:
        for i in result['sells']:
            if use_categorical:
                x_pos = i + 0.5
            else:
                if i < len(df) - 1:
                    time_delta = (df.index[i + 1] - df.index[i]) / 2
                    x_pos = df.index[i] + time_delta
                else:
                    time_delta = (df.index[-1] - df.index[-2]) / 2
                    x_pos = df.index[i] + time_delta

            line_style = 'solid' if result['colors']['line_style'] == 'solid' else 'dot'
            fig.add_vline(
                x=x_pos,
                line=dict(color='red', width=1.5, dash=line_style),
                opacity=0.7,
                row=1, col=1
            )

if show_volume:
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' for i in range(len(df))]
    volume_row = 2
    fig.add_trace(
        go.Bar(
            x=x_data,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=volume_row, col=1
    )

oscillator_row = 2 if show_volume else 1
for algo_id, result in oscillator_results.items():
    oscillator_row += 1

    for line in result.get('separate_lines', []):
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=line['data'],
                mode='lines',
                name=f"{result['name']} - {line['name']}",
                line=dict(color=line['color'], width=2)
            ),
            row=oscillator_row, col=1
        )

    if 'reference_lines' in result:
        for ref_line in result['reference_lines']:
            fig.add_hline(
                y=ref_line['value'],
                line=dict(color=ref_line['color'], width=1, dash='dash'),
                row=oscillator_row, col=1
            )

    if 'y_range' in result:
        fig.update_yaxes(range=result['y_range'], row=oscillator_row, col=1)

    fig.update_yaxes(title_text=result['name'], row=oscillator_row, col=1)

    if show_buys and len(result['buys']) > 0:
        for i in result['buys']:
            if use_categorical:
                x_pos = i + 0.5
            else:
                if i < len(df) - 1:
                    time_delta = (df.index[i + 1] - df.index[i]) / 2
                    x_pos = df.index[i] + time_delta
                else:
                    time_delta = (df.index[-1] - df.index[-2]) / 2
                    x_pos = df.index[i] + time_delta

            line_style = 'solid' if result['colors']['line_style'] == 'solid' else 'dot'
            fig.add_vline(
                x=x_pos,
                line=dict(color='green', width=1.5, dash=line_style),
                opacity=0.7,
                row=oscillator_row, col=1
            )
            fig.add_vline(
                x=x_pos,
                line=dict(color='green', width=1.5, dash=line_style),
                opacity=0.7,
                row=1, col=1
            )

    if show_sells and len(result['sells']) > 0:
        for i in result['sells']:
            if use_categorical:
                x_pos = i + 0.5
            else:
                if i < len(df) - 1:
                    time_delta = (df.index[i + 1] - df.index[i]) / 2
                    x_pos = df.index[i] + time_delta
                else:
                    time_delta = (df.index[-1] - df.index[-2]) / 2
                    x_pos = df.index[i] + time_delta

            line_style = 'solid' if result['colors']['line_style'] == 'solid' else 'dot'
            fig.add_vline(
                x=x_pos,
                line=dict(color='red', width=1.5, dash=line_style),
                opacity=0.7,
                row=oscillator_row, col=1
            )
            fig.add_vline(
                x=x_pos,
                line=dict(color='red', width=1.5, dash=line_style),
                opacity=0.7,
                row=1, col=1
            )

chart_height = 400 + (150 if show_volume else 0) + (200 * num_oscillators)

fig.update_layout(
    title=f'{ticker}',
    yaxis_title='Price ($)',
    xaxis_rangeslider_visible=False,
    hovermode='x unified',
    height=chart_height,
    template='plotly_dark',
    bargap=0.1,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        bgcolor="white",
        bordercolor="rgba(0,0,0,0.2)",
        borderwidth=1,
        font=dict(size=11, color="black")
    ),
    margin=dict(t=80)
)

if show_volume:
    fig.update_yaxes(title_text="Volume", row=2, col=1)

price_min = df['Low'].min()
price_max = df['High'].max()
price_range = price_max - price_min
padding = price_range * 0.1

fig.update_yaxes(
    range=[price_min - padding, price_max + padding],
    row=1, col=1
)

if use_categorical and x_labels:
    tick_spacing = max(1, len(x_labels) // 10)
    tickvals = list(range(0, len(x_labels), tick_spacing))
    ticktext = [x_labels[i] for i in tickvals]
    fig.update_xaxes(
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        tickangle=-45
    )

st.plotly_chart(fig, use_container_width=True)

with st.expander("View Raw Price Data"):
    st.dataframe(df, use_container_width=True)

if date_mode == "Live":
    st.sidebar.button("🔄 Refresh Now")
    import time
    time.sleep(refresh_rate)
    st.rerun()

