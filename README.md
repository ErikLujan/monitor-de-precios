# Monitor de Precios y Alertas para E-commerce / PyMEs

Template production-ready para monitorear precios de la competencia. Extrae precios via scraping (httpx + BeautifulSoup + Playwright), almacena en SQLite, alerta por Telegram + webhook genérico, y expone dashboard en Streamlit. Orquestado con APScheduler en contenedor Podman.

## Estructura del proyecto

```
monitor-de-precios/
├── src/                          # Paquete principal (monitor_de_precios)
│   ├── __init__.py               # Exports públicos + __version__
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py               # Typer CLI: scrape, serve, init-db, test-notify, list-products, scheduler
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic Settings + load_products()
│   │   └── logging.py            # loguru setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py            # ProductConfig, ProductFieldConfig, ScrapedPrice, PriceVariation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLite CRUD (data/precios.db)
│   │   ├── scraper.py            # httpx + BS4 + Playwright fallback
│   │   ├── analyzer.py           # Variaciones + umbrales significativos
│   │   ├── notifier.py           # Telegram Bot API + webhook
│   │   └── scheduler.py          # APScheduler BackgroundScheduler
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py      # Dashboard + password auth opcional
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Fixtures compartidas
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_scraper.py
│   ├── test_database.py
│   ├── test_analyzer.py
│   ├── test_notifier.py
│   └── test_scheduler.py
├── data/                         # SQLite DB (gitignore)
├── logs/                         # Logs rotativos (gitignore)
├── Dockerfile                    # Multi-stage: base → deps → playwright → runtime
├── podman-compose.yml            # Services: scraper (scheduler) + ui (streamlit)
├── pyproject.toml                # Deps, tool config (ruff, mypy, pytest)
├── uv.lock
├── .env.example                  # Plantilla variables de entorno
├── .env                          # Secrets locales (gitignore)
├── products.yaml.example         # Plantilla configuración productos
├── products.yaml                 # Configuración real (gitignore)
├── .gitignore
├── .python-version               # Python 3.11.5
└── README.md
```

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Lenguaje | Python 3.11.5 |
| Gestor deps | `uv` |
| Config | Pydantic Settings v2 + pyyaml |
| DB | SQLite (archivo local) + `sqlite3` stdlib |
| Scraping estático | httpx + BeautifulSoup4 |
| Scraping dinámico | Playwright (Chromium) |
| Scheduler | APScheduler BackgroundScheduler |
| CLI | Typer + Rich |
| UI | Streamlit |
| Logging | loguru (rotación 10MB, retención 7d) |
| Alertas | Telegram Bot API + Webhook genérico |
| Calidad | ruff, mypy (strict), pytest, bandit, pip-audit |
| Contenedor | Podman / Docker |

## Requisitos previos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.11 (definido en `.python-version`)
- Podman (opcional, para deploy en contenedor)

## Instalación local

```bash
cd monitor-de-precios
uv sync

# Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, etc.

# Copiar y configurar productos a monitorear
cp products.yaml.example products.yaml
# Editar products.yaml con tus productos
```

## Variables de entorno (`.env`)

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Sí | Token de @BotFather | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Sí | Chat ID destino alertas | `-1001234567890` |
| `SCRAPE_INTERVAL_HOURS` | No | Intervalo fallback scheduler | `24` |
| `WEBHOOK_URL` | No | Endpoint genérico POST JSON | `https://hooks.example.com/price` |
| `STREAMLIT_PASSWORD` | No | Password SHA-256 para UI | `hash_sha256` |
| `LOG_LEVEL` | No | Nivel logging | `INFO` |

> **No uses comillas en los valores. Nunca commitees `.env`.**

## products.yaml — Esquema

```yaml
products:
  - id: unique-product-id           # slug único (PK lógica)
    nombre: "Display Name"          # visible en UI/alertas
    tienda: "Store Name"            # nombre competencia
    url: "https://store.com/prod"   # URL a scrapeear
    frecuencia_horas: 24            # intervalo APScheduler
    requiere_js: false              # true = Playwright
    user_agent: "auto"              # "auto" = rotativo, o string fijo
    headers: {}                     # headers HTTP extra
    umbral_cambio_porcentaje: 5.0   # % mínimo para alertar
    umbral_precio_maximo: 1500000   # alerta si precio <= este valor (null = desactivado)
    activo: true                    # false = pausado en scheduler
    campos:                         # campos a extraer (orden de prioridad)
      - nombre: precio              # clave interna
        tipo: numero                # "numero" | "texto"
        selectores:                 # CSS selectors (se prueba en orden)
          - ".precio"
          - "[itemprop='price']"
        atributo: null              # null = texto visible, o "content", "href"
        limpiar: true               # solo numero: strip non-digit/dot → float
      - nombre: titulo
        tipo: texto
        selectores: ["h1.producto"]
        atributo: null
        limpiar: false
```

Ver `products.yaml.example` para ejemplos completos.

## Comandos CLI

```bash
# Scraping manual (un ciclo todos los productos activos)
uv run python -m monitor_de_precios.cli.main scrape

# Inicializar base de datos
uv run python -m monitor_de_precios.cli.main init-db

# Listar productos configurados
uv run python -m monitor_de_precios.cli.main list-products

# Test notificaciones (Telegram + webhook)
uv run python -m monitor_de_precios.cli.main test-notify

# Iniciar dashboard Streamlit
uv run python -m monitor_de_precios.cli.main serve
# o directo:
uv run streamlit run src/ui/streamlit_app.py

# Iniciar scheduler (modo producción, bloquea)
uv run python -m monitor_de_precios.cli.main scheduler
```

## Deploy con Podman (producción)

```bash
# Construir imagen
podman compose build

# Levantar servicios (scraper + ui) en background
podman compose up -d

# Ver logs del scraper
podman logs -f monitor-de-precios-scraper

# Ver logs de la UI
podman logs -f monitor-de-precios-ui

# Detener
podman compose down
```

Servicios:
- **scraper**: Ejecuta `scheduler` (jobs periódicos por producto)
- **ui**: Expone Streamlit en puerto 8501

Volúmenes persistidos:
- `./data:/app/data` → SQLite `precios.db`
- `./logs:/app/logs` → Logs rotativos

## Calidad y verificaciones

```bash
# Sync deps congeladas
uv sync --frozen

# Lint + format check
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Typecheck strict
uv run mypy --strict src/

# Tests
uv run pytest tests/ -v

# Smoke test CLI
uv run python -m monitor_de_precios.cli.main list-products

# Seguridad
uv run pip-audit
uv run bandit -r src/
```

## Desarrollo

### Ejecutar tests

```bash
# Todos
uv run pytest

# Archivo específico
uv run pytest tests/test_scraper.py

# Por patrón
uv run pytest -k "test_calcular"
```

### Formatear código

```bash
uv run ruff format src/ tests/
uv run ruff check --fix src/ tests/
```

### Agregar dependencias

```bash
# Runtime
uv add httpx

# Dev
uv add --dev pytest-xdist
```

## Licencia

Uso libre para fines educativos, portafolio y comercial. Basado en template Workana-ready.