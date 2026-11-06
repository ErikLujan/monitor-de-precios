"""Pruebas para el scraper."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from bs4 import BeautifulSoup

from monitor_de_precios.models.product import ProductConfig, ProductFieldConfig
from monitor_de_precios.services.scraper import (
    _build_headers,
    _clean_price_text,
    _extract_field,
    _get_user_agent,
    extract_with_fallback,
    scrape_product,
)


def test_clean_price_text_formatos_varios():
    """Verifica limpieza de varios formatos de precio."""
    assert _clean_price_text("$1.200.000") == 1200000.0
    assert _clean_price_text("$1,200,000") == 1200000.0
    assert _clean_price_text("1200000") == 1200000.0
    assert _clean_price_text("1.200.000,00") == 1200000.0
    assert _clean_price_text("1,200,000.00") == 1200000.0
    assert _clean_price_text("$ 120.000 ") == 120000.0
    assert _clean_price_text("ARS 120.000") == 120000.0


def test_clean_price_text_invalido():
    """Verifica None para texto no parseable."""
    assert _clean_price_text("gratis") is None
    assert _clean_price_text("") is None
    assert _clean_price_text("no hay precio") is None


def test_extract_field_numero_con_limpiar(sample_html):
    """Verifica extracción de campo número con limpieza."""
    field = ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=[".precio", "[itemprop='price']"],
        atributo=None,
        limpiar=True,
    )
    result = _extract_field(sample_html, field)
    assert result == 120000.0


def test_extract_field_texto_sin_limpiar(sample_html):
    """Verifica extracción de campo texto sin limpieza."""
    field = ProductFieldConfig(
        nombre="titulo",
        tipo="texto",
        selectores=["h1.product-title", "h1[itemprop='name']"],
        atributo=None,
        limpiar=False,
    )
    result = _extract_field(sample_html, field)
    assert result == "Test Product"


def test_extract_field_atributo_content(sample_html):
    """Verifica extracción usando atributo HTML."""
    field = ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=["[itemprop='price']"],
        atributo="content",
        limpiar=False,
    )
    result = _extract_field(sample_html, field)
    assert result == 120000.0


def test_extract_field_no_encontrado():
    """Verifica None si selector no encuentra nada."""
    field = ProductFieldConfig(
        nombre="inexistente",
        tipo="texto",
        selectores=[".no-existe"],
        atributo=None,
        limpiar=False,
    )
    result = _extract_field("<html><body></body></html>", field)
    assert result is None


def test_extract_with_fallback_numero(sample_html):
    """Verifica extract_with_fallback con campo número."""
    soup = BeautifulSoup(sample_html, "html.parser")
    field = ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=[".precio", "[itemprop='price']"],
        atributo=None,
        limpiar=True,
    )
    result = extract_with_fallback(soup, field)
    assert result == 120000.0


def test_extract_with_fallback_texto(sample_html):
    """Verifica extract_with_fallback con campo texto."""
    soup = BeautifulSoup(sample_html, "html.parser")
    field = ProductFieldConfig(
        nombre="titulo",
        tipo="texto",
        selectores=["h1.product-title", "h1[itemprop='name']"],
        atributo=None,
        limpiar=False,
    )
    result = extract_with_fallback(soup, field)
    assert result == "Test Product"


def test_extract_with_fallback_atributo(sample_html):
    """Verifica extract_with_fallback usando atributo HTML."""
    soup = BeautifulSoup(sample_html, "html.parser")
    field = ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=["[itemprop='price']"],
        atributo="content",
        limpiar=False,
    )
    result = extract_with_fallback(soup, field)
    assert result == 120000.0


def test_extract_with_fallback_no_encontrado():
    """Verifica None si selector no encuentra nada en extract_with_fallback."""
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    field = ProductFieldConfig(
        nombre="inexistente",
        tipo="texto",
        selectores=[".no-existe"],
        atributo=None,
        limpiar=False,
    )
    result = extract_with_fallback(soup, field)
    assert result is None


def test_extract_with_fallback_selectores_en_orden():
    """Verifica que extract_with_fallback prueba selectores en orden."""
    html = """
    <html><body>
        <span class="precio-secundario">$99.990</span>
        <span class="precio-principal">$150.000</span>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    field = ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=[".precio-principal", ".precio-secundario"],
        atributo=None,
        limpiar=True,
    )
    result = extract_with_fallback(soup, field)
    assert result == 150000.0  # El primero que matchea


