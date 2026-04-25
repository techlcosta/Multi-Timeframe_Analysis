from __future__ import annotations

from datetime import datetime
from typing import ClassVar, TypedDict

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class SymbolStableInfo(TypedDict, total=False):
    name: str
    path: str
    description: str
    currency_base: str
    currency_profit: str


class SymbolModel(Base):
    __tablename__ = "symbols"

    # Keep only the most important stable fields from mt5.symbol_info()._asdict().
    STABLE_FIELDS: ClassVar[tuple[str, ...]] = (
        "name",
        "path",
        "description",
        "currency_base",
        "currency_profit",
    )

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    path: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(String(255), default="")
    currency_base: Mapped[str] = mapped_column(String(32), default="")
    currency_profit: Mapped[str] = mapped_column(String(32), default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
