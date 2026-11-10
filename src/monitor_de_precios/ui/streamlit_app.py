"""Dashboard Streamlit para monitor-de-precios."""

import hashlib
from datetime import datetime
from typing import Any

import streamlit as st

from monitor_de_precios.core.config import get_settings
from monitor_de_precios.services.database import get_price_history, get_recent_prices


def _check_password() -> bool:
    """Verifica contraseña si STREAMLIT_PASSWORD está configurado."""
    settings = get_settings()
    if not settings.streamlit_password:
        return True

    expected_hash = hashlib.sha256(settings.streamlit_password.encode()).hexdigest()

    password = st.text_input("🔐 Contraseña", type="password", key="streamlit_password")
    if not password:
        st.stop()

    input_hash = hashlib.sha256(password.encode()).hexdigest()
    if input_hash != expected_hash:
        st.error("Contraseña incorrecta")
        st.stop()

    return True


def _format_fecha(fecha_str: str) -> str:
    """Formatea fecha ISO a formato legible."""
    try:
        dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return fecha_str


def _render_price_table(prices: list[dict[str, Any]]) -> None:
    """Renderiza tabla de precios recientes."""
    if not prices:
        st.info("📭 No hay precios registrados aún. Ejecutá el scraper para cargar datos.")
        return

    rows = []
    for p in prices:
        rows.append(
            {
                "Producto": p["producto"],
                "Tienda": p["tienda"],
                "Precio": f"${p['precio']:,.2f} {p['moneda']}",
                "Fecha": _format_fecha(p["fecha"]),
                "URL": p["url"] or "-",
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn("URL", display_text="Abrir"),
        },
    )


def main() -> None:
    st.set_page_config(
        page_title="Monitor de Precios",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    from monitor_de_precios.services.database import init_db

    init_db()

    _check_password()

    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📊 Monitor de Precios")
        st.caption("Seguimiento de precios de competencia con alertas automáticas")
    with col2:
        if st.button("🔄 Actualizar ahora", use_container_width=True):
            st.rerun()

    with st.sidebar:
        settings = get_settings()
        st.header("⚙️ Configuración")
        st.metric("Intervalo scrapeo", f"{settings.scrape_interval_hours}h")
        st.metric("Log level", settings.log_level)

        st.divider()
        st.header("📈 Acciones")
        if st.button("🧪 Test notificación", use_container_width=True):
            st.toast("Enviando test...", icon="🧪")

        st.divider()
        st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

    tab1, tab2 = st.tabs(["📋 Precios recientes", "📊 Historial por producto"])

    with tab1:
        st.subheader("Últimos 200 precios registrados")

        st.empty()
        prices = get_recent_prices(200)
        _render_price_table(prices)

        try:
            from importlib import import_module

            st_autorefresh = import_module("streamlit_autorefresh").st_autorefresh
            st_autorefresh(interval=60_000, key="price_refresh")
        except ImportError:
            pass

    with tab2:
        st.subheader("Historial de precios (últimos 30 días)")

        prices_all = get_recent_prices(500)
        if not prices_all:
            st.info("No hay datos para mostrar historial.")
        else:
            productos_unicos = sorted({p["producto"] for p in prices_all})
            producto_sel = st.selectbox("Seleccionar producto", productos_unicos)

            if producto_sel:
                history = get_price_history(producto_sel, days=30)
                if history:
                    import pandas as pd

                    df = pd.DataFrame(history)
                    df["fecha"] = pd.to_datetime(df["fecha"])
                    df = df.sort_values("fecha")

                    st.line_chart(df.set_index("fecha")["precio"])

                    st.dataframe(
                        [
                            {
                                "Tienda": h["tienda"],
                                "Precio": f"${h['precio']:,.2f} {h['moneda']}",
                                "Fecha": _format_fecha(h["fecha"]),
                                "URL": h["url"] or "-",
                            }
                            for h in history
                        ],
                        use_container_width=True,
                        hide_index=True,
                        column_config={"URL": st.column_config.LinkColumn("URL")},
                    )
                else:
                    st.info(f"No hay historial para {producto_sel} en los últimos 30 días.")


if __name__ == "__main__":
    main()
