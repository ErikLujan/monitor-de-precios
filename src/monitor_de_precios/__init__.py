"""Paquete principal de la aplicación monitor-de-precios."""

__version__ = "0.1.0"

from .core.config import get_settings, load_products
from .core.logging import setup_logging
from .models.product import (
    PriceVariation,
    ProductConfig,
    ProductFieldConfig,
    ScrapedPrice,
)
from .services.analyzer import calcular_variacion, es_cambio_significativo
from .services.database import get_price_history, get_recent_prices, init_db, insert_price
from .services.notifier import alerta_precio_cambio, enviar_alerta_telegram, enviar_webhook
from .services.scheduler import add_product_jobs, create_scheduler, start_scheduler
from .services.scraper import scrape_product

__all__ = [
    "__version__",
    "get_settings",
    "load_products",
    "setup_logging",
    "ProductFieldConfig",
    "ProductConfig",
    "ScrapedPrice",
    "PriceVariation",
    "init_db",
    "insert_price",
    "get_recent_prices",
    "get_price_history",
    "scrape_product",
    "calcular_variacion",
    "es_cambio_significativo",
    "enviar_alerta_telegram",
    "enviar_webhook",
    "alerta_precio_cambio",
    "create_scheduler",
    "add_product_jobs",
    "start_scheduler",
]
