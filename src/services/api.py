import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from src.controllers import delete as delete_symbol
from src.controllers import get as get_saved_symbols
from src.controllers import get_indicators
from src.controllers import save as save_symbol
from src.models.symbol_model import SymbolModel, SymbolStableInfo
from src.MQL import MT5_SYMBOLS_GET_OK, MT5ConnectionSettings, MetaTrader5Error, SymbolRecord, get_symbols

T = TypeVar("T")

SYMBOLS_GET_OK = "SYMBOLS_GET_OK"
SYMBOL_SAVE_OK = "SYMBOL_SAVE_OK"
SYMBOL_DELETE_OK = "SYMBOL_DELETE_OK"
SYMBOL_DELETE_NOT_FOUND = "SYMBOL_DELETE_NOT_FOUND"
INDICATORS_GET_OK = "INDICATORS_GET_OK"
INTERNAL_ERROR = "INTERNAL_ERROR"

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class APIError:
    message: str
    mt5_error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"message": self.message, "mt5_error": self.mt5_error}


@dataclass(frozen=True, slots=True)
class APIResponse(Generic[T]):
    code: str
    data: T | None
    ok: bool = True
    error: APIError | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "data": self.data,
            "error": self.error.to_dict() if self.error else None,
        }


class API:
    _instance: ClassVar["API | None"] = None

    def __new__(cls) -> "API":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def mt_symbols(self, group: str | None = None, settings: MT5ConnectionSettings | None = None) -> dict[str, Any]:
        return self._run(
            lambda: get_symbols(group=group, settings=settings),
            success_code=MT5_SYMBOLS_GET_OK,
        )

    def fech_symbols(self) -> dict[str, Any]:
        return self._run(
            lambda: [_serialize_symbol(symbol) for symbol in get_saved_symbols()],
            success_code=SYMBOLS_GET_OK,
        )

    def add_symbol(self, symbol_data: SymbolStableInfo | SymbolRecord) -> dict[str, Any]:
        return self._run(
            lambda: _serialize_symbol(save_symbol(symbol_data)),
            success_code=SYMBOL_SAVE_OK,
        )

    def remove_symbol(self, symbol: str) -> dict[str, Any]:
        return self._run(
            lambda: delete_symbol(symbol),
            success_code=SYMBOL_DELETE_OK,
            empty_code=SYMBOL_DELETE_NOT_FOUND,
        )

    def indicators(
        self,
        bars: int = 200,
        settings: MT5ConnectionSettings | None = None,
    ) -> dict[str, Any]:
        return self._run(
            lambda: get_indicators(bars=bars, settings=settings),
            success_code=INDICATORS_GET_OK,
        )

    def _run(
        self,
        action: Callable[[], T],
        *,
        success_code: str,
        empty_code: str | None = None,
    ) -> dict[str, Any]:
        try:
            data = action()
        except MetaTrader5Error as exc:
            logger.warning("API call failed with MT5 error %s", exc.code, exc_info=True)
            return APIResponse(
                code=exc.code,
                data=None,
                ok=False,
                error=APIError(
                    message=exc.code,
                    mt5_error=_serialize_mt5_error(exc.mt5_error),
                ),
            ).to_dict()
        except Exception as exc:
            logger.exception("Unexpected API error")
            return APIResponse(
                code=INTERNAL_ERROR,
                data=None,
                ok=False,
                error=APIError(message=str(exc) or INTERNAL_ERROR),
            ).to_dict()

        code = empty_code if data is False and empty_code is not None else success_code
        return APIResponse(code=code, data=data).to_dict()


api = API()


def _serialize_symbol(symbol: SymbolModel) -> dict[str, Any]:
    return {
        "name": symbol.name,
        "path": symbol.path,
        "description": symbol.description,
        "currency_base": symbol.currency_base,
        "currency_profit": symbol.currency_profit,
        "created_at": symbol.created_at.isoformat() if symbol.created_at else None,
        "updated_at": symbol.updated_at.isoformat() if symbol.updated_at else None,
    }


def _serialize_mt5_error(mt5_error: tuple[int, str] | None) -> dict[str, Any] | None:
    if mt5_error is None:
        return None

    code, message = mt5_error
    return {"code": code, "message": message}


__all__ = ["API", "APIError", "APIResponse", "api"]
