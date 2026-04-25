from typing import TypedDict

import pandas as pd
import pandas_ta  # noqa: F401


class MACDResult(TypedDict):
    value: float | None
    signal: float | None
    histogram: float | None
    fast: int
    slow: int
    signal_period: int
    macd_series: list[float]
    signal_series: list[float]
    histogram_series: list[float]


def calc_macd(
    dataframe: pd.DataFrame,
    *,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult:
    if dataframe.empty or "close" not in dataframe:
        return {
            "value": None,
            "signal": None,
            "histogram": None,
            "fast": fast,
            "slow": slow,
            "signal_period": signal,
            "macd_series": [],
            "signal_series": [],
            "histogram_series": [],
        }

    macd_frame = dataframe.ta.macd(fast=fast, slow=slow, signal=signal)
    if macd_frame is None or macd_frame.dropna().empty:
        return {
            "value": None,
            "signal": None,
            "histogram": None,
            "fast": fast,
            "slow": slow,
            "signal_period": signal,
            "macd_series": [],
            "signal_series": [],
            "histogram_series": [],
        }

    clean_frame = macd_frame.dropna().tail(24)
    latest = clean_frame.iloc[-1]
    return {
        "value": float(latest[f"MACD_{fast}_{slow}_{signal}"]),
        "signal": float(latest[f"MACDs_{fast}_{slow}_{signal}"]),
        "histogram": float(latest[f"MACDh_{fast}_{slow}_{signal}"]),
        "fast": fast,
        "slow": slow,
        "signal_period": signal,
        "macd_series": [float(item) for item in clean_frame[f"MACD_{fast}_{slow}_{signal}"].tolist()],
        "signal_series": [float(item) for item in clean_frame[f"MACDs_{fast}_{slow}_{signal}"].tolist()],
        "histogram_series": [float(item) for item in clean_frame[f"MACDh_{fast}_{slow}_{signal}"].tolist()],
    }
