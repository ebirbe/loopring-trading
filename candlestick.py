import plotly.graph_objects as go

import pandas as pd
from datetime import datetime


df = pd.read_csv(
    'loopring.csv',
    header=None,
    names=[
        'time',
        'vol',
        'open',
        'close',
        'low',
        'high',
        'sma',
        'action'])

fig = go.Figure(data=[
    go.Scatter(
        x=df['time'],
        y=df['sma']),
    go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']),
])

fig.show()
