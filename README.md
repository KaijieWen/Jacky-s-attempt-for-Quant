# Jacky Quant Attempt

Jacky Quant Attempt is a research-oriented, Python-powered toolkit for systematic options trading strategy development, technical analysis, and backtesting. Designed for traders and quants, it provides a modern GUI for live market exploration alongside a robust offline mode for historical research and model validation.

---

## Features

- **Real-time Market Analysis**
    - Integrates with Yahoo Finance, Alpha Vantage, and Polygon.io APIs for live equity/option data.
    - Computes advanced technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, Fibonacci retracements, Renko, Heikin-Ashi, trendlines, support/resistance, stochastic oscillator, OBV, and more.
    - Optional news sentiment analysis (Alpha Vantage).
    - Automated multi-factor options contract screening: moneyness, IV, open interest, liquidity, DTE, etc.
    - Interactive plotting and rich signal explanations for technical/trend events.

- **Offline (Training) Mode**
    - Analyze and visualize strategies using pre-downloaded historical price CSVs (no internet required).
    - Full indicator and trend charting when markets are closed or for deterministic backtesting.
    - Enables model prototyping and validation in a reproducible environment.

- **Trade Logging & Backtest Framework**
    - Persistent log of every recommendation, including entry/exit, contract, realized P&L, win/loss, and capital allocation.
    - Batch update and performance scripts for historical win rates, average returns, and cumulative equity curves.
    - Standardized signal evaluation and model validation tools.

---

## Current Capabilities

- **GUI Front-End**
    - User-friendly interface (PySimpleGUI/FreeSimpleGUI) for ticker selection, data source, API keys, and toggling offline mode.
    - Actionable outputs in both online and offline modes.

- **Offline Mode (Technical-Only)**
    - Loads OHLCV data from `training_dataset/{SYMBOL}_historical_data.csv`.
    - Computes and visualizes all technical/trend signals.
    - Skips options contract recommendations (options backtesting planned).

- **Online Mode**
    - Fetches live historical and options chain data.
    - Computes technical/sentiment signals and generates ranked option picks.
    - Records all recommendations to `trade_log.csv` for later audit/performance review.

- **Performance Tracking**
    - Scripts for updating trade outcomes and plotting cumulative P&L and win statistics.

---

## In Progress

- **Offline Mode Options Backtest**
    - Planned support for loading and simulating options chains from local CSVs.
- **ML-Based Signal/Prediction Engine**
    - Forthcoming integration of ML models for win-probability calibration using offline-mode logs.
- **Automated Hyperparameter Tuning**
    - Grid search and scoring parameter optimization tools.
- **Statistical Reporting**
    - Advanced analytics: rolling Sharpe, drawdown, strategy comparison, improved plots.

---

## Usage

1. **Clone the repository and install requirements**
    ```bash
    pip install -r requirements.txt
    ```

2. **Prepare offline datasets (optional)**
    - Place historical price CSVs named `{SYMBOL}_historical_data.csv` in `/training_dataset`.

3. **Launch the application**
    ```bash
    python main.py
    ```

4. **Workflow**
    - **Select Data Source**: Choose from "Yahoo Finance (default)", "Alpha Vantage", or "Polygon.io".
    - **Enter Stock Symbol** (e.g., `AAPL`, `NVDA`).
    - **Toggle 'Offline Training Mode'** to use local CSVs for backtesting and technical analysis.
    - **Review Outputs**: Trend/technical plots and signal explanations (all modes), ranked options recommendations (live only).

---

## Limitations

- Offline mode currently does **not** support options contract simulation; only price/indicator research is available.
- Options backtesting and ML prediction modules are under active development.

---

## Project Status

- **Stable for technical analysis and visualization** in both live and offline modes.
- **Fully functional live options recommendation and trade logging.**
- **Offline options simulation** and **ML/automated backtest pipeline** in development.

---

## Contributing

PRs and issue reports are welcome. For larger contributions, please open an issue to discuss scope and integration.

---

## License

MIT

---

## Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance)
- [Alpha Vantage](https://www.alphavantage.co/)
- [Polygon.io](https://polygon.io/)
- Technical indicator libraries: `pandas_ta`, `stocktrends`, `scikit-learn`, and related packages.

---
