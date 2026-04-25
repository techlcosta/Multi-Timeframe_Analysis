import argparse
import atexit
import ctypes
import logging
import sys

import webview

from src.config import add_settings_cli_arguments, load_settings
from src.database import init_database
from src.MQL import initialize
from src.services.api import api

logger = logging.getLogger(__name__)

_ERROR_ALREADY_EXISTS = 183
_mutex_handle: int | None = None


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def configure_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FX Strategies (pywebview)")
    add_settings_cli_arguments(parser)
    return parser.parse_args()


def acquire_single_instance_lock(app_id: str) -> bool:
    global _mutex_handle

    if not sys.platform.startswith("win"):
        return True

    kernel32 = ctypes.windll.kernel32
    mutex_name = f"Local\\{app_id}"
    handle = kernel32.CreateMutexW(None, False, mutex_name)

    if not handle:
        raise OSError("Nao foi possivel criar o mutex de instancia unica.")

    last_error = kernel32.GetLastError()
    if last_error == _ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return False

    _mutex_handle = int(handle)
    return True


def release_single_instance_lock() -> None:
    global _mutex_handle

    if not _mutex_handle or not sys.platform.startswith("win"):
        return

    ctypes.windll.kernel32.CloseHandle(_mutex_handle)
    _mutex_handle = None


def main() -> None:
    configure_stdio()
    configure_logging()

    try:
        args = parse_args()
        settings = load_settings(args)
        dev_mode = settings.frontend.mode == "dev"
        app_id = "FXStrategies.SingleInstance"

        if not acquire_single_instance_lock(app_id):
            logger.warning("Aplicacao ja esta em execucao. Nova instancia sera encerrada.")
            raise SystemExit(0)

        atexit.register(release_single_instance_lock)

        init_database()
        logger.info("Inicializando FX Strategies (mode=%s)", settings.frontend.mode)

        initialize.initialize_mt5()

        webview.create_window(
            title=settings.window.title,
            url=settings.frontend.entry_url,
            width=settings.window.width,
            height=settings.window.height,
            min_size=(settings.window.min_width, settings.window.min_height),
            js_api=api,
        )

        logger.info("Iniciando pywebview (http_server=%s)", not dev_mode)
        webview.start(debug=dev_mode, http_server=not dev_mode)
    except KeyboardInterrupt:
        return
    except FileNotFoundError as exc:
        logger.error("Arquivo obrigatorio nao encontrado: %s", exc)
        raise SystemExit(1) from exc
    except Exception as err:
        logger.exception("Erro ao iniciar a aplicacao.")
        raise SystemExit(1) from err


if __name__ == "__main__":
    main()
