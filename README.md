# Options Trading Recommendation Platform

A Python-powered application that delivers intelligent options trade recommendations by combining real-time market data with a rich suite of technical indicators. Use the user-friendly GUI for live analysis and options ranking—or flip on “Offline Training Mode” to run full technical/trend analysis and charting based on your own historical CSVs when the market is closed.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
   - [Folder Structure](#folder-structure)  
4. [Usage](#usage)  
   - [Live (Real-Time) Mode](#live-real-time-mode)  
   - [Offline (Backtest/Analysis) Mode](#offline-backtestanalysis-mode)  
5. [Core Components](#core-components)  
6. [Dependencies](#dependencies)  
7. [Contributing](#contributing)  
8. [License](#license)

---

## Project Overview

This project is an end-to-end Python solution for options trade analysis and technical charting:

- **Live Mode (Online):**
  - Fetches up-to-date price history, option chains, and (optionally) news sentiment via Yahoo Finance, Alpha Vantage, or Polygon.io.
  - Computes a suite of technical indicators (RSI, MACD, Bollinger bands, volume spikes, support/resistance, trendlines, and more).
  - Ranks option contracts by moneyness, implied volatility, open interest, and a custom scoring function.
  - Presents a clean GUI (FreeSimpleGUI/PySimpleGUI) with charting and “Top 3” contract recommendations, and logs trades for backtesting.

- **Offline Mode (Closed Market/Backtest/Training):**
  - Flip the “Offline Training Mode” checkbox in the GUI to run the full technical and trend analysis pipeline on your own historical CSV data (located in `training_dataset/`).  
  - No real-time data is fetched—**no options contracts are ranked or recommended in offline mode.**  
  - Instead, you get instant charting, full indicator calculation, and trend signal explanations for any ticker you have local data for.

---

## Key Features

- **Live Market Data Integration:**  
  - Supports Yahoo Finance, Alpha Vantage, and Polygon.io APIs for historical and real-time prices, option chains, and news sentiment.

- **Technical Indicator Suite:**  
  - Computes moving averages, RSI, MACD, Bollinger bands, volume spikes, support/resistance, trendlines, Renko, Heikin Ashi, Fibonacci retracement, and more.

- **Options Chain Ranking:**  
  - Ranks and recommends options contracts based on moneyness, IV, open interest, volume, days to expiry, and custom weights.

- **Interactive GUI:**  
  - Built with FreeSimpleGUI/PySimpleGUI for simple use.
  - Input ticker, select data source, toggle offline mode, and instantly visualize charting/analysis.

- **Seamless Offline Mode:**  
  - Instantly switch to local CSV-driven analysis and charting when the market is closed, with no dependency on any APIs.

- **Performance Logging and Backtesting:**  
  - Every recommendation and trade is logged to `trade_log.csv` for future backtest analysis and P/L visualization.

---

## Getting Started

### Prerequisites

- **Python 3.8+**
- **API Keys** for live mode (get a free Alpha Vantage key [here](https://www.alphavantage.co/support/#api-key); Polygon.io is optional for extra data)
- **pip** (Python package installer)

### Installation

1. **Clone this repo:**

   ```bash
   git clone https://github.com/yourusername/options-recommendation-platform.git
   cd options-recommendation-platform
   ```

2. **(Recommended) Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate.bat   # Windows
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Or manually:

   ```bash
   pip install pandas numpy scikit-learn yfinance FreeSimpleGUI pandas_ta stocktrends scipy matplotlib pandas_market_calendars
   ```

### Folder Structure

```plaintext
my_trading_project/
├── config.py
├── datasource.py
├── logging_utils.py
├── main.py
├── options.py
├── plotting.py
├── technicals.py
├── backtest.py
├── pl_plot.py
├── update_exits.py
├── trade_log.csv
├── training_dataset/
│   ├── NVDA_historical_data.csv
│   ├── GOOGL_historical_data.csv
│   └── MNST_historical_data.csv
├── requirements.txt
```

- **`config.py`**: Global constants (API keys, log file paths, dataset folder).
- **`datasource.py`**: Unified data source handlers for both online and offline (CSV) fetches.
- **`main.py`**: Launches the GUI and controls live/offline workflow.
- **`options.py`**: Ranks and filters option contracts for recommendations.
- **`technicals.py`**: Calculates all technical indicators and signal flags.
- **`plotting.py`**: Advanced matplotlib charting/annotation for both online and offline modes.
- **`logging_utils.py`**: CSV-based logging for trade recommendations.
- **`backtest.py`, `update_exits.py`, `pl_plot.py`**: Tools for P/L visualization, automated backtests, and log maintenance.
- **`training_dataset/`**: Folder for local CSVs used in offline mode (must be named like `NVDA_historical_data.csv`).

---

## Usage

### Live (Real-Time) Mode

1. Run the main program:

   ```bash
   python main.py
   ```

2. In the GUI:
    - Enter a **stock symbol** (e.g., `NVDA`).
    - Select a **data source** (Yahoo Finance, Alpha Vantage, or Polygon.io).
    - (Optional) Enter API keys for live sentiment or advanced data.
    - (Optional) Check **"Include News Sentiment"** for sentiment-based signals.
    - **Do NOT check "Offline Training Mode"**—leave it unchecked for live data.

3. Click **Submit** to get:
    - Live price chart with technical/trend overlays.
    - Bullish/bearish signals and explanations.
    - Top-3 option contract recommendations.
    - Trade logged to `trade_log.csv` for backtesting.

### Offline (Backtest/Analysis) Mode

Use this mode to run full technical/trend analysis and charting on **your own CSVs** without fetching any data from APIs.

1. Place historical OHLCV CSV files (named like `NVDA_historical_data.csv`) in the `training_dataset/` folder.

2. Run the program as usual:

   ```bash
   python main.py
   ```

3. **Check the "Offline Training Mode" box** in the GUI.

4. Enter a **stock symbol** that matches your CSV (e.g., `NVDA`).

5. Click **Submit** to:
    - Instantly load and chart the historical data.
    - Run the full technical/trend analysis pipeline and explanations.
    - **No options will be recommended**; this mode is for chart/indicator analysis only.

---

## Core Components

- **config.py:** Central location for keys, file paths, and offline mode settings.
- **datasource.py:** Handles all data acquisition, including CSV reading in offline mode.
- **main.py:** Controls GUI workflow and dispatches to correct online/offline branch.
- **technicals.py:** Computes all major indicators and pattern flags.
- **options.py:** Option contract ranking and selection logic (online mode only).
- **plotting.py:** Creates rich matplotlib charts for both live and offline data.
- **logging_utils.py:** Appends all trade recommendations and outcomes to `trade_log.csv`.
- **backtest.py / update_exits.py / pl_plot.py:** Scripts for log analysis, automated backtesting, and P/L visualization.

---

## Dependencies

- Python 3.8+
- pandas
- numpy
- scikit-learn
- yfinance
- FreeSimpleGUI (or PySimpleGUI)
- pandas_ta
- stocktrends
- scipy
- matplotlib
- pandas_market_calendars

(See `requirements.txt`.)

---

## Contributing

1. **Fork** this repository.
2. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make your changes**, ensuring both live and offline modes function.
4. **Test thoroughly** and submit a pull request with clear description.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
