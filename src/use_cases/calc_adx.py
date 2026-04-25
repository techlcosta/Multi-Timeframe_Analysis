from typing import TypedDict

import pandas as pd
import pandas_ta  # noqa: F401


class ADXResult(TypedDict):
    value: float | None
    plus_di: float | None
    minus_di: float | None
    length: int
    adx_series: list[float]
    plus_di_series: list[float]
    minus_di_series: list[float]


def calc_adx(dataframe: pd.DataFrame, *, length: int = 14) -> ADXResult:
    required_columns = {"high", "low", "close"}
    if dataframe.empty or not required_columns.issubset(dataframe.columns):
        return {
            "value": None,
            "plus_di": None,
            "minus_di": None,
            "length": length,
            "adx_series": [],
            "plus_di_series": [],
            "minus_di_series": [],
        }

    adx_frame = dataframe.ta.adx(length=length)
    if adx_frame is None or adx_frame.dropna().empty:
        return {
            "value": None,
            "plus_di": None,
            "minus_di": None,
            "length": length,
            "adx_series": [],
            "plus_di_series": [],
            "minus_di_series": [],
        }

    clean_frame = adx_frame.dropna().tail(24)
    latest = clean_frame.iloc[-1]
    return {
        "value": float(latest[f"ADX_{length}"]),
        "plus_di": float(latest[f"DMP_{length}"]),
        "minus_di": float(latest[f"DMN_{length}"]),
        "length": length,
        "adx_series": [float(item) for item in clean_frame[f"ADX_{length}"].tolist()],
        "plus_di_series": [float(item) for item in clean_frame[f"DMP_{length}"].tolist()],
        "minus_di_series": [float(item) for item in clean_frame[f"DMN_{length}"].tolist()],
    }
