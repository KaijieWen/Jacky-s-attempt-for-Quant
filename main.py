# main.py

import pandas as pd
import threading
from datetime import datetime
import FreeSimpleGUI as sg  # or PySimpleGUI as sg

from config import DEFAULT_ALPHA_VANTAGE_KEY, DEFAULT_POLYGON_KEY, TRADE_LOG_PATH
from datasource import (
    fetch_current_price, fetch_history, fetch_options_chain, fetch_option_chain_data, fetch_news_sentiment
)
from technicals import compute_technical_indicators, compute_signals
from options import find_best_options
from plotting import plot_signals_and_explanations
from logging_utils import log_trade_result
import pandas_market_calendars as mcal

def is_us_market_open(date=None):
    nyse = mcal.get_calendar('NYSE')
    date = pd.Timestamp(date or datetime.now().date())
    schedule = nyse.valid_days(start_date=date, end_date=date)
    return len(schedule) > 0

def compute_recommendation(symbol, data_source, news_sentiment=False, api_key=None, polygon_api_key=None, offline_mode=False):
    try:
        symbol = symbol.strip().upper()
        if not symbol:
            return "No stock symbol provided."
        price_history = fetch_history(symbol, data_source, '1y', api_key, polygon_api_key, offline_mode=offline_mode)
        if price_history is None or price_history.empty:
            return "Error: Unable to retrieve history."
        techs = compute_technical_indicators(price_history)
        signals = compute_signals(price_history, techs)
        news_summary = ""
        if news_sentiment and api_key:
            news_score, news_err = fetch_news_sentiment(symbol, api_key)
            if news_err:
                news_summary = f"News sentiment unavailable: {news_err}"
            else:
                news_summary = f"News sentiment score: {round(news_score,2)}"
                signals['news_positive'] = news_score > 0.1
        else:
            news_summary = "News sentiment not used (unchecked)."
        bullish = (signals['above_ma20'] and signals['macd_cross'] and signals['rsi_status'] != "overbought")
        direction = "call" if bullish else "put"
        underlying_price = fetch_current_price(symbol, data_source, api_key, polygon_api_key, offline_mode=offline_mode)
        options_chains = {}
        expirations = fetch_options_chain(symbol, data_source, offline_mode=offline_mode)
        if data_source == "Yahoo Finance (default)" and expirations:
            from datetime import timedelta
            today = datetime.today().date()
            cutoff_date = today + timedelta(days=45)
            sorted_dates = sorted(datetime.strptime(date, "%Y-%m-%d").date() for date in expirations)
            exp_dates = [d.strftime("%Y-%m-%d") for d in sorted_dates if d <= cutoff_date]
            for exp_date in exp_dates:
                chain = fetch_option_chain_data(symbol, exp_date, data_source, offline_mode=offline_mode)
                options_chains[exp_date] = chain
        return {
            "signals": signals,
            "techs": techs,
            "options_chains": options_chains,
            "underlying_price": underlying_price,
            "direction": direction,
            "news_summary": news_summary,
            "price_history": price_history,
            "ticker": symbol,
            "provider": data_source
        }
    except Exception as e:
        return f'Error occurred processing: {str(e)}'

