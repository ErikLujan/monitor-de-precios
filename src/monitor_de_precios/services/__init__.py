"""Paquete de servicios de monitor-de-precios."""

from .analyzer import calcular_variacion, es_cambio_significativo
from .database import get_price_history, get_recent_prices, init_db, insert_price
from .notifier import alerta_precio_cambio, enviar_alerta_telegram, enviar_webhook
from .scheduler import add_product_jobs, create_scheduler, start_scheduler
from .scraper import scrape_product

__all__ = [
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
