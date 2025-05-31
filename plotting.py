import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import argrelextrema
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import timedelta
from technicals import compute_technical_indicators

def auto_fit_font(ax, num_labels, min_size=7, max_size=14):
    new_size = max(min_size, min(max_size, int(max_size - 0.4 * (num_labels - 10))))
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(new_size)

def plot_signals_and_explanations(price_history, techs, signals, direction, ticker, window=120, provider="Yahoo Finance (default)"):
    df = price_history.tail(window).copy()
    close = df['Close']
    dates = df.index
    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(3, 2, width_ratios=[7, 3], height_ratios=[2.5, 1, 1])
    ax_main = fig.add_subplot(gs[0, 0])
    ax_info = fig.add_subplot(gs[0, 1])
    ax_rsi = fig.add_subplot(gs[1, 0], sharex=ax_main)
    ax_macd = fig.add_subplot(gs[2, 0], sharex=ax_main)
    ax_info.axis("off")
    ax_main.plot(dates, close, label="Close", color="black", linewidth=2)

    # -- Original: Standard MA/Bollinger overlays --
    for ma, color in zip([20,50,200], ['#0af','#fa0','#800080']):
        if len(close) >= ma:
            ax_main.plot(dates, close.rolling(ma).mean(), label=f"MA{ma}", linewidth=1.3, color=color)
    if len(close) >= 20:
        bb_mid = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_upper = bb_mid + 2*bb_std
        bb_lower = bb_mid - 2*bb_std
        ax_main.fill_between(dates, bb_upper, bb_lower, color='skyblue', alpha=0.12, label="Bollinger Bands")

    # --------- ADVANCED INDICATOR OVERLAYS HERE ---------
    indicators = compute_technical_indicators(df)

    # 1. Fibonacci Retracement
    if 'fib' in indicators:
        for level in indicators['fib']['levels']:
            ax_main.axhline(level, linestyle='--', color='magenta', alpha=0.45, label=f'Fib {level:.2f}')

    # 2. Enhanced Support/Resistance
    if 'support_resistance' in indicators:
        supports, resistances = indicators['support_resistance']
        if supports:
            d, val = zip(*supports)
            ax_main.scatter(d, val, color='lime', marker='^', s=70, label='Support+')
        if resistances:
            d, val = zip(*resistances)
            ax_main.scatter(d, val, color='orangered', marker='v', s=70, label='Resistance+')

    # 3. Heikin Ashi overlay (optional: faded)
    if 'heikin_ashi' in indicators:
        ha_df = indicators['heikin_ashi']
        ax_main.plot(ha_df.index, ha_df['HA_Close'], label="Heikin Ashi", color='orange', alpha=0.7, linewidth=1.1)

    # 4. Renko overlay (optional: comment/uncomment)
    # if 'renko' in indicators and indicators['renko'] is not None:
    #     renko = indicators['renko']
    #     ax_main.plot(renko['date'], renko['close'], label="Renko", color='brown', alpha=0.7, linewidth=1.2)

    # 5. Trendline (linear regression)
    if 'trendline' in indicators:
        trend, trend_dates = indicators['trendline']
        ax_main.plot(trend_dates, trend, label="Trendline", color='blue', linestyle='--', linewidth=2, alpha=0.8)

    # 6. Engulfing pattern signal
    engulfing = indicators.get('engulfing', 'none')
    if engulfing != "none":
        ax_main.annotate(
            f'{engulfing.replace("_", " ").title()}',
            xy=(dates[-1], close.iloc[-1]),
            xytext=(-70, 30),
            textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='purple'),
            color='purple', fontsize=12, fontweight='bold'
        )
    # --- (keep your original extrema finder for local S/R overlays) ---
    def find_extrema(prices, order=8):
        min_idx = argrelextrema(prices.values, np.less, order=order)[0]
        max_idx = argrelextrema(prices.values, np.greater, order=order)[0]
        supports = [(dates[i], prices.iloc[i]) for i in min_idx]
        resistances = [(dates[i], prices.iloc[i]) for i in max_idx]
        return supports, resistances
    supports, resistances = find_extrema(close, order=7)
    if supports:
        sup_dates, sup_vals = zip(*supports)
        ax_main.scatter(sup_dates, sup_vals, color='green', marker='^', label='Support', s=70, zorder=5)
    if resistances:
        res_dates, res_vals = zip(*resistances)
        ax_main.scatter(res_dates, res_vals, color='red', marker='v', label='Resistance', s=70, zorder=5)

    # -- Forecasting, "now" marker, axes, legend, etc. --
    if provider != "Yahoo Finance (default)":
        ndays_future = 14
        X = np.arange(len(close)).reshape(-1, 1)
        y = close.values
        reg = LinearRegression().fit(X, y)
        future_X = np.arange(len(close)+ndays_future).reshape(-1,1)
        forecast = reg.predict(future_X)
        forecast_dates = list(dates) + [dates[-1]+timedelta(days=i) for i in range(1, ndays_future+1)]
        ax_main.plot(
            forecast_dates,
            forecast,
            label="Trend Forecast (Linear)", color='magenta', linestyle='--', linewidth=2
        )
        pred_date = dates[-1]+timedelta(days=ndays_future)
        pred_val = forecast[-1]
        ax_main.scatter([pred_date], [pred_val], color='blue', marker='*', s=150, zorder=10, label='Forecast End')
        ax_main.annotate(f"Est. {pred_val:.2f} on {pred_date.date()}",
                         (pred_date, pred_val), textcoords="offset points", xytext=(-60,15),
                         ha='center', fontsize=10, color='blue', fontweight='bold')
    ax_main.axvline(dates[-1], color='purple', linestyle='--', linewidth=1.2)
    ax_main.scatter(dates[-1], close.iloc[-1], color='gold' if direction=='call' else 'magenta',
               marker='o', s=130, label=f"Now: {'CALL' if direction=='call' else 'PUT'}", zorder=10)
    ax_main.set_title(f"{ticker} {'(Prediction Mode)' if provider != 'Yahoo Finance (default)' else ''} Price & Signals")
    ax_main.set_ylabel("Price")
    auto_fit_font(ax_main, len(dates))

    # Remove duplicate legend entries for readability!
    handles, labels = ax_main.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax_main.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.0, 1), fontsize=10, framealpha=0.92, ncol=1)

    ax_main.grid(alpha=0.2)
    # --- RSI subplot ---
    rsi = close.rolling(14).apply(
        lambda x: 100 - (100 / (1 + (x.diff().clip(lower=0).mean() /
                                    -x.diff().clip(upper=0).mean()))) if x.diff().clip(upper=0).mean() != 0 else 50)
    ax_rsi.plot(dates, rsi, label="RSI", color="blue")
    ax_rsi.axhline(70, color='red', linestyle='--', linewidth=1, label='Overbought')
    ax_rsi.axhline(30, color='green', linestyle='--', linewidth=1, label='Oversold')
    ax_rsi.set_ylabel("RSI")
    ax_rsi.legend(loc='upper left', fontsize=8)
    ax_rsi.grid(alpha=0.18)
    auto_fit_font(ax_rsi, len(dates))
    # --- MACD subplot ---
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    ax_macd.plot(dates, macd, label="MACD", color="purple")
    ax_macd.plot(dates, signal, label="Signal Line", color="orange")
    ax_macd.bar(dates, macd - signal, color=['green' if v > 0 else 'red' for v in macd-signal], width=1, alpha=0.34)
    ax_macd.legend(loc='upper left', fontsize=8)
    ax_macd.set_ylabel("MACD")
    ax_macd.grid(alpha=0.15)
    ax_macd.axhline(0, color='black', linewidth=1)
    auto_fit_font(ax_macd, len(dates))
    ax_macd.xaxis.set_major_locator(mdates.MonthLocator())
    ax_macd.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.tight_layout(rect=(0,0.03,1,1))
    desc = [
        f"Signals as of {dates[-1].date()}:\n",
        f"- {'CALL' if direction=='call' else 'PUT'} suggestion: based on trend/indicators.",
        f"- Price {'above' if signals['above_ma20'] else 'below'} MA20.",
        f"- MA20 {'>' if signals['ma_crossover'] else '<='} MA50: {'bullish' if signals['ma_crossover'] else 'bearish'}.",
        f"- MACD: {'bullish' if signals['macd_cross'] else 'bearish'}.",
        f"- RSI: {signals['rsi_status']}.",
        f"- Volume: {'spike' if signals['volume_spike'] else 'normal'}.",
        f"- Bollinger: {signals['bollinger']}.",
        f"- Supports (green) & Resistances (red) marked on price.",
        f"- Extra: Fib/Heikin Ashi/Trendline overlays visible."
    ]
    if provider != "Yahoo Finance (default)":
        desc.append(
            "\nForecast: Linear regression predicts price trajectory (magenta dashed).\n"
            "The blue star marks the estimated price in 2 weeks. Crucial levels are marked.\n"
            "Use these for swing or short-term trend planning."
        )
    ax_info.text(0.02, 0.95, "\n".join(desc), va='top', ha='left', fontsize=11, wrap=True)
    plt.show()
