"""Acceso a base de datos SQLite para almacenar precios."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC
from pathlib import Path
from typing import Any

from monitor_de_precios.models.product import ScrapedPrice

# DB_PATH relativo a la raíz del proyecto (donde se ejecuta uv run)
DB_PATH = Path("data/precios.db")


@contextmanager
def _get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager para conexiones SQLite con row_factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Crea la tabla de precios si no existe."""
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                tienda TEXT NOT NULL,
                precio REAL NOT NULL,
                moneda TEXT DEFAULT 'ARS',
                fecha TEXT NOT NULL,
                url TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_precios_producto_fecha
            ON precios (producto, fecha DESC)
            """
        )
        conn.commit()


def insert_price(scraped: ScrapedPrice) -> int:
    """Inserta un registro de precio y devuelve el ID insertado.

    Args:
        scraped: Objeto ScrapedPrice con los datos a guardar

    Returns:
        ID del registro insertado
    """
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO precios (producto, tienda, precio, moneda, fecha, url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                scraped.producto,
                scraped.tienda,
                scraped.precio,
                scraped.moneda,
                scraped.fecha.isoformat(),
                scraped.url,
            ),
        )
        conn.commit()
        last_id = cursor.lastrowid
        return int(last_id) if last_id is not None else 0


def get_recent_prices(limit: int = 100) -> list[dict[str, Any]]:
    """Devuelve los precios más recientes ordenados por fecha descendente.

    Args:
        limit: Número máximo de registros a devolver

    Returns:
        Lista de diccionarios con los campos de la tabla
    """
    with _get_connection() as conn:
        filas = conn.execute(
            """
            SELECT producto, tienda, precio, moneda, fecha, url
            FROM precios
            ORDER BY fecha DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def get_price_history(product_id: str, days: int = 30) -> list[dict[str, Any]]:
    """Devuelve el historial de precios de un producto en los últimos N días.

    Args:
        product_id: ID del producto (campo 'producto' en la tabla)
        days: Días hacia atrás para buscar

    Returns:
        Lista de diccionarios con los campos de la tabla
    """
    from datetime import datetime, timedelta

    fecha_limite = (datetime.now(UTC) - timedelta(days=days)).isoformat()

    with _get_connection() as conn:
        filas = conn.execute(
            """
            SELECT producto, tienda, precio, moneda, fecha, url
            FROM precios
            WHERE producto = ? AND fecha >= ?
            ORDER BY fecha ASC
            """,
            (product_id, fecha_limite),
        ).fetchall()
        return [dict(fila) for fila in filas]


def get_last_price(producto: str, tienda: str) -> dict[str, Any] | None:
    """Obtiene el último precio registrado para un producto en una tienda.

    Args:
        producto: Nombre del producto
        tienda: Nombre de la tienda

    Returns:
        Diccionario con el último precio o None si no existe
    """
    with _get_connection() as conn:
        fila = conn.execute(
            """
            SELECT producto, tienda, precio, moneda, fecha, url
            FROM precios
            WHERE producto = ? AND tienda = ?
            ORDER BY fecha DESC
            LIMIT 1
            """,
            (producto, tienda),
        ).fetchone()
        return dict(fila) if fila else None
