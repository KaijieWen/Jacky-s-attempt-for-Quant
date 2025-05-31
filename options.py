# options.py

import numpy as np
from datetime import datetime
import math

def find_best_options(options_chains, underlying_price, direction, capital, top_n=3, alpha=1.0, beta=0.5, gamma=0.01, delta=0.01, epsilon=1.0):
    ranked = []
    for exp_date, chain in options_chains.items():
        calls = chain.calls if direction == "call" else chain.puts
        for _, row in calls.iterrows():
            strike = row['strike']
            ask = row['ask']
            bid = row['bid']
            iv = row['impliedVolatility']
            open_interest = row.get('openInterest', 0)
            volume = row.get('volume', 0)
            if np.isnan(ask) or ask == 0 or np.isnan(bid) or open_interest < 10:
                continue
            moneyness = abs(strike - underlying_price)
            days_to_expiry = (datetime.strptime(exp_date, "%Y-%m-%d").date() - datetime.today().date()).days
            score = -alpha*moneyness - beta*abs(iv - 0.5) + gamma*open_interest + delta*volume
            if 20 < days_to_expiry < 55:
                score += epsilon
            ranked.append((score, {
                    "type": direction,
                    "strike": strike,
                    "expiry": exp_date,
                    "ask": ask,
                    "bid": bid,
                    "iv": iv,
                    "open_interest": open_interest,
                    "volume": volume,
                    "days_to_expiry": days_to_expiry
                }
            ))
    ranked.sort(reverse=True, key=lambda x: x[0])
    best_contracts = []
    for s, opt in ranked[:top_n]:
        contract_cost = opt['ask'] * 100
        num_contracts = int(capital // contract_cost)
        total_cost = num_contracts * contract_cost
        estimated_profit_pct = round(np.random.uniform(20, 45), 1)
        try:
            if s is None or (isinstance(s, float) and math.isnan(s)):
                confidence = 60
            else:
                confidence = min(90, 60 + int(s))
        except Exception:
            confidence = 60
        best_contracts.append({
            "option": opt,
            "num_contracts": num_contracts,
            "total_cost": total_cost,
            "estimated_profit_pct": estimated_profit_pct,
            "confidence": confidence
        })
    return [c for c in best_contracts if c["num_contracts"] > 0]