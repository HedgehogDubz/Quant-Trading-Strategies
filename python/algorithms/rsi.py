import pandas as pd


def rsi_strategy(closing_prices, opening_prices, high_prices, low_prices, **params):
    period = params.get('period', 14)
    oversold = params.get('oversold', 30)
    overbought = params.get('overbought', 70)

    if len(closing_prices) < period + 1:
        return {
            'buys': [],
            'sells': [],
            'overlay_lines': [],
            'separate_lines': [],
            'points': []
        }

    delta = closing_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    loss = loss.replace(0, 0.0001)
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    buys = []
    sells = []

    for i in range(period, len(rsi)):
        if pd.notna(rsi.iloc[i]) and pd.notna(rsi.iloc[i-1]):
            if rsi.iloc[i] < oversold and rsi.iloc[i-1] >= oversold:
                buys.append(i)
            elif rsi.iloc[i] > overbought and rsi.iloc[i-1] <= overbought:
                sells.append(i)

    rsi_list = [None if pd.isna(val) else val for val in rsi]

    return {
        'buys': buys,
        'sells': sells,
        'overlay_lines': [],
        'separate_lines': [
            {
                'name': 'RSI',
                'data': rsi_list,
                'color': 'purple'
            }
        ],
        'points': [],
        'y_range': [0, 100],
        'reference_lines': [
            {'value': 70, 'label': 'Overbought', 'color': 'rgba(255, 0, 0, 0.3)'},
            {'value': 50, 'label': 'Neutral', 'color': 'rgba(128, 128, 128, 0.2)'},
            {'value': 30, 'label': 'Oversold', 'color': 'rgba(0, 255, 0, 0.3)'}
        ]
    }

