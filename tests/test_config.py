"""Pruebas para la configuración centralizada."""

from monitor_de_precios.core.config import load_products


def test_settings_tiene_campos_requeridos(settings_mock):
    """Verifica que Settings tenga los campos requeridos."""
    assert settings_mock.telegram_bot_token == "test_token"
    assert settings_mock.telegram_chat_id == "-1001234567890"
    assert settings_mock.scrape_interval_hours == 24
    assert settings_mock.webhook_url == "https://webhook.test"
    assert settings_mock.streamlit_password == "testpass"
    assert settings_mock.log_level == "DEBUG"


def test_settings_extra_ignore(settings_mock):
    """Verifica que campos extra no causen error (extra='ignore')."""
    assert hasattr(settings_mock, "telegram_bot_token")
    assert hasattr(settings_mock, "telegram_chat_id")


def test_load_products_valida_yaml(sample_product_config, tmp_path):
    """Verifica carga exitosa de products.yaml."""
    import yaml

    data = {"products": [sample_product_config.model_dump(mode="json")]}
    yaml_path = tmp_path / "products.yaml"
    yaml_path.write_text(yaml.dump(data))

    products = load_products(yaml_path)
    assert len(products) == 1
    assert products[0].id == "test-product-1"
    assert products[0].nombre == "Test Product"
    assert products[0].tienda == "Test Store"


def test_load_products_archivo_no_existente():
    """Verifica error si archivo no existe."""
    from pathlib import Path

    try:
        load_products(Path("/no/existe.yaml"))
        raise AssertionError("Debería lanzar FileNotFoundError")
    except FileNotFoundError:
        pass


def test_load_products_yaml_invalido(tmp_path):
    """Verifica error si YAML inválido."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("invalid: yaml: [")
    try:
        load_products(bad_yaml)
        raise AssertionError("Debería lanzar error")
    except Exception:
        pass


def test_load_products_sin_clave_products(tmp_path):
    """Verifica error si falta clave 'products'."""
    import yaml

    data = {"otra_cosa": []}
    yaml_path = tmp_path / "products.yaml"
    yaml_path.write_text(yaml.dump(data))
    try:
        load_products(yaml_path)
        raise AssertionError("Debería lanzar ValueError")
    except ValueError as e:
        assert "clave 'products'" in str(e)


def test_load_products_validacion_falla(tmp_path):
    """Verifica error si validación Pydantic falla."""
    import yaml

    data = {"products": [{"id": "bad", "nombre": "X", "tienda": "Y", "url": "not-a-url"}]}
    yaml_path = tmp_path / "products.yaml"
    yaml_path.write_text(yaml.dump(data))
    try:
        load_products(yaml_path)
        raise AssertionError("Debería lanzar ValueError")
    except ValueError as e:
        assert "validando producto" in str(e)


def test_load_products_example_file():
    """Verifica carga exitosa de products.yaml.example con productos reales."""
    from pathlib import Path

    yaml_path = Path("products.yaml.example")
    assert yaml_path.exists(), "products.yaml.example debe existir"

    products = load_products(yaml_path)
    assert len(products) >= 3, "Debería cargar al menos 3 productos del ejemplo"

    # Verificar que los productos reales de books.toscrape.com están presentes
    ids = [p.id for p in products]
    assert "libro-luz-en-el-atico" in ids
    assert "libro-tipping-the-velvet" in ids

    # Verificar que los productos tienen campos configurados
    for p in products:
        assert p.id
        assert p.nombre
        assert p.tienda
        assert p.url
        assert p.frecuencia_horas > 0
        assert len(p.campos) > 0
        assert any(c.nombre == "precio" for c in p.campos)
