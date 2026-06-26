import numpy as np

def simple_forecast(counts, days=5):

    if len(counts) < 2:
       return [0] * days

    x = np.arange(len(counts))
    y = np.array(counts)

    coef = np.polyfit(x, y, 1)
    trend = np.poly1d(coef)

    future_x = np.arange(len(x), len(x) + days)

    predictions = trend(future_x)

    return [int(p) if p > 0 else 0 for p in predictions]