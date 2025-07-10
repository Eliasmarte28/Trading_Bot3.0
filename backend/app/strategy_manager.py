from typing import Dict, List
from .strategy import STRATEGIES
from .analytics import get_backtest_win_rates, get_recent_signal_performance

class StrategyManager:
    def __init__(self, active_strategies: List[str]):
        self.active_strategies = active_strategies

    def get_signals(
        self,
        asset_prices: Dict[str, List[float]],
        backtest_win_rates: Dict[str, Dict[str, float]] = None,  # {symbol: {strategy: win_rate}}
        recent_perf: Dict[str, Dict[str, float]] = None,         # {symbol: {strategy: recent_win_rate}}
        volatility: Dict[str, float] = None                      # {symbol: volatility}
    ) -> Dict[str, Dict]:
        results = {}
        for symbol, prices in asset_prices.items():
            signals = []
            details = {}
            for strat_name in self.active_strategies:
                strat = STRATEGIES.get(strat_name)
                if strat:
                    s, c = strat.generate_signal(prices)
                    details[strat_name] = {"signal": s, "raw_confidence": c}
                    # Factor in backtest win rate and recent performance
                    strat_conf = c
                    if backtest_win_rates and symbol in backtest_win_rates and strat_name in backtest_win_rates[symbol]:
                        strat_conf *= (0.6 + 0.4 * backtest_win_rates[symbol][strat_name])  # 60% base, 40% scaled by win rate
                        details[strat_name]["backtest_win_rate"] = backtest_win_rates[symbol][strat_name]
                    if recent_perf and symbol in recent_perf and strat_name in recent_perf[symbol]:
                        strat_conf *= (0.7 + 0.3 * recent_perf[symbol][strat_name])
                        details[strat_name]["recent_win_rate"] = recent_perf[symbol][strat_name]
                    signals.append((s, strat_conf))
                    details[strat_name]["final_confidence"] = strat_conf

            direction_counts = {"long": 0, "short": 0, "hold": 0}
            conf_by_dir = {"long": [], "short": [], "hold": []}
            for s, adj_conf in signals:
                direction_counts[s] += 1
                conf_by_dir[s].append(adj_conf)
            # Majority vote for direction
            main_signal = max(direction_counts, key=direction_counts.get)
            # Confidence: ensemble = agreement * mean(confidence) * volatility factor
            agreement = direction_counts[main_signal] / len(self.active_strategies) if self.active_strategies else 0
            mean_conf = sum(conf_by_dir[main_signal]) / len(conf_by_dir[main_signal]) if conf_by_dir[main_signal] else 0
            # Volatility penalty: high volatility reduces confidence
            vol_factor = 1.0
            if volatility and symbol in volatility:
                # e.g. scale [0, max_vol] to [1, 0.7]
                max_vol = max(volatility.values()) if volatility.values() else 1.0
                vol = volatility[symbol]
                vol_factor = max(0.7, 1.0 - 0.3 * (vol / max_vol))
            final_confidence = round(agreement * mean_conf * vol_factor, 2)
            results[symbol] = {
                "signal": main_signal,
                "confidence": final_confidence,
                "agreement": agreement,
                "volatility_factor": vol_factor,
                "per_strategy": details
            }
        return results