# Monitor de Precios de la Competencia, con Alertas Automáticas

**Enterate cuando la competencia cambia sus precios, sin revisar páginas a mano.** Un sistema que vigila los productos que le indiques, guarda el historial y te avisa por Telegram apenas hay una variación importante.

[![CI](https://img.shields.io/github/actions/workflow/status/ErikLujan/monitor-de-precios/ci.yml?label=CI&branch=main)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/ci.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/ErikLujan/monitor-de-precios/cd.yml?label=CD&branch=main)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/cd.yml)
[![Daily Scraper](https://img.shields.io/github/actions/workflow/status/ErikLujan/monitor-de-precios/scraper.yml?label=Scraper)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/scraper.yml)
[![Tests: 65 passing](https://img.shields.io/badge/tests-65%20passing-brightgreen)](https://github.com/ErikLujan/monitor-de-precios/actions/workflows/ci.yml)
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

> **¿Querés algo así para tu negocio?** Contactame por Workana contándome qué productos o tiendas querés seguir y te paso un presupuesto sin cargo. [Ir a la sección de contacto](#contacto-y-próximos-pasos).

## Contenido

- [El problema que resuelve](#el-problema-que-resuelve)
- [Cómo funciona](#cómo-funciona)
- [Avisos en tu celular](#avisos-en-tu-celular)
- [Para quién es](#para-quién-es)
- [Qué podés monitorear](#qué-podés-monitorear)
- [Qué incluye y qué no](#qué-incluye-y-qué-no)
- [Qué recibís al contratarlo](#qué-recibís-al-contratarlo)
- [Inversión vs alternativas](#inversión-vs-alternativas)
- [Preguntas frecuentes](#preguntas-frecuentes)
- [Contacto y próximos pasos](#contacto-y-próximos-pasos)
- [Documentación técnica](#documentación-técnica)
- [Licencia](#licencia)

## El problema que resuelve

Si vendés online o revendés productos, sabés lo que cuesta estar pendiente de los precios de la competencia: abrir páginas una por una, anotar en una planilla, y aun así enterarte tarde de que alguien bajó el precio o se quedó sin stock.

Este sistema hace ese trabajo por vos, todos los días y sin intervención:

- Revisa automáticamente las páginas que le indiques.
- Guarda el historial de cada producto para que veas cómo evolucionó el precio.
- Te avisa por **Telegram** (o a otro sistema, por webhook) cuando el cambio supera el porcentaje que definas.
- Todo se ve en un **dashboard web** simple, también desde el celular.

Además, no hay cuotas mensuales de software: se contrata una sola vez como proyecto.

## Cómo funciona

<img width="1692" height="215" alt="Diagrama" src="https://github.com/user-attachments/assets/ef882ded-18af-43c0-93dc-b91bae13e7a8" />

1. **Programación:** el sistema revisa cada producto con la frecuencia que elijas (por ejemplo, una vez por día).
2. **Lectura de precios:** entra a la página del producto y extrae precio, título y disponibilidad. También funciona con tiendas que cargan su contenido con JavaScript.
3. **Historial:** cada lectura queda guardada para ver la evolución en el tiempo.
4. **Análisis:** compara con la lectura anterior y detecta variaciones significativas según el umbral que definas.
5. **Aviso:** si hay un cambio relevante, te llega una alerta por Telegram y/o webhook.
6. **Dashboard:** podés ver precios actuales, historial y gráficos por producto cuando quieras.

## Avisos en tu celular

<table align="center">
  <tr>
    <th>Notificación móvil</th>
    <th>Mensaje en chat</th>
  </tr>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/3a6e8de7-c591-46e8-b922-b041b16821ce" width="300" alt="Mobile Notification"/>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/af7d158c-c619-46a1-abf1-8b842f95462d" width="300" alt="Telegram Message"/>
    </td>
  </tr>
</table>

Las alertas llegan como un mensaje de Telegram: te enterás en el momento, sin tener que abrir el dashboard.

## Para quién es

| Si sos... | Qué obtenés |
|-----------|-------------|
| **Dueño de PyME o e-commerce** | Control de precios de la competencia sin suscripciones mensuales. Alertas automáticas cuando suben o bajan. Un dashboard visual para decidir cuándo ajustar tus precios. |
| **Revendedor o comerciante** | Sabés cuándo conviene comprar stock o lanzar una promoción, según cómo se mueve el mercado. |
| **Equipo que ya tiene sistemas propios** | Las alertas pueden enviarse por webhook para integrarse con lo que ya usás. |

## Qué podés monitorear

| Caso de uso | Qué se sigue | Valor para tu negocio |
|-------------|--------------|-----------------------|
| **Precio de un producto en una tienda online** | Precio, disponibilidad, título, stock | Detectás cuando la competencia baja el precio y ajustás tu margen |
| **Variación de precio en un marketplace** | Historial de precios, alertas por % de cambio | Sabés cuándo comprar stock o cuándo lanzar una promo |
| **Disponibilidad de stock crítico** | Con stock / sin stock | Evitás quiebres en tus productos estrella |
| **Insumos importados y tipo de cambio** | Precio de insumos, cotizaciones | Planificás costos y márgenes en productos importados |

## Qué incluye y qué no

| Incluye ✅ | No incluye ❌ |
|------------|---------------|
| Revisión automática y programada de precios | Hosting en la nube (se instala en tu servidor o en Streamlit Cloud) |
| Reconocimiento de la moneda (pesos, dólares, euros, libras) | Base de datos remota (los datos se guardan en un archivo local) |
| Alertas por Telegram y webhook | Inicio de sesión corporativo (solo contraseña opcional en el dashboard) |
| Dashboard con historial y gráficos | API pública para terceros (se usa por dashboard o línea de comandos) |
| Instalación lista para producción en contenedores | Varios negocios en una misma instalación (una instalación por negocio) |
| 65 tests automáticos y verificación continua | |

## Qué recibís al contratarlo

- **Instalación y puesta en marcha** en tu servidor, VPS o Streamlit Cloud.
- **Configuración de tus productos** (URLs, qué dato leer de cada página y umbrales de alerta).
- **Configuración de las alertas** (bot de Telegram y webhook opcional).
- **Capacitación básica** de uso del dashboard (30 minutos por videollamada o en video grabado).
- **1 mes de soporte posterior a la entrega** (ajustes y dudas de uso).
- **Documentación de la instalación** para tu equipo.

> **No incluye:** hosting o servidor (corre por tu cuenta), dominio propio, certificado SSL (si usás tu propio servidor) ni modificaciones de código a medida (se cotizan aparte).

## Inversión vs alternativas

| Alternativa | Costo estimado (ARS/año) | Con este servicio |
|-------------|--------------------------|-------------------|
| Herramienta SaaS de monitoreo (suscripción mensual) | $240.000 – $600.000+ | **Pago único por proyecto** (sin cuotas mensuales) |
| Desarrollo desde cero (freelance/agencia) | $500.000 – $1.500.000+ | **Mismo modelo (proyecto), pero más rápido y probado** |
| Seguimiento manual (tu tiempo) | Horas por semana | **Automatizado: 0 tiempo diario** |

> **Modelo de cobro:** un solo pago por proyecto (en ARS), sin suscripciones mensuales. Incluye instalación, configuración de productos, capacitación básica y 1 mes de soporte posterior a la entrega. Los costos de la tabla son estimaciones de referencia.

## Preguntas frecuentes

**¿Necesito saber programar para usarlo?**
No. Yo hago la instalación y la configuración inicial, y el uso diario es mirar el dashboard y recibir los avisos en Telegram.

**¿Funciona con cualquier tienda?**
Funciona con la mayoría de las páginas públicas, incluidas las que cargan con JavaScript. Algunas tiendas tienen protecciones especiales; antes de empezar reviso las que te interesan y te confirmo si es viable.

**¿Cada cuánto revisa los precios?**
Lo definís vos, producto por producto (por ejemplo, cada 24 horas).

**¿Cuánto tarda en estar funcionando?**
Depende de la cantidad de productos y del lugar donde se instale. Te doy un plazo concreto en el presupuesto.

**¿Puedo agregar o quitar productos después?**
Sí, y durante el primer mes de soporte te ayudo a hacerlo.

**¿Mis datos quedan en un servicio de terceros?**
No. El historial se guarda en un archivo en el servidor donde se instala el sistema, que es tuyo.

## Contacto y próximos pasos

<img width="1983" height="793" alt="image" src="https://github.com/user-attachments/assets/c887e81c-90fd-4ab9-a10d-c57797078d52" />

¿Te interesa para tu negocio?

**👉 Solicitá un presupuesto sin cargo:** contactame por Workana con el detalle de qué productos o tiendas querés monitorear y te paso una cotización en ARS (pago único por proyecto, sin cuotas mensuales).

- **Ver el repositorio:** https://github.com/ErikLujan/monitor-de-precios
- **Demo en vivo:** https://monitor-de-precios.streamlit.app/

---

## Documentación técnica

Esta parte es para desarrolladores o para el equipo técnico que quiera revisar el proyecto en detalle.

### Calidad del código

Tipado estricto (`mypy --strict`), 65 tests automáticos, integración y despliegue continuos en GitHub Actions y auditoría de seguridad (`bandit` + `pip-audit`).

### Stack tecnológico

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

### Flujo de datos

1. **Scheduler** (APScheduler) dispara el scraping cada X horas por producto.
2. **Scraper** (httpx + BS4, o Playwright si requiere JS) extrae precios del HTML.
3. **Base de datos** (SQLite) almacena el historial de precios.
4. **Analizador** detecta variaciones significativas (umbral configurable).
5. **Notificador** envía alerta por Telegram y/o webhook genérico.
6. **UI** (Streamlit) muestra precios recientes, historial y gráficos por producto.

<details>
<summary><strong>Instalación rápida (5 minutos)</strong></summary>

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

</details>

<details>
<summary><strong>Variables de entorno (<code>.env</code>)</strong></summary>

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

</details>

<details>
<summary><strong>products.yaml: qué productos monitorear</strong></summary>

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

Ver `products.yaml.example` para ejemplos completos con productos de prueba (books.toscrape.com).

</details>

<details>
<summary><strong>Comandos CLI disponibles</strong></summary>

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

</details>

<details>
<summary><strong>Deploy con Podman (producción)</strong></summary>

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
- **scraper**: ejecuta el scheduler con jobs periódicos por producto.
- **ui**: expone Streamlit en el puerto 8501.

Volúmenes persistidos:
- `./data:/app/data` → SQLite `precios.db`
- `./logs:/app/logs` → Logs rotativos

</details>

<details>
<summary><strong>Calidad y verificaciones</strong></summary>

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

</details>

<details>
<summary><strong>Solución de problemas (FAQ técnico)</strong></summary>

| Problema | Solución probable |
|----------|-------------------|
| `TELEGRAM_BOT_TOKEN` no configurado | Revisá `.env` y reiniciá la app |
| Precio no se detecta | Verificá los selectores CSS en `products.yaml` |
| La UI no carga | Ejecutá `init-db` primero, luego `serve` |
| Error de permisos en `data/precios.db` | Borrá el archivo y volvé a correr `init-db` |
| Scraper falla en sitio con JS | Poné `requiere_js: true` en `products.yaml` |
| Moneda muestra ARS en vez de GBP/£ | Los registros viejos tienen ARS hardcodeado. Borrá la BD y volvé a correr `scrape` |

</details>

<details>
<summary><strong>Roadmap (próximas mejoras)</strong></summary>

- [ ] UI rediseñada: mobile-first, accesibilidad WCAG 2.1 AA
- [ ] Dominio propio + Cloudflare Tunnel para demo profesional
- [ ] UptimeRobot para keep-alive en Streamlit Cloud
- [ ] VPS barato (Hetzner) para separación scraper/UI en producción

</details>

## Licencia

© 2026 Erik Luján. Código público para que puedas evaluar el proyecto. Para implementarlo en tu negocio o usarlo comercialmente, contactame.
