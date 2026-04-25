from collections.abc import Mapping
from typing import Any

from src.database import get_session
from src.models import SymbolModel, SymbolStableInfo

SYMBOL_NAME_REQUIRED = "SYMBOL_NAME_REQUIRED"


def get() -> list[SymbolModel]:
    with get_session() as session:
        return session.query(SymbolModel).order_by(SymbolModel.name.asc()).all()


def save(symbol_data: Mapping[str, Any]) -> SymbolModel:
    symbol_name = symbol_data.get("name")
    if not isinstance(symbol_name, str) or not symbol_name.strip():
        raise ValueError(SYMBOL_NAME_REQUIRED)

    payload = _filter_symbol_data(symbol_data)

    with get_session() as session:
        symbol = session.get(SymbolModel, symbol_name)
        if symbol is None:
            symbol = SymbolModel(name=symbol_name)

        for field_name, field_value in payload.items():
            setattr(symbol, field_name, field_value)

        session.add(symbol)
        session.commit()
        session.refresh(symbol)
        return symbol


def delete(symbol_name: str) -> bool:
    with get_session() as session:
        symbol = session.get(SymbolModel, symbol_name)
        if symbol is None:
            return False

        session.delete(symbol)
        session.commit()
        return True


def _filter_symbol_data(symbol_data: Mapping[str, Any]) -> SymbolStableInfo:
    filtered_data: SymbolStableInfo = {}
    for field_name in SymbolModel.STABLE_FIELDS:
        if field_name in symbol_data:
            filtered_data[field_name] = symbol_data[field_name]
    return filtered_data
