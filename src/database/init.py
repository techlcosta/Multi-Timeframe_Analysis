import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

APP_NAME = "FX Strategies"
DATABASE_FILENAME = "fx_strategies.sqlite3"


class Base(DeclarativeBase):
    pass


def get_app_data_directory() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        app_data_dir = Path(appdata)
    else:
        app_data_dir = Path.home() / "AppData" / "Roaming"

    target_dir = app_data_dir / APP_NAME
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def get_database_path() -> Path:
    return get_app_data_directory() / DATABASE_FILENAME


def get_database_url() -> str:
    return f"sqlite:///{get_database_path().as_posix()}"


engine = create_engine(get_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_database() -> None:
    # Lazy import avoids circular imports with models that depend on Base.
    from src.models.symbol_model import SymbolModel  # noqa: F401

    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
