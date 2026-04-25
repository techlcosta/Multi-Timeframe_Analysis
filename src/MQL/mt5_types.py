from typing import Protocol, TypeAlias, cast

import MetaTrader5 as _mt5

MT5Error: TypeAlias = tuple[int, str]
SymbolRecord: TypeAlias = dict[str, object]
RateRecord: TypeAlias = dict[str, object]
MT5TimeframeValue: TypeAlias = int


class SupportsAsDict(Protocol):
    def _asdict(self) -> dict[str, object]: ...


class MetaTrader5Module(Protocol):
    TIMEFRAME_M1: MT5TimeframeValue
    TIMEFRAME_M5: MT5TimeframeValue
    TIMEFRAME_M15: MT5TimeframeValue
    TIMEFRAME_M30: MT5TimeframeValue
    TIMEFRAME_D1: MT5TimeframeValue

    def initialize(
        self,
        path: str | None = None,
        *,
        login: int | None = None,
        password: str | None = None,
        server: str | None = None,
    ) -> bool: ...

    def shutdown(self) -> None: ...

    def last_error(self) -> MT5Error: ...

    def symbols_get(self, group: str | None = None) -> tuple[SupportsAsDict, ...] | None: ...

    def copy_rates_from_pos(
        self,
        symbol: str,
        timeframe: MT5TimeframeValue,
        start_pos: int,
        count: int,
    ) -> object: ...


mt5 = cast(MetaTrader5Module, _mt5)
