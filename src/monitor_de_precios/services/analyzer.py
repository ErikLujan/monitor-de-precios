"""Análisis de variaciones de precios."""

from monitor_de_precios.models.product import PriceVariation


def calcular_variacion(
    precio_anterior: float,
    precio_actual: float,
    producto: str = "",
    tienda: str = "",
    moneda: str = "ARS",
) -> PriceVariation:
    """Calcula la diferencia absoluta y porcentual entre dos precios.

    Args:
        precio_anterior: Precio previo de referencia
        precio_actual: Precio recién scrapeado
        producto: Nombre del producto (opcional)
        tienda: Nombre de la tienda (opcional)
        moneda: Código de moneda original (opcional, default ARS)

    Returns:
        PriceVariation con los detalles del cambio
    """
    diferencia = precio_actual - precio_anterior
    porcentaje = (diferencia / precio_anterior * 100) if precio_anterior else 0.0

    return PriceVariation(
        producto=producto,
        tienda=tienda,
        precio_anterior=precio_anterior,
        precio_actual=precio_actual,
        diferencia=diferencia,
        porcentaje=round(porcentaje, 2),
        moneda=moneda,
    )


def es_cambio_significativo(
    variacion: PriceVariation,
    umbral_porcentaje: float = 5.0,
    umbral_precio_maximo: float | None = None,
) -> bool:
    """Determina si un cambio de precio es significativo para alertar.

    Args:
        variacion: Objeto PriceVariation calculado
        umbral_porcentaje: % mínimo de cambio para considerar significativo
        umbral_precio_maximo: Si el precio actual está por debajo, alertar

    Returns:
        True si el cambio supera umbrales, False en caso contrario
    """
    if abs(variacion.porcentaje) >= umbral_porcentaje:
        return True

    if umbral_precio_maximo is not None and variacion.precio_actual <= umbral_precio_maximo:
        return True

    return False
