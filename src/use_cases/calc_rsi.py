from typing import TypedDict, cast

import pandas as pd
import pandas_ta  # noqa: F401


class RSIResult(TypedDict):
    value: float | None
    length: int
    series: list[float]


def calc_rsi(dataframe: pd.DataFrame, *, length: int = 14) -> RSIResult:
    if dataframe.empty or "close" not in dataframe:
        return {"value": None, "length": length, "series": []}

    rsi_series = dataframe.ta.rsi(length=length)
    if rsi_series is None or rsi_series.dropna().empty:
        return {"value": None, "length": length, "series": []}

    clean_series = rsi_series.dropna().tail(24)
    value = float(clean_series.iloc[-1])
    return {
        "value": cast(float, value),
        "length": length,
        "series": [float(item) for item in clean_series.tolist()],
    }
