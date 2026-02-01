import json
import logging
from datetime import datetime
from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.json import JSON
from rich.console import Group

console = Console()


class Logger:
    def _log(
        self, level: str, color: str, message: str, data: Optional[Any] = None
    ) -> None:
        table = Table(show_header=False, box=None, padding=(0, 2), expand=True)

        table.add_column(style=f"bold {color}", width=10, justify="left")
        table.add_column(ratio=1)
        table.add_column(style="dim", width=10, justify="right")

        content_renderable = Text(message, style="white")

        if data is not None:
            if isinstance(data, (dict, list)):
                try:
                    json_str = json.dumps(data, default=str, indent=2)
                    json_renderable = JSON(json_str)
                    content_renderable = Group(content_renderable, json_renderable)
                except Exception:
                    content_renderable = Text(
                        f"{message}\n[Não foi possível serializar dados]", style="white"
                    )
            else:
                content_renderable = Text(f"{message} {str(data)}", style="white")

        time_str = datetime.now().strftime("%H:%M:%S")

        table.add_row(level, content_renderable, time_str)
        console.print(table)

    def info(self, message: str, data: Optional[Any] = None):
        self._log("INFO", "blue", message, data)

    def debug(self, message: str, data: Optional[Any] = None):
        self._log("DEBUG", "magenta", message, data)

    def warning(self, message: str, data: Optional[Any] = None):
        self._log("AVISO", "yellow", message, data)

    def error(self, message: str, error: Optional[Any] = None):
        self._log("ERRO", "red", message, error)

    def success(self, message: str, data: Optional[Any] = None):
        self._log("SUCESSO", "green", message, data)


logger = Logger()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                logger.error(msg)
            elif record.levelno >= logging.WARNING:
                logger.warning(msg)
            elif record.levelno >= logging.INFO:
                logger.info(msg)
            else:
                logger.debug(msg)
        except Exception:
            self.handleError(record)


def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        log = logging.getLogger(logger_name)
        log.handlers = [InterceptHandler()]
        log.propagate = False
