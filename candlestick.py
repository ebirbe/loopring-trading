import plotly.graph_objects as go

import pandas as pd
from datetime import datetime


df = pd.read_csv(
    'loopring.csv',
    header=None,
    names=[
        'time',
        'hodl',
        'strategy'
    ])

fig = go.Figure(data=[
    go.Scatter(
        name="% Return Hodl",
        x=df['time'],
        y=df['hodl']),
    go.Scatter(
        name="% Return Strategy",
        x=df['time'],
        y=df['strategy']),
    #go.Candlestick(
    #    x=df['time'],
    #    open=df['open'],
    #    high=df['high'],
    #    low=df['low'],
    #    close=df['close']),
])

fig.show()
