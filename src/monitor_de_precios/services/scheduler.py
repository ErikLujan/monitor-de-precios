"""Scheduler con APScheduler para jobs periódicos de scraping."""

import signal
import sys
import time
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from monitor_de_precios.core.config import get_settings, load_products
from monitor_de_precios.core.logging import logger, setup_logging
from monitor_de_precios.models.product import ProductConfig
from monitor_de_precios.services.analyzer import calcular_variacion, es_cambio_significativo
from monitor_de_precios.services.database import get_last_price, insert_price
from monitor_de_precios.services.notifier import alerta_precio_cambio
from monitor_de_precios.services.scraper import scrape_product

_scheduler: BackgroundScheduler | None = None


def create_scheduler() -> BackgroundScheduler:
    """Crea y configura el BackgroundScheduler."""
    global _scheduler
    _scheduler = BackgroundScheduler(timezone="UTC")
    return _scheduler


def _scrape_job(product: ProductConfig) -> None:
    """Job que scrapea un producto y procesa alertas."""
    logger.info(f"[Job] Ejecutando scrape para: {product.nombre}")

    try:
        scraped = scrape_product(product)

        last = get_last_price(scraped.producto, scraped.tienda)
        if last:
            variacion = calcular_variacion(
                precio_anterior=last["precio"],
                precio_actual=scraped.precio,
                producto=scraped.producto,
                tienda=scraped.tienda,
            )

            if es_cambio_significativo(
                variacion,
                umbral_porcentaje=product.umbral_cambio_porcentaje,
                umbral_precio_maximo=product.umbral_precio_maximo,
            ):
                logger.info(f"[Job] Cambio significativo detectado: {variacion.porcentaje:+.2f}%")
                alerta_precio_cambio(variacion, url=scraped.url)

        insert_price(scraped)
        logger.info(f"[Job] Precio guardado: ${scraped.precio:,.2f} ARS")

    except Exception as e:
        logger.error(f"[Job] Error scrapeando {product.nombre}: {e}")


def add_product_jobs(scheduler: BackgroundScheduler, products: list[ProductConfig]) -> int:
    """Agrega jobs al scheduler para cada producto activo.

    Args:
        scheduler: Instancia de BackgroundScheduler
        products: Lista de productos configurados

    Returns:
        Número de jobs agregados
    """
    count = 0
    for product in products:
        if not product.activo:
            logger.info(f"[Scheduler] Producto pausado (activo=false): {product.id}")
            continue

        job_id = product.id
        trigger = IntervalTrigger(hours=product.frecuencia_horas)

        scheduler.add_job(
            _scrape_job,
            trigger=trigger,
            args=[product],
            id=job_id,
            name=f"Scrape: {product.nombre}",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        count += 1
        logger.info(
            f"[Scheduler] Job agregado: {product.nombre} cada {product.frecuencia_horas}h (id={job_id})"
        )

    return count


def start_scheduler() -> None:
    """Inicia el scheduler y bloquea hasta señal de terminación."""
    settings = get_settings()
    setup_logging(settings.log_level)

    from pathlib import Path

    products = load_products(Path("products.yaml"))

    if not products:
        logger.warning("No hay productos configurados. Saliendo.")
        return

    active_products = [p for p in products if p.activo]
    if not active_products:
        logger.warning("No hay productos activos. Saliendo.")
        return

    scheduler = create_scheduler()
    add_product_jobs(scheduler, products)

    def shutdown(signum: int, _frame: Any) -> None:
        logger.info(f"Señal {signum} recibida, deteniendo scheduler...")
        scheduler.shutdown(wait=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Iniciando scheduler...")
    scheduler.start()

    try:
        signal.pause()
    except AttributeError:
        while True:
            time.sleep(1)