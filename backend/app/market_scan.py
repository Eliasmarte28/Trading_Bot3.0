import datetime
import json
import pandas as pd
import pandas_ta as ta
from .capitalcom_api import CapitalComAPI
from .config import settings

# Analysis and auto-trading logic
def analyze_asset(symbol, api: CapitalComAPI):
    candles = api.get_history(symbol, timeframe="1h", count=100)
    df = pd.DataFrame(candles.get("candles", []))
    if df.empty or "close" not in df:
        return [], None

    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df = df.dropna(subset=["close"])
    signals = []
    trade_action = None

    # RSI
    df["rsi"] = ta.rsi(df["close"], length=14)
    if df['rsi'].iloc[-1] < 30:
        signals.append("RSI oversold (potential bounce)")
        trade_action = "BUY"
    if df['rsi'].iloc[-1] > 70:
        signals.append("RSI overbought (potential reversal)")
        trade_action = "SELL"

    # SMA Crossover
    df["sma_fast"] = ta.sma(df["close"], length=9)
    df["sma_slow"] = ta.sma(df["close"], length=21)
    if len(df) >= 2:
        if (
            df["sma_fast"].iloc[-2] < df["sma_slow"].iloc[-2]
            and df["sma_fast"].iloc[-1] > df["sma_slow"].iloc[-1]
        ):
            signals.append("Bullish SMA crossover")
            trade_action = "BUY"
        if (
            df["sma_fast"].iloc[-2] > df["sma_slow"].iloc[-2]
            and df["sma_fast"].iloc[-1] < df["sma_slow"].iloc[-1]
        ):
            signals.append("Bearish SMA crossover")
            trade_action = "SELL"

    # Volatility spike
    df["volatility"] = ta.stdev(df["close"], length=10)
    if df["volatility"].iloc[-1] > df["volatility"].mean() * 2:
        signals.append("Volatility spike")

    return signals, trade_action

def generate_daily_report(api_key, demo=True, top_n=10, do_auto_trade=True, trade_amount=1.0):
    api = CapitalComAPI(api_key, demo=demo)
    assets = api.get_assets()
    results = []
    trade_results = []
    for asset in assets:
        symbol = asset.get('symbol') or asset.get('market')
        if not symbol:
            continue
        signals, trade_action = analyze_asset(symbol, api)
        if signals:
            results.append({"symbol": symbol, "signals": signals})
            # Auto-trade if enabled and there is a clear action
            if do_auto_trade and trade_action in ["BUY", "SELL"]:
                trade_result = api.place_order(symbol, trade_action, trade_amount)
                trade_results.append({
                    "symbol": symbol,
                    "side": trade_action,
                    "response": trade_result
                })
    ranked = sorted(results, key=lambda x: len(x["signals"]), reverse=True)[:top_n]
    report = {
        "date": datetime.datetime.utcnow().isoformat(),
        "assets": ranked,
        "auto_trades": trade_results
    }
    with open(settings.daily_report_file, "w") as f:
        json.dump(report, f, indent=2)
    return report