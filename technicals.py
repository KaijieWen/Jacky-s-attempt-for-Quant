# technicals.py
import ephem
import pandas_ta as ta
from stocktrends import Renko
from scipy.signal import argrelextrema
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

def compute_technical_indicators(df):
    import numpy as np
    indicators = {}
    close = df['Close']
    indicators['sma20'] = close.rolling(20).mean().iloc[-1]
    indicators['sma50'] = close.rolling(50).mean().iloc[-1]
    indicators['sma200'] = close.rolling(200).mean().iloc[-1]
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_gain = up.rolling(14).mean().iloc[-1]
    avg_loss = down.rolling(14).mean().iloc[-1]
    rs = avg_gain / avg_loss if avg_loss != 0 else np.nan
    indicators['rsi'] = 100 - (100 / (1 + rs)) if not np.isnan(rs) else 50
    ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
    indicators['macd'] = ema12 - ema26
    indicators['macd_signal'] = close.ewm(span=9, adjust=False).mean().iloc[-1]
    indicators['bb_middle'] = close.rolling(20).mean().iloc[-1]
    indicators['bb_upper'] = indicators['bb_middle'] + 2 * close.rolling(20).std().iloc[-1]
    indicators['bb_lower'] = indicators['bb_middle'] - 2 * close.rolling(20).std().iloc[-1]
    indicators['vol_ma20'] = df['Volume'].rolling(20).mean().iloc[-1]
    
    indicators['fib'] = fibonacci_retracement(df)
    indicators['breakout'] = detect_breakout(df)
    indicators['engulfing'] = detect_engulfing(df)
    indicators['heikin_ashi'] = heikin_ashi(df)
    indicators['moon_phase'] = moon_phase()
    indicators['renko'] = renko_bricks(df)
    indicators['support_resistance'] = support_resistance(df)
    indicators['dynamic_sr'] = dynamic_support_resistance(df)
    indicators['trendline'] = auto_trendline(df)
    indicators['stochastic'] = stochastic_oscillator(df)
    indicators['obv'] = on_balance_volume(df)

    return indicators

def compute_signals(price_history, techs):
    signals = {}
    signals['above_ma20'] = price_history['Close'].iloc[-1] > techs['sma20']
    signals['ma_crossover'] = techs['sma20'] > techs['sma50']
    signals['rsi_status'] = 'overbought' if techs['rsi'] > 70 else 'oversold' if techs['rsi'] < 30 else 'neutral'
    signals['macd_cross'] = techs['macd'] > techs['macd_signal']
    signals['volume_spike'] = price_history['Volume'].iloc[-1] > techs['vol_ma20']
    signals['bollinger'] = (
        'above' if price_history['Close'].iloc[-1] > techs['bb_upper']
        else 'below' if price_history['Close'].iloc[-1] < techs['bb_lower'] else 'middle'
    )
    return signals

def fibonacci_retracement(df, lookback=120):
    # Find swing high/low in the window
    high = df['High'][-lookback:].max()
    low = df['Low'][-lookback:].min()
    diff = high - low
    levels = [high - diff * r for r in [0.236, 0.382, 0.5, 0.618, 0.786]]
    return {'levels': levels, 'high': high, 'low': low}

def detect_breakout(df, window=20, threshold=2.5):
    highs = df['High'].rolling(window).max()
    lows = df['Low'].rolling(window).min()
    recent_close = df['Close'].iloc[-1]
    # Break above window high
    if recent_close > highs.iloc[-2]:
        return "breakout_up"
    elif recent_close < lows.iloc[-2]:
        return "breakout_down"
    return "none"

def detect_engulfing(df):
    # Simple example: last 2 candles
    open1, close1 = df['Open'].iloc[-2], df['Close'].iloc[-2]
    open2, close2 = df['Open'].iloc[-1], df['Close'].iloc[-1]
    if close2 > open2 and close1 < open1 and close2 > open1 and open2 < close1:
        return "bullish_engulfing"
    elif close2 < open2 and close1 > open1 and close2 < open1 and open2 > close1:
        return "bearish_engulfing"
    return "none"

def heikin_ashi(df):
    ha = df.copy()
    ha['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    ha['HA_Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
    ha['HA_High'] = ha[['HA_Open', 'HA_Close', 'High']].max(axis=1)
    ha['HA_Low'] = ha[['HA_Open', 'HA_Close', 'Low']].min(axis=1)
    return ha


def moon_phase(date=None):
    # Returns moon phase as string for given date (default: today)
    date = date or ephem.now()
    moon = ephem.Moon(date)
    phase = moon.phase
    # 0=new, ~14=full, ~7=first quarter, ~21=last quarter
    if phase < 1:
        return "New Moon"
    elif phase < 7:
        return "Waxing Crescent"
    elif phase < 13:
        return "First Quarter"
    elif phase < 21:
        return "Full Moon"
    elif phase < 27:
        return "Last Quarter"
    else:
        return "Waning Crescent"

def renko_bricks(df, brick_size=None):
    df2 = df[['Open','High','Low','Close','Volume']].copy().reset_index()
    df2.columns = ['date','open','high','low','close','volume']
    renko_obj = Renko(df2)
    if brick_size:
        renko_obj.brick_size = brick_size
    renko_df = renko_obj.get_ohlc_data()
    return renko_df

# def detect_harmonic_patterns(df):
#     # TODO: Use a package like 'harmonics' or your own ML
#     return "not_implemented"



def support_resistance(df, order=10):
    close = df['Close']
    min_idx = argrelextrema(close.values, np.less, order=order)[0]
    max_idx = argrelextrema(close.values, np.greater, order=order)[0]
    supports = [(close.index[i], close.iloc[i]) for i in min_idx]
    resistances = [(close.index[i], close.iloc[i]) for i in max_idx]
    return supports, resistances

def dynamic_support_resistance(df, window=30):
    rolling_min = df['Close'].rolling(window).min()
    rolling_max = df['Close'].rolling(window).max()
    return rolling_min, rolling_max

def auto_trendline(df, window=50):
    close = df['Close'][-window:]
    X = np.arange(len(close)).reshape(-1,1)
    y = close.values
    reg = LinearRegression().fit(X, y)
    trend = reg.predict(X)
    return trend, close.index

def stochastic_oscillator(df, k_period=14, d_period=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    return k, d

def on_balance_volume(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)