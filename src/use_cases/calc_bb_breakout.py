from typing import Literal, TypedDict

import pandas as pd
import pandas_ta  # noqa: F401

SignalName = Literal["BUY", "SELL", "NEUTRAL"]


class BBBreakoutResult(TypedDict):
    signal: SignalName
    status: str
    value: float | None
    upper: float | None
    middle: float | None
    lower: float | None
    length: int
    std_dev: int
    price_series: list[float]
    upper_series: list[float]
    middle_series: list[float]
    lower_series: list[float]


def _empty_result(*, length: int, std_dev: int) -> BBBreakoutResult:
    return {
        "signal": "NEUTRAL",
        "status": "INSIDE_BANDS",
        "value": None,
        "upper": None,
        "middle": None,
        "lower": None,
        "length": length,
        "std_dev": std_dev,
        "price_series": [],
        "upper_series": [],
        "middle_series": [],
        "lower_series": [],
    }


def _find_band_column(columns: pd.Index, prefix: str) -> str | None:
    return next((column for column in columns if column.startswith(prefix)), None)


def calc_bb_breakout(
    dataframe: pd.DataFrame,
    *,
    length: int = 20,
    std_dev: int = 3,
) -> BBBreakoutResult:
    if dataframe.empty or "close" not in dataframe:
        return _empty_result(length=length, std_dev=std_dev)

    bb_frame = dataframe.ta.bbands(length=length, std=std_dev)
    if bb_frame is None or bb_frame.dropna().empty:
        return _empty_result(length=length, std_dev=std_dev)

    upper_column = _find_band_column(bb_frame.columns, "BBU_")
    middle_column = _find_band_column(bb_frame.columns, "BBM_")
    lower_column = _find_band_column(bb_frame.columns, "BBL_")
    if upper_column is None or middle_column is None or lower_column is None:
        return _empty_result(length=length, std_dev=std_dev)

    clean_frame = bb_frame.dropna().tail(24)
    close_series = dataframe["close"].tail(len(clean_frame))
    latest = clean_frame.iloc[-1]
    close_value = float(close_series.iloc[-1])
    upper_value = float(latest[upper_column])
    middle_value = float(latest[middle_column])
    lower_value = float(latest[lower_column])
    band_range = max(upper_value - lower_value, 1e-9)
    upper_proximity = abs(upper_value - close_value) / band_range
    lower_proximity = abs(close_value - lower_value) / band_range
    proximity_threshold = 0.18

    signal: SignalName = "NEUTRAL"
    status = "INSIDE_BANDS"

    if close_value <= lower_value:
        signal = "BUY"
        status = "BROKE_LOWER_BAND"
    elif close_value >= upper_value:
        signal = "SELL"
        status = "BROKE_UPPER_BAND"
    elif close_value > middle_value:
        if upper_proximity <= proximity_threshold:
            signal = "SELL"
            status = "ABOVE_MIDDLE_NEAR_UPPER_BAND"
        else:
            signal = "BUY"
            status = "ABOVE_MIDDLE_FAR_FROM_UPPER_BAND"
    elif close_value < middle_value:
        if lower_proximity <= proximity_threshold:
            signal = "BUY"
            status = "BELOW_MIDDLE_NEAR_LOWER_BAND"
        else:
            signal = "SELL"
            status = "BELOW_MIDDLE_FAR_FROM_LOWER_BAND"

    return {
        "signal": signal,
        "status": status,
        "value": close_value,
        "upper": upper_value,
        "middle": middle_value,
        "lower": lower_value,
        "length": length,
        "std_dev": std_dev,
        "price_series": [float(item) for item in close_series.tolist()],
        "upper_series": [float(item) for item in clean_frame[upper_column].tolist()],
        "middle_series": [float(item) for item in clean_frame[middle_column].tolist()],
        "lower_series": [float(item) for item in clean_frame[lower_column].tolist()],
    }