def main_gui():
    main_layout = [
        [sg.Text("Data Source:"), sg.Combo(["Yahoo Finance (default)", "Alpha Vantage", "Polygon.io"], default_value="Yahoo Finance (default)", key="data_source")],
        [sg.Text("Enter Stock Symbol:"), sg.Input(key="stock", size=(20, 1), focus=True)],
        [sg.Checkbox('Include News Sentiment (Alpha Vantage API required)', key="news_sentiment", default=False)],
        [sg.Text('Alpha Vantage API Key:'), sg.Input(key="api_key", size=(32, 1), password_char="*", default_text=DEFAULT_ALPHA_VANTAGE_KEY)],
        [sg.Text('Polygon.io API Key:'), sg.Input(key="polygon_key", size=(32, 1), password_char="*", default_text=DEFAULT_POLYGON_KEY)],
        [sg.Button("Submit", bind_return_key=True), sg.Button("Exit")],
        [sg.Text("", key="recommendation", size=(60, 2))],
        [sg.Checkbox('Offline Training Mode', key="offline_mode", default=False)]
    ]
    window = sg.Window("Options Trade Recommendation", main_layout)
    while True:
        event, values = window.read()
        offline_mode = values.get("offline_mode", False)
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        if event == "Submit":
            window["recommendation"].update("")
            if not offline_mode and not is_us_market_open():
                sg.popup("The US stock market is closed today. Please try again on a trading day.")
                continue
            stock = values.get("stock", "")
            data_source = values.get("data_source", "Yahoo Finance (default)")
            news_sentiment_on = values.get("news_sentiment", False)
            api_key = values.get("api_key", "").strip()
            polygon_key = values.get("polygon_key", "").strip()
            loading_layout = [[sg.Text("Loading...", key="loading", justification="center")]]
            loading_window = sg.Window("Loading", loading_layout, modal=True, finalize=True, size=(275, 100))
            result_holder = {}
            def worker():
                try:
                    offline_mode = values.get("offline_mode", False)
                    result = compute_recommendation(stock, data_source, news_sentiment_on, api_key, polygon_key, offline_mode=offline_mode)
                    result_holder['result'] = result
                except Exception as e:
                    result_holder['error'] = str(e)
            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            while thread.is_alive():
                event_load, _ = loading_window.read(timeout=100)
                if event_load == sg.WINDOW_CLOSED:
                    break
            thread.join(timeout=1)
            loading_window.close()
            if 'error' in result_holder:
                window["recommendation"].update(f"Error: {result_holder['error']}")
            elif 'result' in result_holder:
                result = result_holder['result']
                if isinstance(result, str):
                    window["recommendation"].update(result)
                    continue
                signals = result['signals']
                techs = result['techs']
                direction = result['direction']
                news_summary = result['news_summary']
                options_chains = result['options_chains']
                underlying_price = result['underlying_price']
                price_history = result['price_history']
                ticker = result['ticker']
                provider = result.get('provider', "Yahoo Finance (default)")
                signal_list = [
                    f"Price vs MA20: {'Above' if signals['above_ma20'] else 'Below'}",
                    f"MA20 vs MA50: {'Bullish' if signals['ma_crossover'] else 'Bearish'}",
                    f"RSI: {signals['rsi_status'].capitalize()} ({round(techs['rsi'],2)})",
                    f"MACD: {'Bullish' if signals['macd_cross'] else 'Bearish'}",
                    f"Bollinger Bands: {signals['bollinger'].capitalize()}",
                    f"Volume: {'Spike' if signals['volume_spike'] else 'Normal'}",
                    f"Direction: {'CALL (Bullish)' if direction == 'call' else 'PUT (Bearish)'}",
                    f"{news_summary}"
                ]
                result_layout = [[sg.Text("\n".join(signal_list), font=("Helvetica", 11), text_color="#2222CC")]]
                show_options = (provider == "Yahoo Finance (default)") and (options_chains and any(options_chains.values()))
                if show_options:
                    capital_layout = [
                        [sg.Text("How much capital (USD) do you want to use for this trade?")],
                        [sg.Input(key="capital", size=(15,1)), sg.Button("OK")]
                    ]
                    cap_window = sg.Window("Capital Input", capital_layout, modal=True, finalize=True)
                    while True:
                        ev_cap, cap_vals = cap_window.read()
                        if ev_cap == "OK":
                            try:
                                capital = float(cap_vals.get("capital", ""))
                                break
                            except:
                                continue
                        elif ev_cap in (sg.WINDOW_CLOSED, "Exit"):
                            capital = 0
                            break
                    cap_window.close()
                else:
                    capital = 0
                top3_contracts = []
                if show_options:
                    top3_contracts = find_best_options(
                        options_chains, underlying_price, direction, capital, top_n=3
                    )
                log_info = {
                    'entry_timestamp': str(datetime.now()),
                    'exit_timestamp': '',
                    'ticker': ticker,
                    'price': underlying_price,
                    'signals': str(signals),
                    'direction': direction,
                    'news_summary': news_summary,
                    'rec1': str(top3_contracts[0]) if len(top3_contracts) > 0 else "",
                    'rec2': str(top3_contracts[1]) if len(top3_contracts) > 1 else "",
                    'rec3': str(top3_contracts[2]) if len(top3_contracts) > 2 else "",
                    'entry_price': top3_contracts[0]['option']['ask'] if top3_contracts else "",
                    'entry_capital': top3_contracts[0]['total_cost'] if top3_contracts else "",
                    'exit_price': '',
                    'realized_outcome': ''
                }
                log_trade_result(TRADE_LOG_PATH, log_info)
                option_summary = []
                if show_options:
                    if len(top3_contracts) == 0:
                        option_summary.append([sg.Text("No suitable option contract found in your budget.", text_color="#800000")])
                    else:
                        option_summary.append([sg.Text("Top 3 Contract Recommendations", text_color="#0055CC", font=("Helvetica", 13))])
                        for idx, rec in enumerate(top3_contracts):
                            opt = rec['option']
                            option_summary += [
                                [sg.Text(f"#{idx+1} Buy {rec['num_contracts']} {opt['expiry']} {opt['strike']}$ {opt['type'].upper()}s @ ${opt['ask']:.2f}")],
                                [sg.Text(f"    Total cost: ${rec['total_cost']:.2f}")],
                                [sg.Text(f"    Estimated profit: {rec['estimated_profit_pct']}% (Confidence: {rec['confidence']}%)")],
                                [sg.Text(f"    Suggested exit: Close near late June or at 25-40% profit.")],
                                [sg.Text("-"*40, text_color="#888888")]
                            ]
                elif provider != "Yahoo Finance (default)":
                    option_summary.append([sg.Text("Options recommendations only available with Yahoo Finance!", text_color="#800000")])
                result_layout += [[sg.HorizontalSeparator()]] + option_summary
                result_layout += [
                    [sg.Button("Show Chart/Explanation"), sg.Button("OK")]
                ]
                result_window = sg.Window("Recommendation", result_layout, modal=True, finalize=True, size=(540, 600))
                while True:
                    event_result, _ = result_window.read(timeout=100)
                    if event_result in (sg.WINDOW_CLOSED, "OK"):
                        break
                    elif event_result == "Show Chart/Explanation":
                        plot_signals_and_explanations(
                            price_history,
                            techs,
                            signals,
                            direction,
                            ticker,
                            window=120,
                            provider=provider
                        )
                result_window.close()
    window.close()

def gui():
    main_gui()

if __name__ == "__main__":
    gui()