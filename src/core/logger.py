import logging

from core.settings import settings


def setup_logger():
    logging.basicConfig(
        level=settings.logs.level,
        format=settings.logs.format,
    )
