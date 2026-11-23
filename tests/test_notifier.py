"""Pruebas para el notificador (Telegram + webhook)."""

from monitor_de_precios.core.config import Settings
from monitor_de_precios.models.product import PriceVariation
from monitor_de_precios.services.notifier import (
    alerta_precio_cambio,
    enviar_alerta_telegram,
    enviar_webhook,
)


def test_enviar_alerta_telegram_exitoso(mock_http, settings_mock):
    """Verifica envío exitoso a Telegram."""
    result = enviar_alerta_telegram("Test message")
    assert result is True
    mock_http.post.assert_called_once()
    args, kwargs = mock_http.post.call_args
    assert "sendMessage" in args[0]
    assert kwargs["json"]["chat_id"] == "-1001234567890"
    assert kwargs["json"]["text"] == "Test message"
    assert kwargs["json"]["parse_mode"] == "HTML"


def test_enviar_alerta_telegram_sin_config(monkeypatch):
    """Verifica False si falta configuración."""
    # Set empty values to trigger the check
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "")
    monkeypatch.setenv("SCRAPE_INTERVAL_HOURS", "24")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Need to reset the lazy settings instance
    import monitor_de_precios.core.config as config_mod

    config_mod._settings_instance = None

    result = enviar_alerta_telegram("Test")
    assert result is False


def test_enviar_alerta_telegram_error_red(mock_http, settings_mock):
    """Verifica False y log en error de red."""
    mock_http.post.side_effect = Exception("Connection error")
    result = enviar_alerta_telegram("Test")
    assert result is False


def test_enviar_webhook_exitoso(mock_http, settings_mock):
    """Verifica envío exitoso a webhook."""
    payload = {"event": "test", "data": 123}
    result = enviar_webhook(payload)
    assert result is True
    mock_http.post.assert_called_once_with("https://webhook.test", json=payload, timeout=15.0)


def test_enviar_webhook_sin_url(monkeypatch):
    """Verifica True silencioso si no hay webhook_url."""
    monkeypatch.delenv("WEBHOOK_URL", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    import monitor_de_precios.core.config as config_mod
    config_mod._settings_instance = None

    monkeypatch.setattr("monitor_de_precios.core.config.get_settings", lambda: Settings())
    monkeypatch.setattr("monitor_de_precios.services.notifier.get_settings", lambda: Settings())

    result = enviar_webhook({"test": "data"})
    assert result is True


def test_enviar_webhook_error_red(mock_http, settings_mock):
    """Verifica False en error de red."""
    mock_http.post.side_effect = Exception("Timeout")
    result = enviar_webhook({"test": "data"})
    assert result is False


def test_alerta_precio_cambio_llama_ambos(mock_http, settings_mock):
    """Verifica que alerta_precio_cambio llama a Telegram y webhook."""
    variacion = PriceVariation(
        producto="Test Product",
        tienda="Test Store",
        precio_anterior=100000.0,
        precio_actual=120000.0,
        diferencia=20000.0,
        porcentaje=20.0,
    )

    alerta_precio_cambio(variacion, url="https://example.com/prod")

    # Verificar que se hicieron 2 llamadas POST (Telegram + webhook)
    assert mock_http.post.call_count == 2

    # Obtener las llamadas
    calls = mock_http.post.call_args_list

    # Primera llamada: Telegram
    calls[0]
    assert "sendMessage" in calls[0][0][0]
    assert "📈" in calls[0][1]["json"]["text"]  # emoji aumento
    assert "Test Product" in calls[0][1]["json"]["text"]
    assert "20.00%" in calls[0][1]["json"]["text"]

    # Segunda llamada: webhook
    calls[1]
    assert calls[1][0][0] == "https://webhook.test"
    payload = calls[1][1]["json"]
    assert payload["event"] == "price_change"
    assert payload["producto"] == "Test Product"
    assert payload["direccion"] == "aumento"
    assert payload["url"] == "https://example.com/prod"


def test_alerta_precio_cambio_disminucion(mock_http, settings_mock):
    """Verifica emoji 📉 para disminución."""
    variacion = PriceVariation(
        producto="Test",
        tienda="Store",
        precio_anterior=100000.0,
        precio_actual=80000.0,
        diferencia=-20000.0,
        porcentaje=-20.0,
    )

    alerta_precio_cambio(variacion)

    # Verificar que se hizo 1 llamada POST a Telegram (webhook también se llama pero retorna early)
    assert mock_http.post.call_count >= 1

    tg_call = mock_http.post.call_args_list[0]
    assert "📉" in tg_call[1]["json"]["text"]  # emoji disminución
