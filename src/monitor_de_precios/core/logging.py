"""Configuración de logging con loguru."""

import sys
from pathlib import Path

from loguru import logger as _logger

logger = _logger


def setup_logging(level: str = "INFO") -> None:
    """Configura loguru con salida a stdout y archivo rotativo.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    """
    # Remover handlers por defecto
    logger.remove()

    # Asegurar directorio de logs
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Handler stdout (colorizado)
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Handler archivo rotativo
    logger.add(
        log_dir / "app.log",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
    )
