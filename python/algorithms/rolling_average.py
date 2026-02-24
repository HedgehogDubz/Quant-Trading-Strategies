import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'lib'))
import rolling_average as ra


def rolling_average_switch(closing_prices, opening_prices, high_prices, low_prices, **params):
    window = params.get('window', 3)
    
    rolling_avg = ra.get(closing_prices, window)
    buys = ra.get_buys(rolling_avg)
    sells = ra.get_sells(rolling_avg)
    
    return {
        'buys': buys,
        'sells': sells,
        'overlay_lines': [
            {
                'name': f'{window}-period RA',
                'data': rolling_avg,
                'color': 'orange'
            }
        ],
        'separate_lines': [],
        'points': []
    }

