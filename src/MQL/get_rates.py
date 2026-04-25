from typing import Any, cast

import pandas as pd

from src.MQL.codes import MT5_RATES_GET_FAILED
from src.MQL.errors import MetaTrader5ConnectionError
from src.MQL.initialize import MT5ConnectionSettings, managed_mt5_connection
from src.MQL.mt5_types import MT5TimeframeValue, RateRecord, mt5


def get_rates(symbol: str, timeframe: MT5TimeframeValue, count: int = 200, start_pos: int = 0, settings: MT5ConnectionSettings | None = None) -> list[RateRecord]:
    with managed_mt5_connection(settings):
        raw_rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
        if raw_rates is None or isinstance(raw_rates, bool):
            raise MetaTrader5ConnectionError(
                MT5_RATES_GET_FAILED,
                mt5_error=mt5.last_error(),
            )

        frame = pd.DataFrame(cast(Any, raw_rates))
        if frame.empty:
            return []

        return cast(list[RateRecord], frame.to_dict(orient="records"))
