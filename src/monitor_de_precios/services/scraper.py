import asyncio
import random
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from monitor_de_precios.core.logging import logger
from monitor_de_precios.models.product import ProductConfig, ProductFieldConfig, ScrapedPrice
from monitor_de_precios.services.database import init_db, insert_price

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _get_user_agent(product: ProductConfig) -> str:
    """Obtiene el User-Agent a usar.

    Args:
        product: Configuración del producto

    Returns:
        User-Agent string a utilizar
    """
    if product.user_agent and product.user_agent != "auto":
        return product.user_agent
    return random.choice(USER_AGENTS)  # nosec B311


def _build_headers(product: ProductConfig) -> dict[str, str]:
    """Construye los headers HTTP combinando defaults + custom.

    Args:
        product: Configuración del producto

    Returns:
        Diccionario con headers HTTP
    """
    headers = {
        "User-Agent": _get_user_agent(product),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    headers.update(product.headers)
    return headers


def _check_robots_txt(url: str, client: httpx.Client) -> bool:
    """Verifica robots.txt básico. Retorna True si permitido, False si denegado.

    Args:
        url: URL a verificar
        client: Cliente HTTP a utilizar

    Returns:
        True si permitido, False si denegado
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        resp = client.get(robots_url, timeout=5.0)
        if resp.status_code != 200:
            return True

        content = resp.text
        user_agent_star = False
        for line in content.splitlines():
            line = line.strip()
            if line.lower().startswith("user-agent:"):
                user_agent_star = "*" in line.split(":", 1)[1].strip()
            elif line.lower().startswith("disallow:") and user_agent_star:
                path = line.split(":", 1)[1].strip()
                if path and path != "/":
                    if urlparse(url).path.startswith(path):
                        logger.warning(f"robots.txt deniega acceso a {url} (Disallow: {path})")
                        return False
        return True
    except Exception as e:
        logger.debug(f"No se pudo verificar robots.txt para {url}: {e}")
        return True


def _detect_currency(raw_text: str) -> str:
    """Detecta moneda ISO a partir del símbolo monetario en el texto crudo.

    Args:
        raw_text: Texto crudo del precio (ej. "£51.77", "$100.00", "€45,99")

    Returns:
        Código ISO de moneda: GBP, EUR, ARS (por defecto para $ y sin símbolo)
    """
    if "£" in raw_text:
        return "GBP"
    if "€" in raw_text:
        return "EUR"
    return "ARS"


def _clean_price_text(text: str) -> float | None:
    """Limpia texto de precio y lo convierte a float.

    Args:
        text: Texto crudo del precio

    Returns:
        Precio como float o None si no se puede parsear
    """
    cleaned = re.sub(r"[^\d.,]", "", text)
    if cleaned.count(",") > 0 and cleaned.count(".") > 0:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif cleaned.count(",") > 0:
        if len(cleaned.split(",")[-1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif cleaned.count(".") > 0:
        parts = cleaned.split(".")
        if len(parts[-1]) == 3 and len(parts) > 1:
            cleaned = cleaned.replace(".", "")
        elif len(parts[-1]) == 2:
            pass
        else:
            cleaned = cleaned.replace(".", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_with_fallback(soup: BeautifulSoup, campo: ProductFieldConfig) -> str | float | None:
    """Extrae un campo de un objeto BeautifulSoup usando selectores CSS con fallback.

    Args:
        soup: Objeto BeautifulSoup parseado
        campo: Configuración del campo a extraer

    Returns:
        Valor extraído (str, float o None si no se encuentra)
    """
    for selector in campo.selectores:
        elements = soup.select(selector)
        if not elements:
            continue

        for el in elements:
            if campo.atributo:
                value = el.get(campo.atributo)
            else:
                value = el.get_text(strip=True)

            if value:
                if isinstance(value, list):
                    value = " ".join(str(v) for v in value)
                value = str(value)

                if campo.tipo == "numero" and campo.limpiar:
                    num = _clean_price_text(value)
                    if num is not None:
                        return num
                elif campo.tipo == "numero" and not campo.limpiar:
                    try:
                        return float(value)
                    except ValueError:
                        pass
                elif campo.tipo == "texto":
                    return value.strip()

    return None


def _extract_field(html: str, field: ProductFieldConfig) -> Any:
    """Extrae un campo del HTML usando selectores CSS.

    Args:
        html: HTML crudo a parsear
        field: Configuración del campo a extraer

    Returns:
        Valor extraído (str, float o None si no se encuentra)
    """
    soup = BeautifulSoup(html, "html.parser")

    for selector in field.selectores:
        elements = soup.select(selector)
        if not elements:
            continue

        for el in elements:
            if field.atributo:
                value = el.get(field.atributo)
            else:
                value = el.get_text(strip=True)

            if value:
                if isinstance(value, list):
                    value = " ".join(str(v) for v in value)
                value = str(value)

                if field.tipo == "numero" and field.limpiar:
                    num = _clean_price_text(value)
                    if num is not None:
                        return num
                elif field.tipo == "numero" and not field.limpiar:
                    try:
                        return float(value)
                    except ValueError:
                        pass
                elif field.tipo == "texto":
                    return value.strip()

    return None


def _scrape_static(product: ProductConfig) -> str:
    """Scrapeo estático con httpx + BeautifulSoup."""

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=8),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(
            (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError)
        ),
        reraise=True,
    )
    def _fetch() -> str:
        headers = _build_headers(product)
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            _check_robots_txt(str(product.url), client)

            resp = client.get(str(product.url), headers=headers)
            resp.raise_for_status()

            final_url = str(resp.url)
            html_len = len(resp.text)
            html_preview = resp.text[:200].replace("\n", " ").replace("\r", " ")
            logger.debug(
                f"HTTP {resp.status_code} | URL final: {final_url} | "
                f"Len: {html_len} | Preview: {html_preview}..."
            )

            return resp.text

    return _fetch()


async def _scrape_js(product: ProductConfig) -> str:
    """Scrapeo con JavaScript usando Playwright.

    Args:
        product: Configuración del producto a scrapeear

    Returns:
        HTML renderizado del producto

    Raises:
        RuntimeError: Si Playwright no está instalado
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError("Playwright no instalado. Ejecuta: playwright install chromium") from e

    headers = _build_headers(product)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                user_agent=headers["User-Agent"],
                extra_http_headers={k: v for k, v in headers.items() if k != "User-Agent"},
            )
            page = await context.new_page()
            await page.goto(str(product.url), wait_until="networkidle", timeout=60000)
            content = await page.content()
            return content
        finally:
            await browser.close()


