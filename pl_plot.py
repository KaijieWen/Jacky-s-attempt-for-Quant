import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('trade_log.csv', parse_dates=['entry_timestamp','exit_timestamp'])
df = df.dropna(subset=['realized_outcome'])
df['pnl_usd'] = df['realized_outcome'] * df['entry_capital']
df['cumulative_pnl'] = df['pnl_usd'].cumsum()
plt.plot(df['exit_timestamp'], df['cumulative_pnl'])
plt.ylabel('Cumulative P/L (USD)')
plt.xlabel('Date')
plt.title('Backtest Performance')
plt.grid(True)
plt.show()

# Summary stats
print("Win rate:", (df['realized_outcome'] > 0).mean())
print("Mean return:", df['realized_outcome'].mean())
print("Median return:", df['realized_outcome'].median())
print("Max drawdown:", (df['cumulative_pnl'].cummax() - df['cumulative_pnl']).max())
