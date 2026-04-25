from typing import Any, Protocol, overload

__version__: str
__author__: str
TIMEFRAME_M1: int
TIMEFRAME_M5: int
TIMEFRAME_M15: int
TIMEFRAME_M30: int


class _SupportsAsDict(Protocol):
    def _asdict(self) -> dict[str, Any]: ...


def initialize(
    path: str | None = None,
    *,
    login: int | None = None,
    password: str | None = None,
    server: str | None = None,
) -> bool: ...


def shutdown() -> None: ...


def last_error() -> tuple[int, str]: ...


@overload
def symbols_get(group: str) -> tuple[_SupportsAsDict, ...] | None: ...
@overload
def symbols_get() -> tuple[_SupportsAsDict, ...] | None: ...


def copy_rates_from_pos(
    symbol: str,
    timeframe: int,
    start_pos: int,
    count: int,
) -> Any: ...
