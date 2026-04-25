import argparse
import atexit
import logging
import sys

import webview

from src.config import add_settings_cli_arguments, load_settings
from src.database import init_database
from src.MQL import initialize
from src.runtime import SingleInstanceManager
from src.services.api import api

logger = logging.getLogger(__name__)


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


def main() -> None:
    configure_stdio()
    configure_logging()
    instance_manager: SingleInstanceManager | None = None

    try:
        args = parse_args()
        settings = load_settings(args)
        dev_mode = settings.frontend.mode == "dev"

        if sys.platform.startswith("win") and not dev_mode:
            instance_manager = SingleInstanceManager(
                app_id="FXStrategies",
                window_title=settings.window.title,
            )

            if not instance_manager.acquire_or_activate_existing():
                raise SystemExit(0)

            instance_manager.start_listener()
            atexit.register(instance_manager.release)

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
