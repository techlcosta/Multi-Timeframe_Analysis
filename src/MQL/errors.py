from src.MQL.codes import MT5Code
from src.MQL.mt5_types import MT5Error


class MetaTrader5Error(RuntimeError):
    """Base error carrying a stable code for frontend i18n."""

    def __init__(self, code: MT5Code, *, mt5_error: MT5Error | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.mt5_error = mt5_error


class MetaTrader5ConnectionError(MetaTrader5Error):
    """Raised when a MetaTrader 5 operation cannot be completed."""


class MetaTrader5ConfigurationError(MetaTrader5Error):
    """Raised when the MetaTrader 5 configuration is invalid."""
