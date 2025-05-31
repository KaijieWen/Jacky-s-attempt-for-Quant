# datasource.py

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import os
import numpy as np
from datetime import timedelta

TRAINING_DATA_PATH = r"/Users/wan/Desktop/stock_model/Jacky Quant Attempt /training_dataset"

def fetch_current_price_offline(symbol):
    fn = os.path.join(TRAINING_DATA_PATH, f"{symbol}_history.csv")
    if not os.path.exists(fn):
        return None
    df = pd.read_csv(fn)
    return float(df['Close'].iloc[-1])

def fetch_history_offline(symbol, period='1y'):
    fn = os.path.join(TRAINING_DATA_PATH, f"{symbol}_historical_data.csv")
    if not os.path.exists(fn):
        print(f"File not found: {fn}")
        return pd.DataFrame()
    df = pd.read_csv(fn, index_col=0, parse_dates=True)
    return df

def fetch_options_chain_offline(symbol):
    # List expiries as all files matching {symbol}_*_options.csv
    files = [f for f in os.listdir(TRAINING_DATA_PATH) if f.startswith(f"{symbol}_") and f.endswith("_options.csv")]
    return [f.split("_")[1] for f in files]

def fetch_option_chain_data_offline(symbol, exp_date):
    fn = os.path.join(TRAINING_DATA_PATH, f"{symbol}_{exp_date}_options.csv")
    print("OFFLINE MODE: Loading options from", fn)
    if not os.path.exists(fn):
        print("File not found!")
        return None
    df = pd.read_csv(fn)
    calls = df[df['type'] == 'call']
    puts = df[df['type'] == 'put']
    class Chain: pass
    c = Chain()
    c.calls = calls
    c.puts = puts
    return c





def fetch_current_price(symbol, data_source, av_api_key=None, polygon_api_key=None, offline_mode=False):
    if offline_mode:
        return fetch_current_price_offline(symbol)
    if data_source == "Yahoo Finance (default)":
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if data.empty:
            return None
        return float(data['Close'].iloc[0])
    elif data_source == "Alpha Vantage":
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={av_api_key}"
        resp = requests.get(url)
        data = resp.json()
        try:
            return float(data["Global Quote"]["05. price"])
        except Exception:
            return None
    elif data_source == "Polygon.io":
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey={polygon_api_key}"
        resp = requests.get(url)
        try:
            close = resp.json()["results"][0]["c"]
            return float(close)
        except Exception:
            return None
    else:
        raise NotImplementedError

def fetch_history(symbol, data_source, period, av_api_key=None, polygon_api_key=None, offline_mode=False):
    if offline_mode:
            return fetch_history_offline(symbol, period)
    if data_source == "Yahoo Finance (default)":
        ticker = yf.Ticker(symbol)
        return ticker.history(period=period)
    elif data_source == "Alpha Vantage":
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={av_api_key}"
        resp = requests.get(url)
        data = resp.json().get("Time Series (Daily)", {})
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.rename(columns={
            "1. open": "Open", "2. high": "High", "3. low": "Low", "4. close": "Close", "6. volume": "Volume"
        })
        df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        if period == "1y":
            cutoff = pd.Timestamp(datetime.now() - timedelta(days=365))
            df = df[df.index > cutoff]
        return df
    elif data_source == "Polygon.io":
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/2022-01-01/{datetime.now().strftime('%Y-%m-%d')}?adjusted=true&sort=desc&apiKey={polygon_api_key}"
        resp = requests.get(url)
        results = resp.json().get("results", [])
        if not results:
            return pd.DataFrame()
        df = pd.DataFrame(results)
        df['t'] = pd.to_datetime(df['t'], unit='ms')
        df = df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'})
        df = df[['t','Open','High','Low','Close','Volume']].set_index('t').sort_index()
        return df
    else:
        raise NotImplementedError

def fetch_options_chain(symbol, data_source, offline_mode=False):
    if offline_mode:
        return fetch_history_offline(symbol)
    if data_source == "Yahoo Finance (default)":
        return yf.Ticker(symbol).options
    else:
        return []

def fetch_option_chain_data(symbol, exp_date, data_source, offline_mode=False):
    if offline_mode:
        return fetch_option_chain_data_offline(symbol, exp_date)
    if data_source == "Yahoo Finance (default)":
        return yf.Ticker(symbol).option_chain(exp_date)
    else:
        return None

def fetch_news_sentiment(ticker, api_key, date=None, num_articles=8):
    import numpy as np
    from datetime import datetime
    import pandas as pd
    if not api_key:
        return None, "API key missing."
    if not date:
        date = datetime.now().strftime("%Y%m%dT0000")
    else:
        date = pd.to_datetime(date).strftime("%Y%m%dT0000")
    next_date = (pd.to_datetime(date[:8]) + pd.Timedelta(days=1)).strftime("%Y%m%dT0000")
    url = (
        f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
        f"&tickers={ticker}&time_from={date}&time_to={next_date}&limit={num_articles}&apikey={api_key}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "feed" in data:
            scores = []
            for article in data["feed"]:
                score = float(article.get("overall_sentiment_score", 0))
                scores.append(score)
            avg_score = np.mean(scores) if scores else 0
            return avg_score, None
        return None, "No news found."
    except Exception as e:
        return None, str(e)
