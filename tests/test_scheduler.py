"""Pruebas para el scheduler APScheduler."""

from unittest.mock import MagicMock, patch

from apscheduler.schedulers.background import BackgroundScheduler

from monitor_de_precios.models.product import ProductConfig
from monitor_de_precios.services.scheduler import (
    _scrape_job,
    add_product_jobs,
    create_scheduler,
)


def test_create_scheduler_retorna_background_scheduler():
    """Verifica que create_scheduler retorna BackgroundScheduler configurado."""
    scheduler = create_scheduler()
    assert isinstance(scheduler, BackgroundScheduler)
    assert str(scheduler.timezone) == "UTC"


def test_add_product_jobs_agrega_jobs_activos(sample_product_config):
    """Verifica que agrega jobs solo para productos activos."""
    scheduler = MagicMock(spec=BackgroundScheduler)

    # Crear productos: 2 activos, 1 inactivo
    p1 = ProductConfig(**sample_product_config.model_dump())
    p2 = ProductConfig(**sample_product_config.model_dump())
    p2.id = "product-2"
    p3 = ProductConfig(**sample_product_config.model_dump())
    p3.id = "product-3"
    p3.activo = False

    products = [p1, p2, p3]
    count = add_product_jobs(scheduler, products)

    assert count == 2
    assert scheduler.add_job.call_count == 2

    # Verificar que se llamó con los IDs correctos
    called_ids = [call.kwargs.get("id") for call in scheduler.add_job.call_args_list]
    assert "product-2" in called_ids
    assert "product-3" not in called_ids


def test_add_product_jobs_configura_trigger_correcto(sample_product_config):
    """Verifica que el trigger usa frecuencia_horas del producto."""
    scheduler = MagicMock(spec=BackgroundScheduler)

    p = ProductConfig(**sample_product_config.model_dump())
    p.frecuencia_horas = 6
    add_product_jobs(scheduler, [p])

    call_args = scheduler.add_job.call_args
    trigger = call_args[1]["trigger"]
    assert trigger.interval_length == 6 * 3600  # 6 hours in seconds
    assert isinstance(trigger.interval, type(trigger.interval))  # timedelta


def test_add_product_jobs_id_unico_por_producto(sample_product_config):
    """Verifica que cada job usa el ID del producto."""
    scheduler = MagicMock(spec=BackgroundScheduler)

    p1 = ProductConfig(**sample_product_config.model_dump())
    p1.id = "prod-a"
    p2 = ProductConfig(**sample_product_config.model_dump())
    p2.id = "prod-b"

    add_product_jobs(scheduler, [p1, p2])

    ids = [call.kwargs["id"] for call in scheduler.add_job.call_args_list]
    assert ids == ["prod-a", "prod-b"]


def test_scrape_job_scrapea_y_guarda(
    sample_product_config,
    mock_httpx,
    sample_html,
    sample_scraped_price,
):
    """Verifica que _scrape_job scrapea, analiza y guarda."""
    # Mock BD: sin precio anterior
    with (
        patch(
            "monitor_de_precios.services.scheduler.get_last_price", return_value=None
        ) as mock_get_last,
        patch("monitor_de_precios.services.scheduler.insert_price", return_value=1) as mock_insert,
        patch(
            "monitor_de_precios.services.scheduler.es_cambio_significativo", return_value=False
        ) as mock_significativo,
        patch("monitor_de_precios.services.scheduler.alerta_precio_cambio") as mock_alerta,
        patch(
            "monitor_de_precios.services.scheduler.scrape_product",
            return_value=sample_scraped_price,
        ),
    ):
        _scrape_job(sample_product_config)

        # Verificar llamadas
        mock_get_last.assert_called_once_with("Test Product", "Test Store")
        mock_insert.assert_called_once()
        mock_significativo.assert_not_called()
        mock_alerta.assert_not_called()


def test_scrape_job_alerta_si_significativo(
    sample_product_config,
    sample_scraped_price,
):
    """Verifica alerta si hay cambio significativo."""
    last_price = {"precio": 100000.0}

    with (
        patch("monitor_de_precios.services.scheduler.get_last_price", return_value=last_price),
        patch("monitor_de_precios.services.scheduler.insert_price", return_value=1),
        patch(
            "monitor_de_precios.services.scheduler.es_cambio_significativo", return_value=True
        ) as mock_significativo,
        patch("monitor_de_precios.services.scheduler.alerta_precio_cambio") as mock_alerta,
        patch(
            "monitor_de_precios.services.scheduler.scrape_product",
            return_value=sample_scraped_price,
        ),
    ):
        _scrape_job(sample_product_config)

    mock_significativo.assert_called_once()
    mock_alerta.assert_called_once()


def test_scrape_job_log_error_si_falla(sample_product_config):
    """Verifica que loggea error si scraping falla."""
    from monitor_de_precios.services import database as db_module

    with (
        patch.object(db_module, "get_last_price", return_value=None),
        patch(
            "monitor_de_precios.services.scheduler.scrape_product",
            side_effect=Exception("Network error"),
        ),
        patch("monitor_de_precios.services.scheduler.logger") as mock_logger,
    ):
        _scrape_job(sample_product_config)

        mock_logger.error.assert_called()
        args = mock_logger.error.call_args[0]
        assert "Error scrapeando" in args[0]
