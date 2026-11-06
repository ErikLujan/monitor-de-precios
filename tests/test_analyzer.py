"""Pruebas para el analizador de variaciones."""

from monitor_de_precios.models.product import PriceVariation
from monitor_de_precios.services.analyzer import calcular_variacion, es_cambio_significativo


def test_calcular_variacion_aumento():
    """Verifica cálculo cuando precio aumenta."""
    v = calcular_variacion(100000.0, 120000.0, "Prod", "Store")
    assert v.precio_anterior == 100000.0
    assert v.precio_actual == 120000.0
    assert v.diferencia == 20000.0
    assert v.porcentaje == 20.0
    assert v.es_aumento is True
    assert v.es_disminucion is False


def test_calcular_variacion_disminucion():
    """Verifica cálculo cuando precio disminuye."""
    v = calcular_variacion(100000.0, 80000.0, "Prod", "Store")
    assert v.diferencia == -20000.0
    assert v.porcentaje == -20.0
    assert v.es_aumento is False
    assert v.es_disminucion is True


def test_calcular_variacion_sin_cambio():
    """Verifica cálculo sin cambio de precio."""
    v = calcular_variacion(100000.0, 100000.0, "Prod", "Store")
    assert v.diferencia == 0.0
    assert v.porcentaje == 0.0
    assert v.es_aumento is False
    assert v.es_disminucion is False


def test_calcular_variacion_precio_anterior_cero():
    """Verifica manejo de precio anterior = 0 (evita división por cero)."""
    v = calcular_variacion(0.0, 100000.0, "Prod", "Store")
    assert v.porcentaje == 0.0


def test_es_cambio_significativo_porcentaje_superado():
    """Verifica True si cambio supera umbral porcentual."""
    v = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=110000.0,
        diferencia=10000.0,
        porcentaje=10.0,
    )
    assert es_cambio_significativo(v, umbral_porcentaje=5.0) is True


def test_es_cambio_significativo_porcentaje_no_superado():
    """Verifica False si cambio no supera umbral."""
    v = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=102000.0,
        diferencia=2000.0,
        porcentaje=2.0,
    )
    assert es_cambio_significativo(v, umbral_porcentaje=5.0) is False


def test_es_cambio_significativo_umbral_exacto():
    """Verifica True si cambio exactamente en umbral."""
    v = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=105000.0,
        diferencia=5000.0,
        porcentaje=5.0,
    )
    assert es_cambio_significativo(v, umbral_porcentaje=5.0) is True


def test_es_cambio_significativo_precio_maximo():
    """Verifica True si precio actual <= umbral_precio_maximo."""
    v = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=80000.0,
        diferencia=-20000.0,
        porcentaje=-20.0,
    )
    assert es_cambio_significativo(v, umbral_porcentaje=5.0, umbral_precio_maximo=90000.0) is True


def test_es_cambio_significativo_precio_maximo_no_alcanzado():
    """Verifica False si precio actual > umbral_precio_maximo Y porcentaje no supera umbral."""
    v = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=95000.0,
        diferencia=-5000.0,
        porcentaje=-4.0,  # Menos del 5% umbral
    )
    assert es_cambio_significativo(v, umbral_porcentaje=5.0, umbral_precio_maximo=90000.0) is False


def test_es_cambio_significativo_ambos_umbrales():
    """Verifica que cualquiera de los dos umbrales activa alerta."""
    # Solo umbral porcentaje
    v1 = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=110000.0,
        diferencia=10000.0,
        porcentaje=10.0,
    )
    assert es_cambio_significativo(v1, umbral_porcentaje=5.0, umbral_precio_maximo=50000.0) is True

    # Solo umbral precio máximo
    v2 = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=40000.0,
        diferencia=-60000.0,
        porcentaje=-60.0,
    )
    assert es_cambio_significativo(v2, umbral_porcentaje=5.0, umbral_precio_maximo=50000.0) is True

    # Ninguno
    v3 = PriceVariation(
        producto="P",
        tienda="T",
        precio_anterior=100000.0,
        precio_actual=102000.0,
        diferencia=2000.0,
        porcentaje=2.0,
    )
    assert es_cambio_significativo(v3, umbral_porcentaje=5.0, umbral_precio_maximo=50000.0) is False
