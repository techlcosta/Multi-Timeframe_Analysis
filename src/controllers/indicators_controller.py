from src.MQL import MT5ConnectionSettings, mt5
from src.use_cases.indicator_types import IndicatorConfig, IndicatorsControllerResponse, TimeframeMap, TimeframeName
from src.use_cases.indicators import build_indicators_snapshot

MT5_TIMEFRAMES: list[TimeframeName] = ["M1", "M5", "M15", "M30"]
TIMEFRAME_MAP: TimeframeMap = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
}
INDICATORS: list[IndicatorConfig] = [
    {"name": "adx", "params": {"length": 14}},
    {"name": "moving_average_cross", "params": {}},
    {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
    {"name": "support_resistance", "params": {}},
    {"name": "williams_r", "params": {"length": 14}},
    {"name": "vwap_bands", "params": {}},
    {"name": "bb_breakout", "params": {"length": 20, "std_dev": 3}},
    {"name": "pivot_point", "params": {}},
]


def get(
    *,
    bars: int = 200,
    settings: MT5ConnectionSettings | None = None,
) -> IndicatorsControllerResponse:
    symbols = build_indicators_snapshot(
        timeframes=MT5_TIMEFRAMES,
        timeframe_map=TIMEFRAME_MAP,
        indicators=INDICATORS,
        bars=bars,
        settings=settings,
    )
    return {
        "timeframes": MT5_TIMEFRAMES,
        "indicators": INDICATORS,
        "symbols": symbols,
    }
