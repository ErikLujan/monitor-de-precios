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
        return True

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
    settings = get_settings()
    emoji = "📈" if variacion.es_aumento else "📉"

    moneda = getattr(variacion, "moneda", "ARS")
    if moneda == "GBP":
        rate = settings.gbp_to_ars_rate
        precio_anterior_ars = variacion.precio_anterior * rate
        precio_actual_ars = variacion.precio_actual * rate
        diferencia_ars = variacion.diferencia * rate
        moneda_simbolo = "£"
        mensaje = (
            f"{emoji} <b>Cambio de precio detectado</b>\n\n"
            f"📦 <b>Producto:</b> {variacion.producto}\n"
            f"🏪 <b>Tienda:</b> {variacion.tienda}\n"
            f"💰 <b>Precio anterior:</b> {moneda_simbolo}{variacion.precio_anterior:,.2f} GBP (${precio_anterior_ars:,.0f} ARS)\n"
            f"💰 <b>Precio actual:</b> {moneda_simbolo}{variacion.precio_actual:,.2f} GBP (${precio_actual_ars:,.0f} ARS)\n"
            f"📊 <b>Cambio:</b> {moneda_simbolo}{variacion.diferencia:+,.2f} GBP (${diferencia_ars:+,.0f} ARS) ({variacion.porcentaje:+.2f}%)\n"
        )
    else:
        moneda_simbolo = "$" if moneda == "ARS" else moneda
        mensaje = (
            f"{emoji} <b>Cambio de precio detectado</b>\n\n"
            f"📦 <b>Producto:</b> {variacion.producto}\n"
            f"🏪 <b>Tienda:</b> {variacion.tienda}\n"
            f"💰 <b>Precio anterior:</b> {moneda_simbolo}{variacion.precio_anterior:,.2f} {moneda}\n"
            f"💰 <b>Precio actual:</b> {moneda_simbolo}{variacion.precio_actual:,.2f} {moneda}\n"
            f"📊 <b>Cambio:</b> {moneda_simbolo}{variacion.diferencia:+,.2f} {moneda} ({variacion.porcentaje:+.2f}%)\n"
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
        "moneda": moneda,
        "direccion": "aumento" if variacion.es_aumento else "disminucion",
        "url": url,
    }
    if moneda == "GBP":
        rate = settings.gbp_to_ars_rate
        webhook_payload["precio_anterior_ars"] = round(variacion.precio_anterior * rate, 2)
        webhook_payload["precio_actual_ars"] = round(variacion.precio_actual * rate, 2)
        webhook_payload["diferencia_ars"] = round(variacion.diferencia * rate, 2)
        webhook_payload["gbp_to_ars_rate"] = rate

    enviar_webhook(webhook_payload)