def scrape_product(product: ProductConfig) -> ScrapedPrice:
    """Extrae datos de un producto según su configuración.

    Args:
        product: Configuración del producto a scrapeear

    Returns:
        ScrapedPrice con los datos extraídos

    Raises:
        ValueError: Si no se puede extraer el precio (campo obligatorio)
        RuntimeError: Si requiere_js=True pero Playwright falla
    """
    logger.info(f"Scrapeando: {product.nombre} ({product.tienda}) - {product.url}")

    init_db()

    if product.requiere_js:
        html = asyncio.run(_scrape_js(product))
    else:
        html = _scrape_static(product)

    soup = BeautifulSoup(html, "html.parser")

    extracted = {}
    moneda_detectada = "ARS"
    for field in product.campos:
        value = extract_with_fallback(soup, field)
        if value is not None:
            extracted[field.nombre] = value
            logger.debug(f"  Campo '{field.nombre}': {value}")
            # Detectar moneda del precio a partir del texto crudo del HTML
            if field.nombre == "precio" and moneda_detectada == "ARS":
                for selector in field.selectores:
                    elements = soup.select(selector)
                    if elements:
                        raw_text = (
                            elements[0].get(field.atributo)
                            if field.atributo
                            else elements[0].get_text(strip=True)
                        )
                        if raw_text:
                            moneda_detectada = _detect_currency(str(raw_text))
                        break
        else:
            logger.warning(
                f"  Campo '{field.nombre}' no encontrado con selectores: {field.selectores}"
            )

    precio = extracted.get("precio")
    if precio is None:
        for field in product.campos:
            if field.tipo == "numero" and field.nombre in extracted:
                precio = extracted[field.nombre]
                break

    if precio is None:
        raise ValueError(f"No se pudo extraer precio para {product.nombre} ({product.url})")

    scraped = ScrapedPrice(
        producto=product.nombre,
        tienda=product.tienda,
        precio=float(precio),
        moneda=moneda_detectada,
        fecha=datetime.now(UTC),
        url=str(product.url),
    )

    insert_price(scraped)
    logger.info(f"  Precio insertado en BD: ${scraped.precio:,.2f} {scraped.moneda}")

    return scraped