def test_get_user_agent_auto():
    """Verifica user agent rotativo cuando 'auto'."""
    from monitor_de_precios.services.scraper import USER_AGENTS

    config = ProductConfig(
        id="test",
        nombre="Test",
        tienda="Store",
        url="https://example.com",
        user_agent="auto",
        campos=[],
    )
    ua = _get_user_agent(config)
    assert ua in USER_AGENTS


def test_get_user_agent_custom():
    """Verifica user agent fijo personalizado."""
    config = ProductConfig(
        id="test",
        nombre="Test",
        tienda="Store",
        url="https://example.com",
        user_agent="MiBot/1.0",
        campos=[],
    )
    assert _get_user_agent(config) == "MiBot/1.0"


def test_build_headers_combina_defaults_y_custom():
    """Verifica que headers combinan defaults + custom."""
    config = ProductConfig(
        id="test",
        nombre="Test",
        tienda="Store",
        url="https://example.com",
        headers={"X-Custom": "value", "Accept-Language": "en-US"},
        campos=[],
    )
    headers = _build_headers(config)
    assert "User-Agent" in headers
    assert headers["X-Custom"] == "value"
    assert headers["Accept-Language"] == "en-US"  # custom sobrescribe default


def test_scrape_product_precio_obligatorio(sample_product_config, mock_httpx):
    """Verifica que scrape_product falla si no hay precio."""
    mock_resp = MagicMock()
    mock_resp.text = "<html><body>Sin precio aqui</body></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_httpx.get.return_value = mock_resp

    with pytest.raises(ValueError, match="No se pudo extraer precio"):
        scrape_product(sample_product_config)


def test_scrape_product_exitoso(sample_product_config, mock_httpx, sample_html):
    """Verifica scraping exitoso retorna ScrapedPrice e inserta en BD."""
    mock_resp = MagicMock()
    mock_resp.text = sample_html
    mock_resp.raise_for_status = MagicMock()
    mock_httpx.get.return_value = mock_resp

    import monitor_de_precios.services.database as db_module

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = Path(f.name)
    try:
        db_module.DB_PATH = temp_path
        db_module.init_db()
        result = scrape_product(sample_product_config)

        assert result.producto == "Test Product"
        assert result.tienda == "Test Store"
        assert result.precio == 120000.0
        assert result.moneda == "ARS"
        assert result.url == "https://example.com/product"

        # Verificar que se insertó en BD
        recientes = db_module.get_recent_prices(limit=10)
        assert len(recientes) == 1
        assert recientes[0]["precio"] == 120000.0
        assert recientes[0]["producto"] == "Test Product"
    finally:
        db_module.DB_PATH = Path("data/precios.db")
        temp_path.unlink(missing_ok=True)


def test_scrape_product_inserta_en_bd(sample_product_config, mock_httpx, sample_html):
    """Verifica que scrape_product inserta el precio en la base de datos."""
    mock_resp = MagicMock()
    mock_resp.text = sample_html
    mock_resp.raise_for_status = MagicMock()
    mock_httpx.get.return_value = mock_resp

    import monitor_de_precios.services.database as db_module

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = Path(f.name)
    try:
        db_module.DB_PATH = temp_path
        db_module.init_db()

        # Ejecutar scrape_product dos veces
        scrape_product(sample_product_config)
        scrape_product(sample_product_config)

        # Verificar que hay 2 registros
        recientes = db_module.get_recent_prices(limit=10)
        assert len(recientes) == 2
    finally:
        db_module.DB_PATH = Path("data/precios.db")
        temp_path.unlink(missing_ok=True)


def test_scrape_static_retries():
    """Verifica que _scrape_static reintenta en errores de conexión."""
    from monitor_de_precios.services.scraper import _scrape_static

    call_count = 0

    def mock_get(*_args, **_kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.ConnectError("Connection refused")
        resp = MagicMock()
        resp.text = "<html><body><span class='price'>$100</span></body></html>"
        resp.raise_for_status = MagicMock()
        return resp

    config = ProductConfig(
        id="test",
        nombre="Test",
        tienda="Store",
        url="https://example.com/product",
        user_agent="auto",
        headers={},
        campos=[
            ProductFieldConfig(
                nombre="precio",
                tipo="numero",
                selectores=[".price"],
                atributo=None,
                limpiar=True,
            )
        ],
    )

    with patch("monitor_de_precios.services.scraper.httpx.Client") as mock_client:
        instance = MagicMock()
        mock_client.return_value.__enter__.return_value = instance
        instance.get.side_effect = mock_get

        # No verificar robots.txt en este test (mockea _check_robots_txt)
        with patch("monitor_de_precios.services.scraper._check_robots_txt", return_value=True):
            html = _scrape_static(config)

        assert call_count == 3  # Reintentó 3 veces
        assert "<span class='price'>$100</span>" in html
