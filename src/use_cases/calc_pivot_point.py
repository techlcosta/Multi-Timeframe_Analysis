from typing import Literal, TypedDict

import pandas as pd

SignalName = Literal["BUY", "SELL", "NEUTRAL"]


class PivotPointResult(TypedDict):
    signal: SignalName
    status: str
    value: float | None
    pivot: float | None
    resistance_1: float | None
    support_1: float | None
    resistance_2: float | None
    support_2: float | None
    price_series: list[float]


def calc_pivot_point(dataframe: pd.DataFrame, *, pivot_source: pd.DataFrame | None = None) -> PivotPointResult:
    required_columns = {"high", "low", "close"}
    if dataframe.empty or not required_columns.issubset(dataframe.columns):
        return {
            "signal": "NEUTRAL",
            "status": "AT_PIVOT",
            "value": None,
            "pivot": None,
            "resistance_1": None,
            "support_1": None,
            "resistance_2": None,
            "support_2": None,
            "price_series": [],
        }

    intraday_frame = dataframe.tail(48).reset_index(drop=True)
    latest_close = float(intraday_frame["close"].iloc[-1])
    pivot_frame = pivot_source if pivot_source is not None else dataframe
    if pivot_frame.empty or not required_columns.issubset(pivot_frame.columns):
        return {
            "signal": "NEUTRAL",
            "status": "AT_PIVOT",
            "value": latest_close,
            "pivot": None,
            "resistance_1": None,
            "support_1": None,
            "resistance_2": None,
            "support_2": None,
            "price_series": [float(item) for item in intraday_frame["close"].tail(24).tolist()],
        }

    reference_frame = pivot_frame.sort_values("time").reset_index(drop=True)
    reference_bar = reference_frame.iloc[-2] if len(reference_frame) >= 2 else reference_frame.iloc[-1]
    high = float(reference_bar["high"])
    low = float(reference_bar["low"])
    close = float(reference_bar["close"])

    pivot = (high + low + close) / 3
    resistance_1 = 2 * pivot - low
    support_1 = 2 * pivot - high
    range_value = high - low
    resistance_2 = pivot + range_value
    support_2 = pivot - range_value

    signal: SignalName = "NEUTRAL"
    status = "AT_PIVOT"
    tolerance = max(range_value * 0.05, 1e-9)

    if latest_close > pivot + tolerance:
        signal = "BUY"
        status = "ABOVE_PIVOT"
    elif latest_close < pivot - tolerance:
        signal = "SELL"
        status = "BELOW_PIVOT"

    return {
        "signal": signal,
        "status": status,
        "value": latest_close,
        "pivot": pivot,
        "resistance_1": resistance_1,
        "support_1": support_1,
        "resistance_2": resistance_2,
        "support_2": support_2,
        "price_series": [float(item) for item in intraday_frame["close"].tail(24).tolist()],
    }
