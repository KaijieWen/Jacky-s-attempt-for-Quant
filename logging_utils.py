# logging_utils.py

import csv
import os

def log_trade_result(log_path, info):
    file_exists = os.path.isfile(log_path)
    fieldnames = [
        'entry_timestamp', 'exit_timestamp',
        'ticker', 'price', 'signals', 'direction', 'news_summary',
        'rec1', 'rec2', 'rec3',
        'entry_price', 'entry_capital', 'exit_price', 'realized_outcome'
    ]
    with open(log_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(info)