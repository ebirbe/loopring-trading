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
    date = pytz.utc.localize(datetime.fromtimestamp(seconds / 1000))
    date = date.astimezone(tz)
    return date.strftime('%Y-%m-%d %H:%M:%S')


def remote_data(market, interval='15min', limit=120):
    headers = {'X-API-KEY': API_KEY}
    url = "https://api.loopring.io/api/v2/candlestick?market=%s&interval=%s&limit=%s" % (market, interval, limit)
    response = requests.get(url, headers=headers)
    data = json.loads(response._content)
    data = data.get("data", {})
    dates = [time_human(int(r[0])) for r in data]
    closep = [float(r[3]) for r in data]
    closep.reverse()
    dates.reverse()
    return (dates, closep)


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


if __name__ == "__main__":
    market = "ETH-USDT"
    dates, prices = remote_data(market)
    rsi = get_rsi(prices)
    result = []
    for i in range(len(rsi)):
        result.append((dates[i], prices[i], rsi[i]))
    print("%s RSI is: \n%s" % (market, pformat(result)))
