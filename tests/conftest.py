"""Fixtures compartidas para pruebas."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from monitor_de_precios.core.config import Settings
from monitor_de_precios.models.product import (
    PriceVariation,
    ProductConfig,
    ProductFieldConfig,
    ScrapedPrice,
)


@pytest.fixture
def settings_mock(monkeypatch):
    """Fixture con configuración de prueba."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-1001234567890")
    monkeypatch.setenv("SCRAPE_INTERVAL_HOURS", "24")
    monkeypatch.setenv("WEBHOOK_URL", "https://webhook.test")
    monkeypatch.setenv("STREAMLIT_PASSWORD", "testpass")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Reset the lazy settings instance so it picks up the new env vars
    import monitor_de_precios.core.config as config_mod
    config_mod._settings_instance = None

    # Create the mock settings instance
    mock_settings = Settings()

    monkeypatch.setattr("monitor_de_precios.core.config.get_settings", lambda: mock_settings)
    monkeypatch.setattr("monitor_de_precios.services.notifier.get_settings", lambda: mock_settings)

    return Settings()


@pytest.fixture
def sample_product_field():
    """Fixture con un campo de producto de ejemplo."""
    return ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=[".precio", "[itemprop='price']"],
        atributo=None,
        limpiar=True,
    )


@pytest.fixture
def sample_product_config(sample_product_field):
    """Fixture con configuración de producto completa."""
    return ProductConfig(
        id="test-product-1",
        nombre="Test Product",
        tienda="Test Store",
        url="https://example.com/product",
        frecuencia_horas=24,
        requiere_js=False,
        user_agent="auto",
        headers={},
        umbral_cambio_porcentaje=5.0,
        umbral_precio_maximo=100000.0,
        activo=True,
        campos=[sample_product_field],
    )


@pytest.fixture
def sample_scraped_price():
    """Fixture con precio scrapeado de ejemplo."""
    return ScrapedPrice(
        producto="Test Product",
        tienda="Test Store",
        precio=120000.0,
        moneda="ARS",
        fecha=datetime.now(UTC),
        url="https://example.com/product",
    )


@pytest.fixture
def sample_variation():
    """Fixture con variación de precio de ejemplo."""
    return PriceVariation(
        producto="Test Product",
        tienda="Test Store",
        precio_anterior=100000.0,
        precio_actual=120000.0,
        diferencia=20000.0,
        porcentaje=20.0,
    )


@pytest.fixture
def temp_db_path():
    """Fixture con path temporal para BD de pruebas."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def sample_html():
    """Fixture con HTML de ejemplo para testing scraper."""
    return """
    <html>
        <body>
            <div class="precio" itemprop="price" content="120000">$120.000</div>
            <h1 class="product-title" itemprop="name">Test Product</h1>
            <div class="stock-status">Disponible</div>
        </body>
    </html>
    """


@pytest.fixture
def mock_httpx():
    """Mock para httpx.Client."""
    with patch("monitor_de_precios.services.scraper.httpx.Client") as mock:
        client_instance = MagicMock()
        mock.return_value.__enter__.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_playwright():
    """Mock para Playwright."""
    with patch("monitor_de_precios.services.scraper.async_playwright") as mock:
        playwright_instance = AsyncMock()
        browser = AsyncMock()
        context = AsyncMock()
        page = AsyncMock()

        mock.return_value.__aenter__.return_value = playwright_instance
        playwright_instance.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page
        page.goto = AsyncMock()
        page.content = AsyncMock(return_value="<html><body>JS content</body></html>")
        browser.close = AsyncMock()

        yield page


@pytest.fixture
def mock_http():
    """Mock para HTTP requests (Telegram + webhook)."""
    with patch("httpx.Client") as mock:
        client_instance = MagicMock()
        mock.return_value.__enter__.return_value = client_instance
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        client_instance.post.return_value = resp
        yield client_instance


@pytest.fixture(autouse=True)
def _reset_logging():
    """Reset logging entre tests."""
    from loguru import logger

    logger.remove()
    yield
    logger.remove()
