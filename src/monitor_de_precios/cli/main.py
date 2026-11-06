"""CLI principal con Typer: scrape, serve, init-db, test-notify, list-products, scheduler."""

import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from monitor_de_precios.core.config import get_settings, load_products
from monitor_de_precios.core.logging import logger, setup_logging
from monitor_de_precios.models.product import ProductConfig
from monitor_de_precios.services.database import init_db
from monitor_de_precios.services.notifier import enviar_alerta_telegram, enviar_webhook
from monitor_de_precios.services.scheduler import start_scheduler
from monitor_de_precios.services.scraper import scrape_product

app = typer.Typer(
    name="monitor-de-precios",
    help="Monitor de precios para e-commerce/PyMEs",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _setup_logging_and_load_products() -> list[ProductConfig]:
    """Helper: setup logging y carga productos."""
    settings = get_settings()
    setup_logging(settings.log_level)
    products = load_products(Path("products.yaml"))
    return products


@app.command()
def scrape() -> None:
    """Ejecuta un ciclo de scraping para todos los productos activos."""
    settings = get_settings()
    setup_logging(settings.log_level)
    products = load_products(Path("products.yaml"))

    active = [p for p in products if p.activo]
    if not active:
        console.print("[yellow]No hay productos activos para scrapeear[/yellow]")
        return

    console.print(f"[cyan]Scrapeando {len(active)} producto(s)...[/cyan]")
    for product in active:
        try:
            result = scrape_product(product)
            console.print(
                f"  + [green]{result.producto}[/green] ({result.tienda}): ${result.precio:,.2f} {result.moneda}"
            )
        except Exception as e:
            console.print(f"  - [red]{product.nombre}[/red]: {e}")
            logger.error(f"Error scrapeando {product.nombre}: {e}")


@app.command()
def serve(
    port: Annotated[int, typer.Option(help="Puerto para Streamlit")] = 8501,
    host: Annotated[str, typer.Option(help="Host para Streamlit")] = "0.0.0.0",
) -> None:
    """Inicia la interfaz web Streamlit."""
    settings = get_settings()
    setup_logging(settings.log_level)
    console.print(f"[cyan]Iniciando Streamlit en http://{host}:{port}[/cyan]")
    subprocess.run(
        [
            "streamlit",
            "run",
            "src/ui/streamlit_app.py",
            "--server.port",
            str(port),
            "--server.address",
            host,
        ]
    )


@app.command("init-db")
def init_db_cmd() -> None:
    """Inicializa la base de datos SQLite."""
    settings = get_settings()
    setup_logging(settings.log_level)
    init_db()
    console.print("[green]Base de datos inicializada correctamente[/green]")


@app.command("test-notify")
def test_notify() -> None:
    """Envía mensaje de prueba a Telegram y webhook."""
    settings = get_settings()
    setup_logging(settings.log_level)

    mensaje = "🧪 <b>Test de notificación</b>\nMonitor de precios funcionando correctamente."
    console.print("[cyan]Enviando test a Telegram...[/cyan]")
    ok_tg = enviar_alerta_telegram(mensaje)
    console.print(f"  Telegram: {'[green]OK[/green]' if ok_tg else '[red]FAIL[/red]'}")

    console.print("[cyan]Enviando test a webhook...[/cyan]")
    ok_wh = enviar_webhook({"event": "test", "message": "Monitor de precios test"})
    console.print(f"  Webhook: {'[green]OK[/green]' if ok_wh else '[yellow]SKIP/FAIL[/yellow]'}")


@app.command("list-products")
def list_products() -> None:
    """Lista los productos configurados en products.yaml."""
    settings = get_settings()
    setup_logging(settings.log_level)
    products = load_products(Path("products.yaml"))

    if not products:
        console.print("[yellow]No hay productos configurados[/yellow]")
        return

    table = Table(title="Productos configurados")
    table.add_column("ID", style="cyan")
    table.add_column("Nombre")
    table.add_column("Tienda")
    table.add_column("URL")
    table.add_column("Frecuencia (h)", justify="right")
    table.add_column("JS", justify="center")
    table.add_column("Activo", justify="center")

    for p in products:
        table.add_row(
            p.id,
            p.nombre,
            p.tienda,
            str(p.url),
            str(p.frecuencia_horas),
            "Y" if p.requiere_js else "N",
            "Y" if p.activo else "N",
        )

    console.print(table)


@app.command()
def scheduler() -> None:
    """Inicia el scheduler en background (bloquea hasta SIGINT/SIGTERM)."""
    start_scheduler()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[bool, typer.Option("--version", "-v", help="Muestra la versión")] = False,
) -> None:
    """Monitor de precios - CLI principal."""
    if version:
        from monitor_de_precios import __version__

        console.print(f"monitor-de-precios v{__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
