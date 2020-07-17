import os
import requests
import json
# import pandas as pd
import numpy as np
import pytz
from pprint import pformat
from datetime import datetime, timedelta
# from pandas_datareader import data as web
# import matplotlib.pyplot as plt
# %matplotlib inline
import sqlite3

API_KEY = os.getenv("LOOPRING_APIKEY")
DB_NAME = "data_candlestick.sqlite3"
INTERVAL_DELTAS = {
    "1min": timedelta(minutes=1),
    "5min": timedelta(minutes=5),
    "15min": timedelta(minutes=15),
    "30min": timedelta(minutes=30),
    "1hr": timedelta(hours=1),
    "2hr": timedelta(hours=2),
    "4hr": timedelta(hours=4),
    "12hr": timedelta(hours=12),
    "1d": timedelta(days=1),
    "1w": timedelta(weeks=1),
}


def connect_database(name):
    try:
        conn = sqlite3.connect(
            name,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()
        print("Database %s created and successfully connected to SQLite" % name)
        
        query = "SELECT sqlite_version();"
        cursor.execute(query)
        record = cursor.fetchall()
        print("SQLite version is: ", record)
        
        return conn
    
    except sqlite3.Error as error:
        print("Error while connecting to database: ", error)


def _is_date_saved(cr, interval, time):
    sql = "SELECT time FROM candlestick_%s WHERE time = ?" % interval
    cr.execute(sql, [time])
    if cr.fetchall():
        return True
    return False

    
def is_current_time_interval(data_time, current_time, interval):
    """Returns True is the time is whithin the current interval.
    This is useful when we need to check if a candlestick retreived
    is not at its final state in time."""
    return current_time - INTERVAL_DELTAS[interval] < data_time
    
            
def time_human(seconds):
    # ~ tz = pytz.timezone("America/Caracas")
    # ~ date = pytz.utc.localize(datetime.fromtimestamp(seconds / 1000))
    # ~ date = date.astimezone(tz)
    date = datetime.fromtimestamp(seconds / 1000)
    return date.strftime('%Y-%m-%d %H:%M:%S')


def remote_data(market, interval, start, end, limit=None):
    start = int(start.strftime("%s")) * 1000
    end = int(end.strftime("%s")) * 1000
        
    headers = {
        'X-API-KEY': API_KEY
    }
    params = {
        "market": market,
        "interval": interval,
        "start": start,
        "end": end,
        "limit": limit,
    }
    url = "https://api.loopring.io/api/v2/candlestick"
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        raise Exception("Response code was not 200")
    data = response.json()
    if data.get("resultInfo", {}).get('code') != 0:
        raise Exception("Error retreiving data: %s" % data.get("resultInfo"))

    return data.get("data", {})


def _retrieve_candlesticks(market, interval, start=None, end=None, limit=None):
    end = end or datetime.now()
    start = start or end - (INTERVAL_DELTAS[interval] * 120)
    data = []
    while start <= end:
        if limit and limit >= len(data):
            break
        print("Retrieving %s data from %s to %s..." % (interval, start, end))
        res = remote_data(market, interval, start, end, limit)
        print("Retrieved %s candlesticks." % len(res))
        data += res
        end -= (INTERVAL_DELTAS[interval] * 120)
    return data


def insert_candlestick_data(data, interval):
    print("Saving %d rows into database..." % len(data))
    conn = connect_database(DB_NAME)
    cr = conn.cursor()
    
    current_time = datetime.now()
    for i in range(len(data)):

        # Current candlestick should not be saved until time interval is completed
        seconds = int(data[i][0])
        date = datetime.fromtimestamp(seconds / 1000)
        if is_current_time_interval(date, current_time, interval):
            continue

        #date = date.strftime('%Y-%m-%d %H:%M:%S')
        if _is_date_saved(cr, interval, date):
            continue

        row = (
            date,
            data[i][1],
            data[i][2],
            data[i][3],
            data[i][4],
            data[i][5],
            "%s.%s" % (data[i][6][:-18], data[i][6][-18:].zfill(18)),
            "%s.%s" % (data[i][7][:-6], data[i][7][-6:].zfill(6)),
        )
        sql = """
            INSERT INTO candlestick_%s
                (time, txs, open, close, high, low, volume_base, volume_quote)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?);""" % interval
        cr.execute(sql, row)
    conn.commit()
    print("Data saved.")


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
    start = datetime.now() - timedelta(hours=6)
    end = datetime.now()
    window_rsi = 14
    sma_fast_size = 2
    sma_slow_size = 30
    
    #__import__("pudb").set_trace()
    
    data = _retrieve_candlesticks(market, interval, start, end)
    insert_candlestick_data(data, interval)
    
    with connect_database(DB_NAME) as conn:
        cr = conn.cursor()
        sql = """
            SELECT time, txs, open, close, high, low
            FROM candlestick_%s
            WHERE time BETWEEN ? AND ?
            ORDER BY time ASC""" % interval
        cr.execute(sql, [start, end])
        data = cr.fetchall()
    
    closep = [r[3] for r in data]
    # ~ rsi = get_rsi(closep, window_rsi)
    sma_fast = get_sma(closep, sma_fast_size)
    sma_slow = get_sma(closep, sma_slow_size)

    result = []
    for i in range(len(data)):
        result.append((
            data[i][0],
            data[i][1],
            data[i][2],
            data[i][3],
            data[i][4],
            data[i][5],
            # ~ rsi[i],
            i >= sma_slow_size and ("%.2f" % sma_slow[i - sma_slow_size]) or "",
            i >= sma_fast_size and ("%.2f" % sma_fast[i - sma_fast_size]) or "",
            i > sma_slow_size and sma_fast[i - sma_fast_size] >= sma_slow[i - sma_slow_size] and "LONG" or "",
        ))
    for line in result:
        print (("%s - C:%s | MA:%s | %s") % (line[0], line[2], line[6], line[8]))
        #print (("%s,V:%s,O:%s,C:%s,L:%s,H:%s,MA:%s,%s") % (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
        # ~ print (("%s,%s,%s,%s,%s") % (line[0], line[2], line[3], line[4], line[5]))
        #print (("%s,%s,%s,%s,%s,%s,%s,%s,%s") % (line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8]))
        #print (("%s, TXS%s, O%s, C%s, H%s, L%s, SMA%s: %s, %s") % (line[0], line[1], line[2], line[3], line[4], line[5], window_sma, line[6], line[7]))
