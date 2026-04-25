from typing import Literal, TypedDict

import pandas as pd

SignalName = Literal["BUY", "SELL", "NEUTRAL"]


class VWAPBandsResult(TypedDict):
    signal: SignalName
    status: str
    value: float | None
    vwap: float | None
    upper_1: float | None
    lower_1: float | None
    upper_2: float | None
    lower_2: float | None
    price_series: list[float]
    vwap_series: list[float]
    upper_1_series: list[float]
    lower_1_series: list[float]
    upper_2_series: list[float]
    lower_2_series: list[float]


def _empty_result() -> VWAPBandsResult:
    return {
        "signal": "NEUTRAL",
        "status": "SEM_VWAP",
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
    }


def calc_vwap_bands(dataframe: pd.DataFrame) -> VWAPBandsResult:
    required_columns = {"high", "low", "close"}
    if dataframe.empty or not required_columns.issubset(dataframe.columns):
        return _empty_result()

    source_frame = dataframe.copy().reset_index(drop=True)
    typical_price = (source_frame["high"] + source_frame["low"] + source_frame["close"]) / 3
    volume = source_frame["tick_volume"] if "tick_volume" in source_frame.columns else pd.Series([1.0] * len(source_frame))
    volume = volume.astype(float).clip(lower=1.0)

    cumulative_volume = volume.cumsum()
    cumulative_tpv = (typical_price * volume).cumsum()
    vwap_series = cumulative_tpv / cumulative_volume

    weighted_variance = (((typical_price - vwap_series) ** 2) * volume).cumsum() / cumulative_volume
    weighted_std = weighted_variance.clip(lower=0.0).pow(0.5)

    source_frame["vwap"] = vwap_series
    source_frame["upper_1"] = vwap_series + weighted_std
    source_frame["lower_1"] = vwap_series - weighted_std
    source_frame["upper_2"] = vwap_series + weighted_std * 2
    source_frame["lower_2"] = vwap_series - weighted_std * 2

    clean_frame = source_frame.tail(24)
    if clean_frame.empty:
        return _empty_result()

    latest = clean_frame.iloc[-1]
    close_value = float(latest["close"])
    vwap_value = float(latest["vwap"])
    upper_1 = float(latest["upper_1"])
    lower_1 = float(latest["lower_1"])
    upper_2 = float(latest["upper_2"])
    lower_2 = float(latest["lower_2"])

    signal: SignalName = "NEUTRAL"
    status = "NO_VWAP"

    if close_value >= upper_2:
        signal = "SELL"
        status = "ACIMA_BANDA_2"
    elif close_value <= lower_2:
        signal = "BUY"
        status = "ABAIXO_BANDA_2"
    elif close_value >= upper_1:
        signal = "SELL"
        status = "ACIMA_BANDA_1"
    elif close_value <= lower_1:
        signal = "BUY"
        status = "ABAIXO_BANDA_1"
    elif close_value > vwap_value:
        signal = "BUY"
        status = "ACIMA_VWAP"
    elif close_value < vwap_value:
        signal = "SELL"
        status = "ABAIXO_VWAP"

    return {
        "signal": signal,
        "status": status,
        "value": close_value,
        "vwap": vwap_value,
        "upper_1": upper_1,
        "lower_1": lower_1,
        "upper_2": upper_2,
        "lower_2": lower_2,
        "price_series": [float(item) for item in clean_frame["close"].tolist()],
        "vwap_series": [float(item) for item in clean_frame["vwap"].tolist()],
        "upper_1_series": [float(item) for item in clean_frame["upper_1"].tolist()],
        "lower_1_series": [float(item) for item in clean_frame["lower_1"].tolist()],
        "upper_2_series": [float(item) for item in clean_frame["upper_2"].tolist()],
        "lower_2_series": [float(item) for item in clean_frame["lower_2"].tolist()],
    }
