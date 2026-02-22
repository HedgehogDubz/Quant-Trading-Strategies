import mymodule
def moving_average(data, window_size):
    return data.rolling(window=window_size).mean()

def add(a,b):
    return mymodule.add(a,b)
