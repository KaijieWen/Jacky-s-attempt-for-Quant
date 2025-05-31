import pandas as pd
from datetime import datetime, timedelta
from main import compute_recommendation
from datasource import fetch_option_chain_data

symbol = "SPY"
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 4, 1)
capital = 1000
log_rows = []

date = start_date
while date <= end_date:
    print(f"Simulating {date.strftime('%Y-%m-%d')}")
    result = compute_recommendation(symbol, "Yahoo Finance (default)")
    if isinstance(result, str):
        date += timedelta(days=1)
        continue
    contracts = result['options_chains']
    if not contracts:
        date += timedelta(days=1)
        continue
    # Pick top contract as usual
    top = contracts[next(iter(contracts))]  # get first expiry
    if top is None or top.calls.empty:
        date += timedelta(days=1)
        continue
    first_call = top.calls.iloc[0]
    entry_price = float(first_call['ask'])
    expiry = first_call['expiry']
    strike = float(first_call['strike'])
    option_type = "call"
    # Simulate holding for HOLD_DAYS
    exit_date = date + timedelta(days=10)
    exit_chain = fetch_option_chain_data(symbol, expiry, "Yahoo Finance (default)")
    exit_opt_row = exit_chain.calls[exit_chain.calls['strike'] == strike]
    exit_price = float(exit_opt_row['ask'].iloc[0]) if not exit_opt_row.empty else None
    realized_outcome = (exit_price - entry_price) / entry_price if exit_price else None

    log_rows.append({
        "entry_timestamp": date.strftime("%Y-%m-%d"),
        "exit_timestamp": exit_date.strftime("%Y-%m-%d"),
        "ticker": symbol,
        "strike": strike,
        "expiry": expiry,
        "option_type": option_type,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "realized_outcome": realized_outcome
    })
    date += timedelta(days=1)

pd.DataFrame(log_rows).to_csv("backtest_results.csv", index=False)
print("Backtest simulation complete.")
