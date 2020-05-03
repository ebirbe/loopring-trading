import os
import requests
import json
# import pandas as pd
import numpy as np
import pytz
from pprint import pformat
from datetime import datetime
# from pandas_datareader import data as web
# import matplotlib.pyplot as plt
# %matplotlib inline


API_KEY = os.getenv("LOOPRING_APIKEY")


def time_human(seconds):
    tz = pytz.timezone("America/Caracas")
    # ~ date = pytz.utc.localize(datetime.fromtimestamp(seconds / 1000))
    # ~ date = date.astimezone(tz)
    date = datetime.fromtimestamp(seconds / 1000)
    return date.strftime('%Y-%m-%d %H:%M:%S')


def remote_data(market, interval='15min', limit=120):
    headers = {'X-API-KEY': API_KEY}
    url = "https://api.loopring.io/api/v2/candlestick?market=%s&interval=%s&limit=%s" % (market, interval, limit)
    response = requests.get(url, headers=headers)
    data = json.loads(response._content)
    data = data.get("data", {})
    data.reverse()
    return data


def get_rsi(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - (100. / (1. + rs))

    for i in range(n, len(prices)):
        delta = deltas[i-1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


def get_sma(values, window):
    weigths = np.repeat(1.0, window) / window
    smas = np.convolve(values, weigths, 'valid')
    return smas  # as a numpy array


def get_ema(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a


def get_macd(x, slow=26, fast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = ExpMovingAverage(x, slow)
    emafast = ExpMovingAverage(x, fast)
    return emaslow, emafast, emafast - emaslow


if __name__ == "__main__":
    market = "ETH-USDT"
    interval = "1min"
    window_rsi = 14
    window_sma = 24
    data = remote_data(market, interval, 500)
    dates = [time_human(int(r[0])) for r in data]
    closep = [float(r[3]) for r in data]
    # ~ rsi = get_rsi(closep, window_rsi)
    sma = get_sma(closep, window_sma)
    
    result = []
    for i in range(len(data)):
        result.append((
            dates[i],
            data[i][1],
            data[i][2],
            data[i][3],
            data[i][4],
            data[i][5],
            # ~ rsi[i],
            i >= window_sma and ("%.2f" % sma[i - window_sma]) or "",
            i > window_sma and closep[i] >= sma[i - window_sma] and "LONG" or "",
        ))
    for line in result:
        print (("%s,V:%s,O:%s,C:%s,L:%s,H:%s,MA:%s,%s") % (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
        # ~ print (("%s,%s,%s,%s,%s") % (line[0], line[2], line[3], line[4], line[5]))
        # ~ print (("%s, TXS%s, O%s, C%s, H%s, L%s, SMA%s: %s, %s") % (line[0], line[1], line[2], line[3], line[4], line[5], window_sma, line[6], line[7]))
