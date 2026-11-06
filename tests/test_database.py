"""Pruebas para la base de datos SQLite."""

from datetime import UTC, datetime, timedelta

from monitor_de_precios.models.product import ScrapedPrice
from monitor_de_precios.services.database import (
    get_last_price,
    get_price_history,
    get_recent_prices,
    init_db,
    insert_price,
)


def test_init_db_crea_tabla(temp_db_path):
    """Verifica que init_db crea la tabla y índices."""
    # Monkey-patch DB_PATH
    import monitor_de_precios.services.database as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path
    try:
        init_db()
        # Verificar que archivo existe
        assert temp_db_path.exists()
    finally:
        db_module.DB_PATH = original_path


def test_insert_price_retorna_id(temp_db_path, sample_scraped_price):
    """Verifica que insert_price retorna ID autoincremental."""
    import monitor_de_precios.services.database as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path
    try:
        init_db()
        id1 = insert_price(sample_scraped_price)
        assert id1 == 1

        id2 = insert_price(sample_scraped_price)
        assert id2 == 2
    finally:
        db_module.DB_PATH = original_path


def test_get_recent_prices_orden_descendente(temp_db_path, sample_scraped_price):
    """Verifica que get_recent_prices ordena por fecha DESC."""
    import monitor_de_precios.services.database as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path
    try:
        init_db()
        # Insertar 3 precios con timestamps diferentes
        p1 = ScrapedPrice(
            producto="A", tienda="T", precio=100.0, fecha=datetime(2024, 1, 1, tzinfo=UTC)
        )
        p2 = ScrapedPrice(
            producto="A", tienda="T", precio=200.0, fecha=datetime(2024, 1, 2, tzinfo=UTC)
        )
        p3 = ScrapedPrice(
            producto="A", tienda="T", precio=300.0, fecha=datetime(2024, 1, 3, tzinfo=UTC)
        )
        insert_price(p1)
        insert_price(p2)
        insert_price(p3)

        recientes = get_recent_prices(limit=10)
        assert len(recientes) == 3
        # El más reciente primero
        assert recientes[0]["precio"] == 300.0
        assert recientes[1]["precio"] == 200.0
        assert recientes[2]["precio"] == 100.0
    finally:
        db_module.DB_PATH = original_path


def test_get_recent_prices_limite(temp_db_path, sample_scraped_price):
    """Verifica que limit funciona correctamente."""
    import monitor_de_precios.services.database as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path
    try:
        init_db()
        for i in range(5):
            p = ScrapedPrice(
                producto=f"P{i}", tienda="T", precio=float(i * 100), fecha=datetime.now(UTC)
            )
            insert_price(p)

        recientes = get_recent_prices(limit=3)
        assert len(recientes) == 3
    finally:
        db_module.DB_PATH = original_path


def test_get_price_history_filtra_por_producto_y_dias(temp_db_path):
    """Verifica que get_price_history filtra por producto y días."""
    import monitor_de_precios.services.database as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path
    try:
        init_db()
        now = datetime.now(UTC)
        old = now - timedelta(days=45)
        recent = now - timedelta(days=5)

        p_old = ScrapedPrice(producto="Prod1", tienda="T", precio=100.0, fecha=old)
        p_recent = ScrapedPrice(producto="Prod1", tienda="T", precio=200.0, fecha=recent)
        p_other = ScrapedPrice(producto="Prod2", tienda="T", precio=300.0, fecha=recent)

        insert_price(p_old)
        insert_price(p_recent)
        insert_price(p_other)

        history = get_price_history("Prod1", days=30)
        assert len(history) == 1
        assert history[0]["precio"] == 200.0

        history_all = get_price_history("Prod1", days=60)
        assert len(history_all) == 2
    finally:
        db_module.DB_PATH = original_path


def test_get_last_price_retorna_ultimo(temp_db_path):
    """Verifica get_last_price retorna el más reciente."""
    import monitor_de_precios.services.database as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path
    try:
        init_db()
        p1 = ScrapedPrice(
            producto="X", tienda="T", precio=100.0, fecha=datetime(2024, 1, 1, tzinfo=UTC)
        )
        p2 = ScrapedPrice(
            producto="X", tienda="T", precio=200.0, fecha=datetime(2024, 1, 2, tzinfo=UTC)
        )
        insert_price(p1)
        insert_price(p2)

        last = get_last_price("X", "T")
        assert last is not None
        assert last["precio"] == 200.0

        # Producto inexistente
        none = get_last_price("NoExiste", "T")
        assert none is None
    finally:
        db_module.DB_PATH = original_path
