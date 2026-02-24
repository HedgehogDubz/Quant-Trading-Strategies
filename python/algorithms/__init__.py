from .rolling_average import rolling_average_switch
from .rsi import rsi_strategy


ALGORITHM_REGISTRY = [
    {
        'id': 'rolling_average',
        'name': 'Rolling Average Switch',
        'function': rolling_average_switch,
        'description': 'Buy when slope switches up, sell when switches down',
        'params': {
            'window': {
                'type': 'slider',
                'label': 'Window Size',
                'min': 2,
                'max': 50,
                'default': 3
            }
        },
        'colors': {
            'buy': 'green',
            'sell': 'red',
            'line_style': 'solid'
        }
    },
    {
        'id': 'rsi',
        'name': 'RSI Strategy',
        'function': rsi_strategy,
        'description': 'Buy when oversold, sell when overbought',
        'params': {
            'period': {
                'type': 'slider',
                'label': 'RSI Period',
                'min': 5,
                'max': 30,
                'default': 14
            },
            'oversold': {
                'type': 'slider',
                'label': 'Oversold Threshold',
                'min': 20,
                'max': 40,
                'default': 30
            },
            'overbought': {
                'type': 'slider',
                'label': 'Overbought Threshold',
                'min': 60,
                'max': 80,
                'default': 70
            }
        },
        'colors': {
            'buy': 'green',
            'sell': 'red',
            'line_style': 'solid'
        }
    }
]

