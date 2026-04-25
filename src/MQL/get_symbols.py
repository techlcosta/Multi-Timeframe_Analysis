from src.MQL.codes import MT5_SYMBOLS_GET_FAILED
from src.MQL.errors import MetaTrader5ConnectionError
from src.MQL.initialize import MT5ConnectionSettings, managed_mt5_connection
from src.MQL.mt5_types import SupportsAsDict, SymbolRecord, mt5


def get_symbols(group: str | None = None, settings: MT5ConnectionSettings | None = None) -> list[SymbolRecord]:
    with managed_mt5_connection(settings):
        raw_symbols = mt5.symbols_get(group) if group else mt5.symbols_get()
        if raw_symbols is None or isinstance(raw_symbols, bool):
            raise MetaTrader5ConnectionError(MT5_SYMBOLS_GET_FAILED, mt5_error=mt5.last_error())

        return [_symbol_to_dict(symbol) for symbol in raw_symbols]


def _symbol_to_dict(symbol: SupportsAsDict) -> SymbolRecord:
    return dict(symbol._asdict())
