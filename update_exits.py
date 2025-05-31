import pandas as pd
from datetime import datetime, timedelta
from datasource import fetch_option_chain_data

TRADE_LOG = "trade_log.csv"
HOLD_DAYS = 10  # Your fixed holding period

df = pd.read_csv(TRADE_LOG)
now = datetime.now()

for idx, row in df.iterrows():
    if pd.notnull(row.get("exit_price")) and row["exit_price"] != "":
        continue  # already exited

    entry_time = pd.to_datetime(row["entry_timestamp"])
    if (now - entry_time).days < HOLD_DAYS:
        continue  # not due yet

    # Parse rec1 to get contract info
    # Example rec1 string: "{'option': {'type': 'call', 'strike': 100, 'expiry': '2024-06-14', ...}, ...}"
    import ast
    rec1 = row["rec1"]
    try:
        rec_dict = ast.literal_eval(rec1)
        opt = rec_dict['option']
        option_type = opt['type']
        strike = float(opt['strike'])
        expiry = opt['expiry']
        ticker = row['ticker']
        # Fetch option chain for expiry date
        chain = fetch_option_chain_data(ticker, expiry, "Yahoo Finance (default)")
        options = chain.calls if option_type == 'call' else chain.puts
        opt_row = options[options['strike'] == strike]
        if len(opt_row) == 0:
            continue
        exit_price = float(opt_row['ask'].iloc[0])
        df.at[idx, 'exit_timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        df.at[idx, 'exit_price'] = exit_price
        entry_price = float(row["entry_price"])
        realized_outcome = (exit_price - entry_price) / entry_price
        df.at[idx, 'realized_outcome'] = realized_outcome
    except Exception as e:
        print("Could not update exit for row:", idx, e)

df.to_csv(TRADE_LOG, index=False)
print("Done updating exits.")
