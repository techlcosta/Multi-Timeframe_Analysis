from collections.abc import Mapping
from typing import Literal, TypeAlias, TypedDict

from src.MQL import MT5TimeframeValue
from src.use_cases.calc_adx import ADXResult
from src.use_cases.calc_bb_breakout import BBBreakoutResult
from src.use_cases.calc_macd import MACDResult
from src.use_cases.calc_pivot_point import PivotPointResult
from src.use_cases.calc_support_resistance import SupportResistanceResult
from src.use_cases.calc_vwap_bands import VWAPBandsResult
from src.use_cases.calc_williams_r import WilliamsRResult
from src.use_cases.moving_average_cross import MovingAverageCrossResult

TimeframeName = Literal["M1", "M5", "M15", "M30"]
IndicatorName = Literal["williams_r", "macd", "adx", "bb_breakout", "support_resistance", "pivot_point", "moving_average_cross", "vwap_bands"]


class IndicatorConfig(TypedDict):
    name: IndicatorName
    params: dict[str, int | float]


class TimeframeIndicators(TypedDict):
    williams_r: WilliamsRResult
    macd: MACDResult
    adx: ADXResult
    bb_breakout: BBBreakoutResult
    support_resistance: SupportResistanceResult
    pivot_point: PivotPointResult
    moving_average_cross: MovingAverageCrossResult
    vwap_bands: VWAPBandsResult


IndicatorsByTimeframe: TypeAlias = dict[TimeframeName, TimeframeIndicators]
IndicatorsSnapshot: TypeAlias = dict[str, IndicatorsByTimeframe]
TimeframeMap: TypeAlias = Mapping[TimeframeName, MT5TimeframeValue]


class IndicatorsControllerResponse(TypedDict):
    timeframes: list[TimeframeName]
    indicators: list[IndicatorConfig]
    symbols: IndicatorsSnapshot
