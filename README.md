# Monitor de Precios y Alertas para E-commerce / PyMEs
[![CI](https://img.shields.io/github/actions/workflow/status/ErikLujan/monitor-de-precios/ci.yml?label=CI&branch=main)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/ci.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/ErikLujan/monitor-de-precios/cd.yml?label=CD&branch=main)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/cd.yml)
[![Daily Scraper](https://img.shields.io/github/actions/workflow/status/ErikLujan/monitor-de-precios/scraper.yml?label=Scraper)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/scraper.yml)
[![Tests: 65 passing](https://img.shields.io/badge/tests-65%20passing-brightgreen)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/ErikLujan/monitor-de-precios)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Security: bandit + pip-audit](https://img.shields.io/badge/security-bandit%20%2B%20pip--audit-green)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/ci.yml)

<table>
<tr>
<td width="50%" align="center">
<strong>Dashboard · Desktop</strong><br>
<img src="https://github.com/user-attachments/assets/6b1e6013-02f6-419a-af76-d42542afef83" width="100%" alt="Dashboard desktop">
</td>
<td width="50%" align="center">
<strong>Historial · Desktop</strong><br>
<img src="https://github.com/user-attachments/assets/d6fe43c1-ca23-44bd-905e-2ae7778457d3" width="100%" alt="Historial desktop">
</td>
</tr>
</table>

<p align="center">
<strong>Dashboard · Mobile</strong><br>
<img src="https://github.com/user-attachments/assets/4d750c75-6cd3-442c-9644-2c00dea281fb" width="300" alt="Dashboard mobile">
</p>

## Contenido

- [¿Qué hace este template?](#-qué-hace-este-template)
- [¿Para quién es este proyecto?](#-para-quién-es-este-proyecto)
- [Casos de uso (qué podés monitorear)](#-casos-de-uso-qué-podés-monitorear)
- [Stack tecnológico](#-stack-tecnológico)
- [Qué incluye vs qué no incluye](#-qué-incluye-vs-qué-no-incluye)
- [Inversión vs alternativas: ¿cuánto ahorrás?](#-inversión-vs-alternativas-cuánto-ahorrás)
- [Instalación rápida (5 minutos)](#-instalación-rápida-5-minutos)
- [Variables de entorno (`.env`)](#-variables-de-entorno-env)
- [products.yaml — Qué productos monitorear](#-productsyaml---qué-productos-monitorear)
- [Comandos CLI disponibles](#-comandos-cli-disponibles)
- [Deploy con Podman (producción)](#-deploy-con-podman-producción)
- [Calidad y verificaciones](#-calidad-y-verificaciones)
- [Arquitectura del sistema](#-arquitectura-del-sistema)
- [Solución de problemas (FAQ)](#-solución-de-problemas-faq)
- [Roadmap (próximas mejoras)](#-roadmap-próximas-mejoras)
- [Licencia](#-licencia)
- [Alcance del servicio (qué incluye el proyecto)](#-alcance-del-servicio-qué-incluye-el-proyecto)
- [Contacto y próximos pasos](#-contacto-y-próximos-pasos)

## ¿Qué hace este template?

[aca-va-la-futura-imagen-o-captura]
> **Captura sugerida:** Screenshot del dashboard con una alerta de cambio de precio visible, o screenshot del Telegram recibiendo una notificación.

Este **template production-ready** monitoriza precios de la competencia automáticamente, guarda el historial en una base de datos local (SQLite), detecta variaciones significativas y te avisa por **Telegram** o **webhook genérico**. Todo se visualiza en un dashboard **Streamlit** listo para usar.

Ideal para dueños de PyMEs, e-commerce y revendedores que necesitan tracking de precios sin pagar suscripciones mensuales caras.

### ¿Para quién es este proyecto?

| Audiencia | Qué obtiene |
|-----------|-------------|
| **Dueño de PyME / e-commerce** | Control de precios de la competencia sin suscripciones mensuales. Alertas automáticas cuando bajan o suben los precios. Dashboard visual para tomar decisiones de compra/venta. |
| **Recruiter / Tech Lead** | Código limpio, tipado estricto (mypy strict), 65 tests pasando, CI/CD verde en GitHub Actions, arquitectura documentada y seguridad auditada (bandit + pip-audit). |
| **Desarrollador** | Template listo para extender: agregar tiendas, cambiar frecuencia de scraping, exportar datos, integrar con otros sistemas, desplegar en Podman o Streamlit Cloud. |

### Casos de uso (qué podés monitorear)

| Caso de uso | Qué se rastrea | Valor para tu negocio |
|-------------|----------------|----------------------|
| **Precio de producto en tienda online** | Precio, disponibilidad, título, stock | Detectás cuando la competencia baja el precio y ajustás tu margen |
| **Variación de precio en marketplace** | Historial de precios, alertas por % de cambio | Sabés cuándo comprar stock o cuándo lanzar una promo |
| **Disponibilidad de stock crítico** | In/out of stock, tiempo de reposición | Evitás quiebres de stock en tus productos estrella |
| **Monitoreo de insumos / dólar** | Precio de insumos importados, tipo de cambio | Planificás costos y márgenes en productos importados |

---

## Stack tecnológico

```mermaid
flowchart LR
    subgraph Scheduler
        A[APScheduler\nBackgroundScheduler]
    end
    subgraph Scraper
        B[httpx + BS4]
        C[Playwright\n(JS opcional)]
    end
    subgraph Storage
        D[(SQLite\nprecios.db)]
    end
    subgraph Core
        E[Analizador\n(variaciones + umbrales)]
        F[Notificador\n(Telegram + Webhook)]
    end
    subgraph UI
        G[Streamlit\nDashboard]
    end

    A -->|dispara cada X hs| B
    A -->|dispara cada X hs| C
    B -->|HTML crudo| E
    C -->|HTML renderizado| E
    E -->|precio + moneda| D
    E -->|variación significativa| F
    F -->|alerta| G
    D -->|historial| G
```

| Capa | Tecnología |
|------|------------|
| Lenguaje | Python 3.11.5 |
| Gestor de dependencias | `uv` |
| Configuración | Pydantic Settings v2 + PyYAML |
| Base de datos | SQLite (archivo local) + `sqlite3` stdlib |
| Scraping estático | httpx + BeautifulSoup4 |
| Scraping dinámico (JS) | Playwright (Chromium) |
| Scheduler | APScheduler BackgroundScheduler |
| CLI | Typer + Rich |
| UI / Dashboard | Streamlit |
| Logging | loguru (rotación 10MB, retención 7 días) |
| Alertas | Telegram Bot API + Webhook genérico |
| Calidad de código | ruff, mypy (strict), pytest, bandit, pip-audit |
| Contenedor | Podman / Docker |

---

## Qué incluye vs qué no incluye

| Incluye ✅ | No incluye ❌ |
|------------|---------------|
| Scraping automático programado (APScheduler) | Hosting en la nube (deployás tú en tu servidor o Streamlit Cloud) |
| Detección de moneda real (£, $, € → GBP, USD, EUR, ARS) | Base de datos remota (solo SQLite local) |
| Alertas por Telegram y webhook | Autenticación OAuth/SSO (solo password opcional en UI) |
| Dashboard Streamlit con historial y gráficos | API REST pública (solo CLI y UI) |
| Contenedor Podman para producción | Soporte multi-tenant (diseñado para un usuario/negocio) |
| 65 tests + CI/CD verde | Migraciones de base de datos (SQLite sin Alembic) |

---

## Inversión vs alternativas: ¿cuánto ahorrás?

| Alternativa | Costo estimado (ARS/año) | Con este servicio |
|-------------|--------------------------|-------------------|
| Herramienta SaaS de monitoreo (suscripción mensual) | $240.000 – $600.000+ | **Pago único por proyecto** (sin cuotas mensuales) |
| Desarrollo desde cero (freelance/agencia) | $500.000 – $1.500.000+ | **Mismo modelo (proyecto), pero más rápido y probado** |
| Seguimiento manual (tu tiempo) | Tu tiempo (horas/semana) | **Automatizado: 0 tiempo diario** |

> **Modelo de cobro:** Un solo pago por proyecto (en ARS), sin suscripciones mensuales. Incluye instalación, configuración de productos, capacitación básica y 1 mes de soporte post-entrega.

---

## Instalación rápida (5 minutos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/ErikLujan/monitor-de-precios.git
cd monitor-de-precios

# 2. Instalar dependencias con uv
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID

# 4. Configurar productos a monitorear
cp products.yaml.example products.yaml
# Editar products.yaml con las URLs de tus competidores

# 5. Inicializar la base de datos
uv run python -m monitor_de_precios.cli.main init-db

# 6. Ejecutar scraping manual
uv run python -m monitor_de_precios.cli.main scrape

# 7. Abrir el dashboard
uv run python -m monitor_de_precios.cli.main serve
# o directamente: uv run streamlit run src/monitor_de_precios/ui/streamlit_app.py
```

## Variables de entorno (`.env`)

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Sí | Token de @BotFather | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Sí | Chat ID destino de alertas | `-1001234567890` |
| `SCRAPE_INTERVAL_HOURS` | No | Intervalo fallback del scheduler | `24` |
| `WEBHOOK_URL` | No | Endpoint genérico POST JSON | `https://hooks.example.com/price` |
| `STREAMLIT_PASSWORD` | No | Contraseña SHA-256 para la UI | `hash_sha256` |
| `LOG_LEVEL` | No | Nivel de logging | `INFO` |
| `GBP_TO_ARS_RATE` | No | Tasa de conversión GBP → ARS | `2047.11` |

> **No uses comillas en los valores. Nunca commitees `.env`.** Está en `.gitignore`.

## products.yaml — Qué productos monitorear

```yaml
products:
  - id: producto-unico
    nombre: "Nombre visible en UI"
    tienda: "Nombre de la competencia"
    url: "https://tienda.com/producto"
    frecuencia_horas: 24
    requiere_js: false          # true si la tienda usa JavaScript (Playwright)
    user_agent: "auto"          # "auto" = rotativo, o string fijo
    headers: {}
    umbral_cambio_porcentaje: 5.0
    umbral_precio_maximo: null
    activo: true
    campos:
      - nombre: precio
        tipo: numero
        selectores: [".precio", "[itemprop='price']"]
        atributo: null
        limpiar: true
      - nombre: titulo
        tipo: texto
        selectores: ["h1.producto"]
        atributo: null
        limpiar: false
```

Ver `products.yaml.example` para ejemplos completos con productos reales de prueba (books.toscrape.com).

## Comandos CLI disponibles

```bash
# Scraping manual de todos los productos activos
uv run python -m monitor_de_precios.cli.main scrape

# Inicializar base de datos SQLite
uv run python -m monitor_de_precios.cli.main init-db

# Listar productos configurados
uv run python -m monitor_de_precios.cli.main list-products

# Probar notificaciones (Telegram + webhook)
uv run python -m monitor_de_precios.cli.main test-notify

# Iniciar dashboard Streamlit
uv run python -m monitor_de_precios.cli.main serve

# Iniciar scheduler (modo producción, jobs periódicos)
uv run python -m monitor_de_precios.cli.main scheduler
```

## Deploy con Podman (producción)

```bash
# Construir imagen
podman compose build

# Levantar servicios en background (scraper + UI)
podman compose up -d

# Ver logs
podman logs -f monitor-de-precios-scraper
podman logs -f monitor-de-precios-ui

# Detener
podman compose down
```

Servicios:
- **scraper**: Ejecuta el scheduler con jobs periódicos por producto.
- **ui**: Expone Streamlit en el puerto 8501.

Volúmenes persistidos:
- `./data:/app/data` → SQLite `precios.db`
- `./logs:/app/logs` → Logs rotativos

## Calidad y verificaciones

```bash
# Sync de dependencias congeladas
uv sync --frozen

# Lint + formato
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Typecheck estricto
uv run mypy --strict src/

# Tests (65 tests)
uv run pytest tests/ -v

# Smoke test CLI
uv run python -m monitor_de_precios.cli.main list-products

# Seguridad
uv run pip-audit
uv run bandit -r src/
```

## Arquitectura del sistema

[aca-va-la-futura-imagen-o-captura]
> **Captura sugerida:** Diagrama de flujo de datos: Scheduler → Scraper (httpx/BS4/Playwright) → SQLite → Analizador (variaciones) → Notificador (Telegram/webhook) → UI Streamlit.

Flujo de datos:
1. **Scheduler** (APScheduler) dispara el scraping cada X horas por producto.
2. **Scraper** (httpx + BS4, o Playwright si requiere JS) extrae precios del HTML.
3. **Base de datos** (SQLite) almacena el historial de precios.
4. **Analizador** detecta variaciones significativas (umbral configurable).
5. **Notificador** envía alerta por Telegram y/o webhook genérico.
6. **UI** (Streamlit) muestra precios recientes, historial y gráficos por producto.

## Solución de problemas (FAQ)

| Problema | Solución probable |
|----------|-------------------|
| `TELEGRAM_BOT_TOKEN` no configurado | Revisá `.env` y reiniciá la app |
| Precio no se detecta | Verificá los selectores CSS en `products.yaml` |
| La UI no carga | Ejecutá `init-db` primero, luego `serve` |
| Error de permisos en `data/precios.db` | Borrá el archivo y volvé a correr `init-db` |
| Scraper falla en sitio con JS | Poné `requiere_js: true` en `products.yaml` |
| Moneda muestra ARS en vez de GBP/£ | Los registros viejos tienen ARS hardcodeado. Borrá la BD y volvé a correr `scrape` |

## Roadmap (próximas mejoras)

- [ ] UI rediseñada: mobile-first, accesibilidad WCAG 2.1 AA
- [ ] Dominio propio + Cloudflare Tunnel para demo profesional
- [ ] UptimeRobot para keep-alive en Streamlit Cloud
- [ ] VPS barato (Hetzner) para separación scraper/UI en producción

## Licencia

Uso libre para fines educativos, portafolio y comercial. Template listo para Workana.

---

## Alcance del servicio (qué incluye el proyecto)

Cuando contratás este servicio, recibís:

- [ ] **Instalación y despliegue** en tu servidor / VPS / Streamlit Cloud
- [ ] **Configuración de productos** (urls, selectores CSS, umbrales de alerta)
- [ ] **Configuración de alertas** (Telegram Bot + webhook opcional)
- [ ] **Capacitación básica** de uso del dashboard (30 min videollamada o video grabado)
- [ ] **1 mes de soporte post-entrega** (ajustes de selectores, dudas de uso)
- [ ] **Documentación técnica** de la instalación para tu equipo

> **No incluye:** Hosting/servidor (corre por tu cuenta), dominio propio, certificado SSL (si usás tu servidor), modificaciones de código a medida (se cotizan aparte).

---

## Contacto y próximos pasos

[aca-va-la-futura-imagen-o-captura]
> **Captura sugerida:** Banner o imagen de cierre con tus datos de contacto o un QR al repositorio.

¿Te interesa este template para tu negocio o proyecto?

**👉 Solicitar presupuesto sin cargo:** Contáctame por Workana con el detalle de qué productos querés monitorear y te paso una cotización en ARS (pago único por proyecto, sin cuotas mensuales).

- **Ver el repositorio:** https://github.com/ErikLujan/monitor-de-precios
- **Clonar y probar:** `git clone https://github.com/ErikLujan/monitor-de-precios.git`
