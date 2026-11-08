"""Configuración centralizada del proyecto monitor-de-precios."""

from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from monitor_de_precios.models.product import ProductConfig


class Settings(BaseSettings):
    """Ajustes de la aplicación cargados desde variables de entorno."""

    telegram_bot_token: str
    telegram_chat_id: str
    scrape_interval_hours: int = 24
    webhook_url: str | None = None
    streamlit_password: str | None = None
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


def load_products(path: Path | str) -> list[ProductConfig]:
    """Carga y valida productos desde un archivo YAML.

    Args:
        path: Ruta al archivo products.yaml

    Returns:
        Lista de ProductConfig validados

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el YAML es inválido o la validación Pydantic falla
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo de productos no encontrado: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "products" not in data:
        raise ValueError("El archivo YAML debe tener una clave 'products' con una lista")

    products = []
    for i, item in enumerate(data["products"]):
        try:
            product = ProductConfig.model_validate(item)
            products.append(product)
        except Exception as e:
            raise ValueError(
                f"Error validando producto #{i + 1} ('{item.get('id', 'unknown')}'): {e}"
            ) from e

    return products

_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Obtiene la instancia de configuración (inicializada perezosamente)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
