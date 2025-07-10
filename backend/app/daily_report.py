from fastapi import APIRouter, Depends
from datetime import datetime, date, timedelta
import numpy as np

from .models import User
from .capitalcom_api import CapitalComAPI
from .auth import get_current_user

router = APIRouter()

def get_percentage_change(prices):
    if not prices or len(prices) < 2:
        return 0
    return ((prices[-1] - prices[0]) / prices[0]) * 100

def get_volatility(prices):
    if not prices or len(prices) < 2:
        return 0
    return float(np.std(prices))

def get_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - 100 / (1 + rs)
    return float(rsi)

@router.get("/daily-report")
def daily_report(user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        identifier=user.username,
        password=user.password,
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        demo=user.use_demo
    )
    api.session_token = user.cc_session_token

    today = date.today()
    from_date = datetime.combine(today, datetime.min.time()).isoformat() + "Z"
    to_date = datetime.combine(today + timedelta(days=1), datetime.min.time()).isoformat() + "Z"
    trades_data = api.get_trade_history(from_date=from_date, to_date=to_date) or []

    # Debug: print trade history raw data and its type
    print("Trade history raw:", trades_data)
    print("trades_data type:", type(trades_data))

    # Determine the structure of trades
    if isinstance(trades_data, dict):
        trades = trades_data.get("orders", trades_data)
    elif isinstance(trades_data, list):
        trades = trades_data
    else:
        trades = []

    # Debug: print dates or contents of all trades
    for t in trades:
        if isinstance(t, dict):
            print("Trade date:", t.get("date"))
        else:
            print("Trade (unexpected type):", t)

    today_trades = [
        t for t in trades
        if isinstance(t, dict) and "date" in t and datetime.fromisoformat(t["date"]).date() == today
    ]
    total_profit = sum(t.get("profit", 0) for t in today_trades)
    wins = len([t for t in today_trades if t.get("profit", 0) > 0])
    losses = len([t for t in today_trades if t.get("profit", 0) < 0])

    # Get major assets from Capital.com
    assets = api.get_assets()
    major_assets = [a for a in assets if a.get("symbol") in ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD", "GOLD"]]
    if not major_assets:  # fallback to first 6 if none found
        major_assets = assets[:6]

    # Analytics for each asset: percent change, volatility, RSI
    assets_report = []
    for asset in major_assets:
        symbol = asset["symbol"]
        try:
            prices = api.get_price_history(symbol, period="1d", interval="1h")
            close_prices = [c["close"] for c in prices if isinstance(c, dict) and "close" in c]
        except Exception as e:
            print(f"Error fetching prices for {symbol}:", e)
            close_prices = []
        percent_change = get_percentage_change(close_prices)
        volatility = get_volatility(close_prices)
        rsi = get_rsi(close_prices)
        assets_report.append({
            "symbol": symbol,
            "name": asset.get("name"),
            "percent_change": round(percent_change, 3) if percent_change is not None else None,
            "volatility": round(volatility, 3) if volatility is not None else None,
            "rsi": round(rsi, 2) if rsi is not None else None,
        })

    # Assets to Watch: top 3 by abs(% change) or RSI out of range
    sorted_by_move = sorted(assets_report, key=lambda x: abs(x["percent_change"]) if x["percent_change"] is not None else 0, reverse=True)
    assets_to_watch = []
    for a in sorted_by_move:
        if len(assets_to_watch) >= 3:
            break
        if a["rsi"] is not None and (a["rsi"] < 30 or a["rsi"] > 70):
            assets_to_watch.append({**a, "signal": "RSI"})
        elif a["percent_change"] is not None and abs(a["percent_change"]) > 0.5:
            assets_to_watch.append({**a, "signal": "Move"})

    # Market Insights
    trends = []
    for a in assets_report:
        trend = ""
        if a["percent_change"] is not None and a["percent_change"] > 0.5:
            trend = f"{a['symbol']} is up {a['percent_change']}%"
        elif a["percent_change"] is not None and a["percent_change"] < -0.5:
            trend = f"{a['symbol']} is down {a['percent_change']}%"
        if trend:
            trends.append(trend)
    if not trends:
        trends.append("Most major assets are flat today.")
    market_insights = " | ".join(trends)

    return {
        "date": today.isoformat(),
        "num_trades": len(today_trades),
        "total_profit": round(total_profit, 2),
        "wins": wins,
        "losses": losses,
        "trades": today_trades,
        "market_insights": market_insights,
        "assets_to_watch": assets_to_watch
    }