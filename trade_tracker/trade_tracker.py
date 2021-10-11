import numpy as np
import pandas as pd
# Data Source
import yfinance as yf
# Data viz
import plotly.graph_objs as go
import datetime

if __name__ == '__main__':
    fake_buys = [{'datetime': datetime.datetime.fromtimestamp(1633521600).strftime('%c'), 'price': 51276},
                 {'datetime': datetime.datetime.fromtimestamp(1633721400).strftime('%c'), 'price': 54018}]

    buys_df = pd.DataFrame(fake_buys)

    buys_df = buys_df.set_index(pd.DatetimeIndex(buys_df['datetime']))

    # Importing market data
    data = yf.download(tickers='BTC-USD', period='8d', interval='30m')

    # Adding Moving average calculated field
    data['MA5'] = data['Close'].rolling(5).mean()
    data['MA20'] = data['Close'].rolling(20).mean()

    # declare figure
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'], name='market data'))

    # Add Moving average on the graph
    fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], line=dict(color='blue', width=1.5), name='Long Term MA'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA5'], line=dict(color='orange', width=1.5), name='Short Term MA'))

    # add fake buys
    fig.add_trace(go.Scatter(x=buys_df.index, y=buys_df['price'], name='Buys'))

    # Updating X axis and graph
    # X-Axes
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=3, label="3d", step="day", stepmode="backward"),
                dict(count=5, label="5d", step="day", stepmode="backward"),
                dict(count=7, label="WTD", step="day", stepmode="todate"),
                dict(step="all")
            ])
        )
    )

    # Show
    fig.show()