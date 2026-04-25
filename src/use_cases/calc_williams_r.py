from typing import TypedDict, cast

import pandas as pd
import pandas_ta  # noqa: F401


class WilliamsRResult(TypedDict):
    value: float | None
    length: int
    series: list[float]


def calc_williams_r(dataframe: pd.DataFrame, *, length: int = 14) -> WilliamsRResult:
    required_columns = {"high", "low", "close"}
    if dataframe.empty or not required_columns.issubset(dataframe.columns):
        return {"value": None, "length": length, "series": []}

    williams_r_series = dataframe.ta.willr(length=length)
    if williams_r_series is None or williams_r_series.dropna().empty:
        return {"value": None, "length": length, "series": []}

    clean_series = williams_r_series.dropna().tail(24)
    value = float(clean_series.iloc[-1])
    return {
        "value": cast(float, value),
        "length": length,
        "series": [float(item) for item in clean_series.tolist()],
    }
