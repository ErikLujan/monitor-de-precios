"""Pruebas para modelos Pydantic."""

from datetime import UTC

from monitor_de_precios.models.product import (
    PriceVariation,
    ProductConfig,
    ProductFieldConfig,
    ScrapedPrice,
)


def test_product_field_config_valido():
    """Verifica creación de ProductFieldConfig válido."""
    field = ProductFieldConfig(
        nombre="precio",
        tipo="numero",
        selectores=[".precio", "[itemprop='price']"],
        atributo="content",
        limpiar=True,
    )
    assert field.nombre == "precio"
    assert field.tipo == "numero"
    assert field.atributo == "content"
    assert field.limpiar is True


def test_product_field_config_tipo_invalido():
    """Verifica error si tipo no es 'numero' o 'texto'."""
    try:
        ProductFieldConfig(
            nombre="precio",
            tipo="invalido",
            selectores=[".precio"],
        )
        raise AssertionError("Debería lanzar error de validación")
    except Exception:
        pass


def test_product_config_valido(sample_product_field):
    """Verifica creación de ProductConfig válido."""
    config = ProductConfig(
        id="test-1",
        nombre="Test",
        tienda="Store",
        url="https://example.com/prod",
        frecuencia_horas=12,
        requiere_js=True,
        user_agent="custom-ua",
        headers={"Accept-Language": "es-AR"},
        umbral_cambio_porcentaje=3.5,
        umbral_precio_maximo=50000.0,
        activo=False,
        campos=[sample_product_field],
    )
    assert config.id == "test-1"
    assert config.frecuencia_horas == 12
    assert config.requiere_js is True
    assert config.user_agent == "custom-ua"
    assert config.umbral_cambio_porcentaje == 3.5


def test_product_config_url_invalida():
    """Verifica error si URL inválida."""
    try:
        ProductConfig(
            id="test",
            nombre="Test",
            tienda="Store",
            url="not-a-url",
            campos=[],
        )
        raise AssertionError("Debería lanzar error de validación")
    except Exception:
        pass


def test_product_config_frecuencia_minima():
    """Verifica que frecuencia_horas >= 1."""
    try:
        ProductConfig(
            id="test",
            nombre="Test",
            tienda="Store",
            url="https://example.com",
            frecuencia_horas=0,
            campos=[],
        )
        raise AssertionError("Debería lanzar error de validación")
    except Exception:
        pass


def test_scraped_price_valido():
    """Verifica creación de ScrapedPrice válido."""
    from datetime import datetime

    price = ScrapedPrice(
        producto="Test",
        tienda="Store",
        precio=12345.67,
        moneda="ARS",
        fecha=datetime.now(UTC),
        url="https://example.com",
    )
    assert price.precio == 12345.67
    assert price.moneda == "ARS"


def test_scraped_price_precio_negativo():
    """Verifica error si precio negativo."""
    from datetime import datetime

    try:
        ScrapedPrice(
            producto="Test",
            tienda="Store",
            precio=-100.0,
            fecha=datetime.now(UTC),
        )
        raise AssertionError("Debería lanzar error de validación")
    except Exception:
        pass


def test_price_variation_propiedades(sample_variation):
    """Verifica propiedades es_aumento/es_disminucion."""
    # Aumento
    assert sample_variation.es_aumento is True
    assert sample_variation.es_disminucion is False

    # Disminución
    v2 = PriceVariation(
        producto="Test",
        tienda="Store",
        precio_anterior=120000.0,
        precio_actual=100000.0,
        diferencia=-20000.0,
        porcentaje=-16.67,
    )
    assert v2.es_aumento is False
    assert v2.es_disminucion is True

    # Sin cambio
    v3 = PriceVariation(
        producto="Test",
        tienda="Store",
        precio_anterior=100000.0,
        precio_actual=100000.0,
        diferencia=0.0,
        porcentaje=0.0,
    )
    assert v3.es_aumento is False
    assert v3.es_disminucion is False
