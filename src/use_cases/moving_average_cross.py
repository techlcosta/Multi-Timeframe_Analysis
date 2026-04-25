from typing import Literal, TypedDict

import pandas as pd
import pandas_ta  # noqa: F401

SignalName = Literal["BUY", "SELL", "NEUTRAL"]


class MovingAverageCrossResult(TypedDict):
    signal: SignalName
    status: str
    value: float | None
    ema_9: float | None
    ema_21: float | None
    ema_55: float | None
    ema_200: float | None
    price_series: list[float]
    ema_9_series: list[float]
    ema_21_series: list[float]
    ema_55_series: list[float]
    ema_200_series: list[float]


def _empty_result() -> MovingAverageCrossResult:
    return {
        "signal": "NEUTRAL",
        "status": "MISTO",
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
    }


def calc_moving_average_cross(dataframe: pd.DataFrame) -> MovingAverageCrossResult:
    if dataframe.empty or "close" not in dataframe:
        return _empty_result()

    source_frame = dataframe.copy()
    close_series = source_frame["close"].astype(float)
    # Use pandas ewm directly so every bar has an EMA value and the mini chart
    # can render a proportional history even for long periods like EMA 200.
    source_frame["ema_9"] = close_series.ewm(span=9, adjust=False, min_periods=1).mean()
    source_frame["ema_21"] = close_series.ewm(span=21, adjust=False, min_periods=1).mean()
    source_frame["ema_55"] = close_series.ewm(span=55, adjust=False, min_periods=1).mean()
    source_frame["ema_200"] = close_series.ewm(span=200, adjust=False, min_periods=1).mean()

    clean_frame = source_frame.tail(24)
    if clean_frame.empty:
        return _empty_result()

    latest = clean_frame.iloc[-1]
    close_value = float(latest["close"])
    ema_9 = float(latest["ema_9"])
    ema_21 = float(latest["ema_21"])
    ema_55 = float(latest["ema_55"])
    ema_200 = float(latest["ema_200"])

    bullish_stack = close_value >= ema_9 > ema_21 > ema_55 > ema_200
    bearish_stack = close_value <= ema_9 < ema_21 < ema_55 < ema_200

    signal: SignalName = "NEUTRAL"
    status = "MISTO"

    if bullish_stack:
        signal = "BUY"
        status = "ALINHADO_PARA_COMPRA"
    elif bearish_stack:
        signal = "SELL"
        status = "ALINHADO_PARA_VENDA"

    return {
        "signal": signal,
        "status": status,
        "value": close_value,
        "ema_9": ema_9,
        "ema_21": ema_21,
        "ema_55": ema_55,
        "ema_200": ema_200,
        "price_series": [float(item) for item in clean_frame["close"].tolist()],
        "ema_9_series": [float(item) for item in clean_frame["ema_9"].tolist()],
        "ema_21_series": [float(item) for item in clean_frame["ema_21"].tolist()],
        "ema_55_series": [float(item) for item in clean_frame["ema_55"].tolist()],
        "ema_200_series": [float(item) for item in clean_frame["ema_200"].tolist()],
    }
