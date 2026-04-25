import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from src.MQL.codes import MT5_INITIALIZE_FAILED, MT5_LOGIN_ENV_INVALID
from src.MQL.errors import MetaTrader5ConfigurationError, MetaTrader5ConnectionError
from src.MQL.mt5_types import mt5

ENV_PREFIX = "FX_STRATEGIES_MT5"
ENV_PATH_KEY = f"{ENV_PREFIX}_PATH"
ENV_LOGIN_KEY = f"{ENV_PREFIX}_LOGIN"
ENV_PASSWORD_KEY = f"{ENV_PREFIX}_PASSWORD"
ENV_SERVER_KEY = f"{ENV_PREFIX}_SERVER"


@dataclass(frozen=True, slots=True)
class MT5ConnectionSettings:
    path: str | None = None
    login: int | None = None
    password: str | None = None
    server: str | None = None


def load_mt5_connection_settings() -> MT5ConnectionSettings:
    return MT5ConnectionSettings(path=_read_env(ENV_PATH_KEY), login=_read_env_int(ENV_LOGIN_KEY), password=_read_env(ENV_PASSWORD_KEY), server=_read_env(ENV_SERVER_KEY))


def initialize_mt5(settings: MT5ConnectionSettings | None = None) -> None:
    connection_settings = settings or load_mt5_connection_settings()

    kwargs = {
        key: value
        for key, value in {"path": connection_settings.path, "login": connection_settings.login, "password": connection_settings.password, "server": connection_settings.server}.items()
        if value is not None
    }

    if mt5.initialize(**kwargs):
        return

    raise MetaTrader5ConnectionError(MT5_INITIALIZE_FAILED, mt5_error=mt5.last_error())


def shutdown_mt5() -> None:
    mt5.shutdown()


@contextmanager
def managed_mt5_connection(settings: MT5ConnectionSettings | None = None) -> Iterator[None]:
    initialize_mt5(settings)
    try:
        yield
    finally:
        shutdown_mt5()


def _read_env(key: str) -> str | None:
    value = os.environ.get(key)
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


def _read_env_int(key: str) -> int | None:
    value = _read_env(key)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise MetaTrader5ConfigurationError(MT5_LOGIN_ENV_INVALID) from exc
