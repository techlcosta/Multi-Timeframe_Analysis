from collections.abc import Sequence
from typing import cast

import pandas as pd

from src.controllers.symbol_controller import get as get_symbols
from src.models import SymbolModel
from src.MQL import MT5ConnectionSettings, RateRecord, get_rates, mt5
from src.use_cases.calc_adx import calc_adx
from src.use_cases.calc_bb_breakout import calc_bb_breakout
from src.use_cases.calc_macd import calc_macd
from src.use_cases.calc_pivot_point import calc_pivot_point
from src.use_cases.calc_support_resistance import calc_support_resistance
from src.use_cases.calc_vwap_bands import calc_vwap_bands
from src.use_cases.calc_williams_r import calc_williams_r
from src.use_cases.indicator_types import IndicatorConfig, IndicatorsByTimeframe, IndicatorsSnapshot, TimeframeIndicators, TimeframeMap, TimeframeName
from src.use_cases.moving_average_cross import calc_moving_average_cross


def _get_int_param(params: dict[str, int | float], key: str, default: int) -> int:
    return int(params.get(key, default))


def build_indicators_snapshot(
    *,
    timeframes: Sequence[TimeframeName],
    timeframe_map: TimeframeMap,
    indicators: Sequence[IndicatorConfig],
    bars: int = 200,
    settings: MT5ConnectionSettings | None = None,
) -> IndicatorsSnapshot:
    snapshot: IndicatorsSnapshot = {}
    saved_symbols = get_symbols()

    for symbol in saved_symbols:
        snapshot[symbol.name] = _build_symbol_snapshot(
            symbol=symbol,
            timeframes=timeframes,
            timeframe_map=timeframe_map,
            indicators=indicators,
            bars=bars,
            settings=settings,
        )

    return snapshot


def _build_symbol_snapshot(
    *,
    symbol: SymbolModel,
    timeframes: Sequence[TimeframeName],
    timeframe_map: TimeframeMap,
    indicators: Sequence[IndicatorConfig],
    bars: int,
    settings: MT5ConnectionSettings | None,
) -> IndicatorsByTimeframe:
    symbol_snapshot: IndicatorsByTimeframe = {}
    daily_rates = get_rates(
        symbol=symbol.name,
        timeframe=mt5.TIMEFRAME_D1,
        count=10,
        settings=settings,
    )

    for timeframe_name in timeframes:
        timeframe_value = timeframe_map[timeframe_name]
        rates = get_rates(
            symbol=symbol.name,
            timeframe=timeframe_value,
            count=bars,
            settings=settings,
        )
        symbol_snapshot[timeframe_name] = _calculate_timeframe_indicators(
            rates=rates,
            daily_rates=daily_rates,
            indicators=indicators,
        )

    return symbol_snapshot


def _calculate_timeframe_indicators(
    *,
    rates: list[RateRecord],
    daily_rates: list[RateRecord],
    indicators: Sequence[IndicatorConfig],
) -> TimeframeIndicators:
    dataframe = pd.DataFrame(rates)
    if not dataframe.empty:
        dataframe = dataframe.sort_values("time").reset_index(drop=True)
    daily_dataframe = pd.DataFrame(daily_rates)
    if not daily_dataframe.empty:
        daily_dataframe = daily_dataframe.sort_values("time").reset_index(drop=True)

    results: TimeframeIndicators = {
        "bb_breakout": {
            "signal": "NEUTRAL",
            "status": "INSIDE_BANDS",
            "value": None,
            "upper": None,
            "middle": None,
            "lower": None,
            "length": 20,
            "std_dev": 3,
            "price_series": [],
            "upper_series": [],
            "middle_series": [],
            "lower_series": [],
        },
        "support_resistance": {
            "signal": "NEUTRAL",
            "status": "RANGE",
            "support": None,
            "resistance": None,
            "value": None,
            "price_series": [],
        },
        "pivot_point": {
            "signal": "NEUTRAL",
            "status": "AT_PIVOT",
            "value": None,
            "pivot": None,
            "resistance_1": None,
            "support_1": None,
            "resistance_2": None,
            "support_2": None,
            "price_series": [],
        },
        "adx": {
            "value": None,
            "plus_di": None,
            "minus_di": None,
            "length": 14,
            "adx_series": [],
            "plus_di_series": [],
            "minus_di_series": [],
        },
        "macd": {
            "value": None,
            "signal": None,
            "histogram": None,
            "fast": 12,
            "slow": 26,
            "signal_period": 9,
            "macd_series": [],
            "signal_series": [],
            "histogram_series": [],
        },
        "williams_r": {"value": None, "length": 14, "series": []},
        "moving_average_cross": {
            "signal": "NEUTRAL",
            "status": "MIXED",
            "value": None,
            "ema_9": None,
            "ema_21": None,
            "ema_55": None,
            "ema_200": None,
            "price_series": [],
            "ema_9_series": [],
            "ema_21_series": [],
            "ema_55_series": [],
            "ema_200_series": [],
        },
        "vwap_bands": {
            "signal": "NEUTRAL",
            "status": "NO_VWAP",
            "value": None,
            "vwap": None,
            "upper_1": None,
            "lower_1": None,
            "upper_2": None,
            "lower_2": None,
            "price_series": [],
            "vwap_series": [],
            "upper_1_series": [],
            "lower_1_series": [],
            "upper_2_series": [],
            "lower_2_series": [],
        },
    }

    for indicator in indicators:
        name = indicator["name"]
        params = indicator["params"]

        if name == "williams_r":
            results["williams_r"] = calc_williams_r(dataframe, length=_get_int_param(params, "length", 14))
            continue

        if name == "macd":
            results["macd"] = calc_macd(
                dataframe,
                fast=_get_int_param(params, "fast", 12),
                slow=_get_int_param(params, "slow", 26),
                signal=_get_int_param(params, "signal", 9),
            )
            continue

        if name == "adx":
            results["adx"] = calc_adx(dataframe, length=_get_int_param(params, "length", 14))
            continue

        if name == "bb_breakout":
            results["bb_breakout"] = calc_bb_breakout(
                dataframe,
                length=_get_int_param(params, "length", 20),
                std_dev=_get_int_param(params, "std_dev", 3),
            )
            continue

        if name == "support_resistance":
            results["support_resistance"] = calc_support_resistance(dataframe)
            continue

        if name == "pivot_point":
            results["pivot_point"] = calc_pivot_point(dataframe, pivot_source=daily_dataframe)
            continue

        if name == "moving_average_cross":
            results["moving_average_cross"] = calc_moving_average_cross(dataframe)
            continue

        if name == "vwap_bands":
            results["vwap_bands"] = calc_vwap_bands(dataframe)

    return cast(TimeframeIndicators, results)
