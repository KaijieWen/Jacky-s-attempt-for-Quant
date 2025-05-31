
# Options Trading Recommendation Platform

A Python-powered application that delivers intelligent options trade recommendations by combining real-time market data with an offline machine-learning pipeline. It computes advanced technical indicators, ranks option contracts, and provides a user-friendly GUI—while also allowing you to retrain the underlying model on historical CSV data when the market is closed.

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
   - [Offline (Retraining) Mode](#offline-retraining-mode)  
5. [Core Components](#core-components)  
   - [Configuration (`config.py`)](#configuration-configpy)  
   - [Data Sources (`datasource.py`)](#data-sources-datasourcepy)  
   - [Indicator Library (`technicals.py`)](#indicator-library-technicalspy)  
   - [Option Ranking (`options.py`)](#option-ranking-optionspy)  
   - [Plotting & Visualization (`plotting.py`)](#plotting--visualization-plottingpy)  
   - [Logging (`logging_utils.py`)](#logging-logging_utilspy)  
   - [Offline Training (`model_training_csv.py` & `offline_options.py`)](#offline-training-model_training_csvpy--offline_optionspy)  
   - [Main Application (`main.py`)](#main-application-mainpy)  
6. [Dependencies](#dependencies)  
7. [Contributing](#contributing)  
8. [License](#license)

---

## Project Overview

This project delivers an end-to-end, Python-based solution for generating options trade recommendations:

- **Live Mode:**  
  - Fetches up-to-date price history, option chains, and (optionally) news sentiment through Yahoo Finance, Alpha Vantage, or Polygon.io.  
  - Computes a suite of technical indicators (RSI, MACD histogram, Bollinger bands, volume spikes, etc.) and generates “call” vs. “put” signals.  
  - Ranks available option contracts by moneyness, implied volatility, open interest, and a custom scoring function.  
  - Displays results in a GUI built with FreeSimpleGUI/PySimpleGUI, complete with charts and “Top 3” contract recommendations.

- **Offline (Closed-Market) Mode:**  
  - Instead of waiting for the market to open, you can flip a toggle (“Offline Mode”) and retrain the model on historical CSV files stored under a `training_dataset/` folder.  
  - A Random Forest classifier ingests OHLCV CSVs (named `<TICKER>_historical_data.csv`) and learns next-day direction labels, reporting test accuracy and ROC-AUC.  
  - The newly trained model (serialized to `model_csv.pkl`) can then be used for real-time predictions, ensuring that your system continuously improves as you add more historical data.

---

## Key Features

- **Real-Time Data Integration:**  
  - Support for Yahoo Finance (via `yfinance`), Alpha Vantage, and Polygon.io to fetch live price/option-chain data and (optionally) news sentiment.
- **Robust Technical Indicator Library:**  
  - Computes moving averages, RSI, MACD histograms, Bollinger band positions, volume spikes, on-balance volume, Renko bricks, support/resistance, trendlines, and more.
- **Machine-Learning Pipeline:**  
  - Random Forest model trained on historical CSV data (offline mode) to predict next-day stock movement.  
  - Continuous retraining capability when the market is closed, so the model becomes “smarter” over time.
- **Options Chain Ranking:**  
  - Ranks contracts by moneyness, implied volatility, open interest, and a custom score that incorporates model confidence.
- **Interactive GUI:**  
  - Built with FreeSimpleGUI/PySimpleGUI.  
  - Rapidly displays signals, plots, and top-3 option recommendations.  
  - Automatically logs trades to `trade_log.csv`.
- **Seamless Mode Toggle:**  
  - Single boolean flag (`OFFLINE_MODE`) in `config.py` to switch between “live” and “offline” operation.

---

## Getting Started

### Prerequisites

- **Python 3.8+**  
- **API Keys** (for live-mode functionality):  
  - **Alpha Vantage API key** (free signup at [alphavantage.co](https://www.alphavantage.co/))  
  - **Polygon.io API key** (optional, for options data)
- **pip** (package installer for Python)

### Installation

1. **Clone the repository** (or copy files into your local folder):

   ```bash
   git clone https://github.com/yourusername/options-recommendation-platform.git
   cd options-recommendation-platform
   ```

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate.bat     # Windows
   ```

3. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   > If you don’t have a `requirements.txt`, you can install manually:
   >
   > ```bash
   > pip install pandas numpy scikit-learn yfinance FreeSimpleGUI pandas_ta stocktrends scipy matplotlib pandas_market_calendars
   > ```

### Folder Structure

```plaintext
my_trading_project/
├── config.py
├── datasource.py
├── logging_utils.py
├── main.py
├── model_training_csv.py         ← New (Offline Training)
├── offline_options.py            ← New (Offline Recommendation)
├── options.py
├── plotting.py
├── technicals.py
├── backtest.py
├── pl_plot.py
├── update_exits.py
├── trade_log.csv
├── training_dataset/             ← Historical CSVs
│   ├── NVDA_historical_data.csv
│   ├── GOOGL_historical_data.csv
│   └── MNST_historical_data.csv
├── model_csv.pkl                 ← Generated by offline training
└── requirements.txt
```

- **`config.py`**: Global configuration (API keys, offline toggle, paths).  
- **`datasource.py`**: Functions to fetch prices, history, options, and news sentiment.  
- **`logging_utils.py`**: CSV logging utility for trade results.  
- **`technicals.py`**: Technical indicator calculations (RSI, MACD, Bollinger, Renko, etc.).  
- **`plotting.py`**: Chart plotting functions.  
- **`options.py`**: Original logic for ranking option contracts (live mode).  
- **`main.py`**: Entry-point for the GUI; checks `OFFLINE_MODE` and runs either live GUI or offline training.  
- **`model_training_csv.py`**: Offline training script for Random Forest.  
- **`offline_options.py`**: Helper to produce one offline recommendation from CSV.  
- **`training_dataset/`**: Contains `<TICKER>_historical_data.csv` files for offline training.  
- **`model_csv.pkl`**: Serialized RandomForest model (created post-training).  
- **`trade_log.csv`**: Logs each recommendation/trade from the GUI.

---

## Usage

### Live (Real-Time) Mode

Run the GUI and fetch live data:

```bash
# Ensure OFFLINE_MODE is not enabled:
export OFFLINE_MODE="false"   # macOS/Linux
# or
unset OFFLINE_MODE

python main.py
```

- The GUI window appears.  
- Enter **Stock Symbol**, choose **Data Source** (Yahoo Finance, Alpha Vantage, or Polygon.io), optionally check **“Include News Sentiment”**, then click **Submit**.  
- The application:
  1. Fetches historical price data (`fetch_history`) from the chosen provider.  
  2. Computes technical indicators (`compute_technical_indicators`) and signals (`compute_signals`).  
  3. Optionally fetches news sentiment (`fetch_news_sentiment`).  
  4. Determines “call” vs. “put” via the signals.  
  5. Fetches current price (`fetch_current_price`) and option chains (`fetch_options_chain`).  
  6. Ranks top-3 option contracts with `find_best_options()`.  
  7. Plots explanation charts (`plot_signals_and_explanations`) and displays recommendations.  
  8. Logs the recommendation/trade to `trade_log.csv`.

### Offline (Retraining) Mode

Use this when the market is closed to rebuild the model on historical CSVs:

1. Ensure your OHLCV CSVs are placed in `training_dataset/`, named `<TICKER>_historical_data.csv` (e.g., `NVDA_historical_data.csv`).  
2. Enable offline mode:

   ```bash
   export OFFLINE_MODE="true"  # macOS/Linux
   # or (Windows PowerShell)
   setx OFFLINE_MODE "true"
   ```

3. Run:

   ```bash
   python main.py
   ```

- The program sees `OFFLINE_MODE=True` and skips the GUI.  
- Prints:

  ```
  [INFO] OFFLINE_MODE is True. Starting offline training on CSV dataset...
  ```

- Calls `model_training_csv.py`, which:
  1. Loads all CSVs from `training_dataset/`.  
  2. Computes technical features and labels next-day direction.  
  3. Splits into 80% train / 20% test.  
  4. Trains a Random Forest on the training set; prints test accuracy & ROC-AUC.  
  5. Retrains on all data; saves final model to `model_csv.pkl`.  
  6. Prints:

     ```
     [model_training_csv] Saving final model to model_csv.pkl
     [model_training_csv] Offline model training complete.
     ```

- Next, the script prompts:

  ```
  Enter ticker for offline prediction (e.g., NVDA):
  ```

  - Type, for example: `NVDA`

  ```
  Enter direction ('call' or 'put'):
  ```

  - Type: `call`

  ```
  Enter capital in USD (e.g., 1000):
  ```

  - Type: `1000`

- Calls `offline_find_best_options("NVDA", "call", 1000)` from `offline_options.py`, which:
  1. Loads `training_dataset/NVDA_historical_data.csv`.  
  2. Computes the latest 5-feature vector.  
  3. Loads `model_csv.pkl`; predicts call/put probability.  
  4. Calculates `confidence_pct` and `estimated_profit_pct`.  
  5. Prints:

     ```
     Offline Recommendation:
       ticker: NVDA
       latest_date: 2025-05-30
       latest_close: 415.32
       predicted_direction: call
       confidence_pct: 62.3
       estimated_profit_pct: 12.3
       note: Offline mode: using model trained on historical CSV
     ```

- Finally, prints:

  ```
  [INFO] Exiting because OFFLINE_MODE was True.
  ```

- Program exits. No GUI appears in offline mode.

4. Verify that `model_csv.pkl` was created at the project root. This is your updated offline model.

### Switching Back to Live Mode

After offline retraining, disable offline mode:

```bash
unset OFFLINE_MODE            # macOS/Linux
# or
setx OFFLINE_MODE "false"     # Windows
```

Then run the GUI normally:

```bash
python main.py
```

The GUI will launch, using the newly trained `model_csv.pkl` (as a fallback model) to score live signals and rank options contracts.

---

## Core Components

### Configuration (`config.py`)

- Holds global constants:  
  - `DEFAULT_ALPHA_VANTAGE_KEY`, `DEFAULT_POLYGON_KEY`, `TRADE_LOG_PATH`.  
- ***New additions for offline mode:***  
  - `OFFLINE_MODE`: when `True`, skip live data fetch and train on CSVs.  
  - `TRAINING_DATASET_FOLDER`: folder path for CSV files.  
  - `OFFLINE_MODEL_PATH`: filepath to save/load the offline Random Forest model.

### Data Sources (`datasource.py`)

- **`fetch_current_price(symbol, data_source, av_api_key, polygon_api_key)`**  
  Retrieves the latest numeric price for `symbol` from Yahoo Finance, Alpha Vantage, or Polygon.io.

- **`fetch_history(symbol, start_date, end_date, av_api_key, polygon_api_key)`**  
  Fetches historical OHLCV data for `symbol` between `start_date` and `end_date`, returning a pandas DataFrame.

- **`fetch_options_chain(symbol, expiration_date, av_api_key, polygon_api_key)`**  
  Returns a list or dictionary of available option contracts for `symbol` at `expiration_date`.

- **`fetch_option_chain_data(symbol, expiration_date, strike, av_api_key, polygon_api_key)`**  
  Returns detailed bid/ask/implied volatility/open interest/volume data for a specific option contract.

- **`fetch_news_sentiment(symbol, from_date, to_date, api_key)`**  
  Queries a news-sentiment API (e.g., Finnhub, NewsAPI) for `symbol` between `from_date` and `to_date`. Returns `(avg_score, error_message)`.

> **All datasource functions remain unchanged**. They continue to handle real-time API calls in live mode.

### Indicator Library (`technicals.py`)

- **`compute_technical_indicators(df)`**  
  Calculates and returns a dictionary of technical indicators including:  
  - `sma20`, `sma50`, `sma200` (simple moving averages)  
  - `rsi` (relative strength index)  
  - `macd`, `macd_signal` (moving average convergence/divergence)  
  - `bb_upper`, `bb_middle`, `bb_lower` (Bollinger bands)  
  - `volume_ma20` (20-day volume average)  
  - `renko`, `support_resistance`, `dynamic_sr`, `trendline`, `stochastic`, `obv`, `moon_phase`, etc.  

- **`compute_signals(df)`**  
  Produces a signals dictionary:  
  - `above_ma20`, `ma_crossover`, `rsi_status`, `macd_cross`, `vol_spike`, `bollinger`.  

- **`generate_direction(signals)`**  
  Returns `'call'` if bullish logic is met, else `'put'`.

- **`on_balance_volume(df)`**  
  Computes the on-balance volume time series from OHLCV.

> **Unchanged**—all original indicator code is preserved.

### Option Ranking (`options.py`)

- **`find_best_options(options_chains, underlying_price, direction, capital, top_n=3)`**  
  - Iterates through all option contracts in `options_chains`.  
  - Calculates `moneyness`, `days_to_expiry`, and a custom `score` incorporating implied volatility, open interest, and volume.  
  - Filters for contracts fitting criteria (e.g., 20 < days_to_expiry < 55).  
  - Computes a random placeholder `estimated_profit_pct` and a confidence score (based on a sentiment placeholder `s`).  
  - Returns a list of up to `top_n` affordable contracts (contracts > 0) sorted by `score`.

> **Unchanged**—used only in live mode.

### Plotting & Visualization (`plotting.py`)

- **`auto_fit_font(ax, num_labels, min_size=7, max_size=14)`**  
  Adjusts font size of tick labels based on the number of data points.

- **`plot_signals_and_explanations(price_history, techs, signals, direction, ticker, window=120, provider="...")`**  
  Creates a matplotlib figure showing:
  - Close price with overlays: SMA20, SMA50, Bollinger bands, etc.
  - Optionally, subplots for RSI, MACD, or other indicators.

- **`plot_confidence_over_time(dates, confidences)`**  
  Plots a simple line chart of model confidence percentages over time.

> **Unchanged**—exactly as originally provided.

### Logging (`logging_utils.py`)

- **`log_trade_result(log_path, info)`**  
  Appends a dictionary to `log_path` (CSV). Writes a header once and appends each row thereafter.

> **Unchanged**.

### Offline Training & Recommendation

#### `model_training_csv.py`

- **`load_all_csvs(folder_path)`**  
  Reads all CSV files ending with `_historical_data.csv` in `folder_path`. Returns a single concatenated DataFrame with an extra `Ticker` column.

- **`compute_technical_features(df)`**  
  For each ticker group, computes five features:
  - `SMA20_div_SMA50`, `RSI`, `MACD_hist`, `BB_pos`, `Vol_spike`.
  - Also generates a `Label` (1 if next-day return > 0, 0 otherwise).

- **`train_and_save_model()`**  
  1. Loads all CSVs → DataFrame.
  2. Computes feature DataFrame (`X`) and labels (`y`).
  3. Splits 80% train / 20% test: trains `RandomForestClassifier`. Prints test accuracy & ROC-AUC.
  4. Retrains on 100% of data → saves final model to `model_csv.pkl`. Prints completion message.

#### `offline_options.py`

- **`compute_offline_features_from_csv(df_price)`**  
  Applies the exact same five feature calculations (SMA20/SMA50 ratio, RSI, MACD, Bollinger position, volume spike) to a historical-CSV DataFrame. Returns a NumPy array of shape (1,5).

- **`offline_find_best_options(ticker, direction, capital)`**  
  1. Loads `<ticker>_historical_data.csv` from `TRAINING_DATASET_FOLDER`.
  2. Computes feature vector via `compute_offline_features_from_csv()`.
  3. Loads `model_csv.pkl` and predicts call/put probability → sets `confidence_pct`.
  4. Maps `confidence_pct` to `estimated_profit_pct` (`max(confidence*100 – 50, 5)`).
  5. Returns a dictionary with keys:
     - `ticker`, `latest_date`, `latest_close`,
     - `predicted_direction`, `confidence_pct`, `estimated_profit_pct`, `note`.

> These two files are new. They do not modify or remove any existing function. They provide offline training and offline recommendation capabilities.

### Main Application (`main.py`)

- **Imports**:
  - Original imports for GUI, data fetching, indicators, option ranking, plotting, logging, and market calendar checks.
  - ***New imports:***
    ```python
    import config
    from model_training_csv import train_and_save_model
    from offline_options import offline_find_best_options
    ```
- **`is_us_market_open(date=None)`**: Checks if NYSE is open on a given date using `pandas_market_calendars`.
- **`compute_recommendation(...)`**: Your original function for fetching history, computing signals, fetching options, etc. Unmodified.
- **`main_gui()`**:
  - Contains your entire GUI layout and event loop exactly as originally written.
  - ***Addition:*** If `config.OFFLINE_MODE == True`, shows a popup “Offline mode is ON. GUI is disabled in offline mode.” and skips the rest.
- **`gui()`** simply calls `main_gui()`.
- **`if __name__ == "__main__":`**
  - Checks `config.OFFLINE_MODE`.
    - If `True`:
      1. Prints an info message.
      2. Calls `train_and_save_model()` (offline retraining).
      3. Prompts for `ticker`, `direction`, `capital`.
      4. Calls `offline_find_best_options(...)`, prints the single dictionary, then exits.
    - If `False`: calls `gui()` (launches your unchanged GUI).

> **No original code in `main_gui()` or `compute_recommendation()` was removed or altered—only a few lines added to check `OFFLINE_MODE` at runtime.**

---

## Dependencies

- **Python 3.8+**
- **pip packages** (as listed in `requirements.txt`, or install manually):
  ```bash
  pandas
  numpy
  scikit-learn
  yfinance
  FreeSimpleGUI         # or PySimpleGUI
  pandas_ta
  stocktrends
  scipy
  matplotlib
  pandas_market_calendars
  ```
- **API Keys (for live mode)**:
  - Alpha Vantage API key
  - Polygon.io API key (optional)

---

## Contributing

1. **Fork** this repository.
2. **Create** a branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Make changes**, ensuring that both live GUI and offline training still function correctly.
4. **Add tests** for any new functionality.
5. **Submit** a pull request detailing your changes, new dependencies, and any setup instructions.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
