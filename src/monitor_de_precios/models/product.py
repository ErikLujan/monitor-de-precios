"""Pydantic models for product configuration and scraped data."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ProductFieldConfig(BaseModel):
    """Configuración de un campo a extraer del HTML."""

    nombre: str = Field(..., description="Clave interna del campo (ej. precio, titulo)")
    tipo: Literal["numero", "texto"] = Field(..., description="Tipo de dato a extraer")
    selectores: list[str] = Field(..., description="Lista de selectores CSS en orden de prioridad")
    atributo: str | None = Field(
        default=None,
        description="Atributo HTML a extraer (ej. content, href) o None para texto visible",
    )
    limpiar: bool = Field(
        default=False,
        description="Si True y tipo=numero, quita caracteres no numéricos excepto punto decimal",
    )


class ProductConfig(BaseModel):
    """Configuración completa de un producto a monitorear."""

    id: str = Field(..., description="Identificador único (slug, sin espacios)")
    nombre: str = Field(..., description="Nombre visible en UI y alertas")
    tienda: str = Field(..., description="Nombre de la tienda/competencia")
    url: HttpUrl = Field(..., description="URL completa del producto a monitorear")
    frecuencia_horas: int = Field(default=24, ge=1, description="Cada cuántas horas scrapeear")
    requiere_js: bool = Field(
        default=False, description="True = usa Playwright para contenido dinámico"
    )
    user_agent: str = Field(
        default="auto", description="User-Agent: 'auto' para rotativo o string fijo"
    )
    headers: dict[str, str] = Field(default_factory=dict, description="Headers HTTP extra")
    umbral_cambio_porcentaje: float = Field(
        default=5.0, ge=0.0, description="% mínimo para alertar"
    )
    umbral_precio_maximo: float | None = Field(
        default=None, ge=0.0, description="Alerta si precio <= este valor"
    )
    activo: bool = Field(default=True, description="True = incluido en scheduler")
    campos: list[ProductFieldConfig] = Field(
        default_factory=list, description="Campos a extraer del HTML"
    )


class ScrapedPrice(BaseModel):
    """Resultado de un scraping exitoso."""

    producto: str = Field(..., description="Nombre del producto (product.nombre)")
    tienda: str = Field(..., description="Nombre de la tienda (product.tienda)")
    precio: float = Field(..., ge=0.0, description="Precio extraído")
    moneda: str = Field(default="ARS", description="Código de moneda")
    fecha: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp UTC del scraping"
    )
    url: str | None = Field(default=None, description="URL del producto scrapeada")


class PriceVariation(BaseModel):
    """Variación de precio entre dos mediciones."""

    producto: str
    tienda: str
    precio_anterior: float = Field(..., ge=0.0)
    precio_actual: float = Field(..., ge=0.0)
    diferencia: float
    porcentaje: float
    moneda: str = Field(
        default="ARS", description="Código de moneda original (GBP, EUR, ARS, etc.)"
    )

    @property
    def es_aumento(self) -> bool:
        return self.diferencia > 0

    @property
    def es_disminucion(self) -> bool:
        return self.diferencia < 0
