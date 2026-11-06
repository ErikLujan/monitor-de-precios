"""Envío de alertas por Telegram Bot API y webhook genérico."""

from typing import Any

import httpx

from monitor_de_precios.core.config import get_settings
from monitor_de_precios.core.logging import logger
from monitor_de_precios.models.product import PriceVariation


def enviar_alerta_telegram(mensaje: str) -> bool:
    """Envía un mensaje de texto por Telegram Bot API.

    Args:
        mensaje: Texto del mensaje (HTML permitido)

    Returns:
        True si se envió correctamente, False en caso de error
    """
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram no configurado (faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID)")
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Alerta Telegram enviada correctamente")
            return True
    except Exception as e:
        logger.error(f"Error enviando alerta Telegram: {e}")
        return False


def enviar_webhook(payload: dict[str, Any]) -> bool:
    """Envía payload JSON a webhook configurado.

    Args:
        payload: Diccionario a enviar como JSON

    Returns:
        True si se envió correctamente, False en caso de error o sin webhook
    """
    settings = get_settings()
    if not settings.webhook_url:
        return True  # Silencioso si no hay webhook configurado

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(settings.webhook_url, json=payload, timeout=15.0)
            resp.raise_for_status()
            logger.info("Webhook enviado correctamente")
            return True
    except Exception as e:
        logger.error(f"Error enviando webhook: {e}")
        return False


def alerta_precio_cambio(
    variacion: PriceVariation,
    url: str | None = None,
) -> None:
    """Envía alerta de cambio de precio por Telegram y webhook.

    Args:
        variacion: Objeto PriceVariation con los detalles
        url: URL del producto (opcional)
    """
    emoji = "📈" if variacion.es_aumento else "📉"

    mensaje = (
        f"{emoji} <b>Cambio de precio detectado</b>\n\n"
        f"📦 <b>Producto:</b> {variacion.producto}\n"
        f"🏪 <b>Tienda:</b> {variacion.tienda}\n"
        f"💰 <b>Precio anterior:</b> ${variacion.precio_anterior:,.2f} ARS\n"
        f"💰 <b>Precio actual:</b> ${variacion.precio_actual:,.2f} ARS\n"
        f"📊 <b>Cambio:</b> {variacion.diferencia:+,.2f} ARS ({variacion.porcentaje:+.2f}%)\n"
    )

    if url:
        mensaje += f"\n🔗 <a href='{url}'>Ver producto</a>"

    enviar_alerta_telegram(mensaje)

    webhook_payload = {
        "event": "price_change",
        "producto": variacion.producto,
        "tienda": variacion.tienda,
        "precio_anterior": variacion.precio_anterior,
        "precio_actual": variacion.precio_actual,
        "diferencia": variacion.diferencia,
        "porcentaje": variacion.porcentaje,
        "direccion": "aumento" if variacion.es_aumento else "disminucion",
        "url": url,
    }
    enviar_webhook(webhook_payload)
