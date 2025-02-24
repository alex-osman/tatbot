from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

class Log:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def exception(self, message: str | Exception) -> None:
        self.logger.exception(message)
