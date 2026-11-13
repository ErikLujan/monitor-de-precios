"""Dashboard Streamlit para monitor-de-precios.

UI profesional, accesible (WCAG 2.1 AA) y responsive (mobile-first).
Sin frameworks CSS externos, sin emojis decorativos.
"""

import hashlib
from datetime import datetime
from typing import Any, Literal

import pandas as pd
import streamlit as st

from monitor_de_precios.core.config import Settings, get_settings
from monitor_de_precios.services.database import get_price_history, get_recent_prices, init_db

# ── Constantes de configuración ──────────────────────────────────────────────
PAGE_TITLE = "Monitor de Precios"
PAGE_ICON = "📊"  # Único emoji: favicon del navegador
LAYOUT: Literal["wide"] = "wide"
SIDEBAR_STATE: Literal["expanded"] = "expanded"

MAX_RECENT_ROWS = 200
MAX_HISTORY_ROWS = 500
HISTORY_DAYS = 30
PAGINATION_THRESHOLD = 50
AUTO_REFRESH_INTERVAL_MS = 60_000

# Paleta de colores (CSS variables)
CSS_STYLES = """
<style>
:root {
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-light: #dbeafe;
  --color-success: #059669;
  --color-warning: #d97706;
  --color-error: #dc2626;
  --color-bg: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;
  --color-text: #1e293b;
  --color-text-secondary: #475569;
  --color-text-muted: #94a3b8;
  --color-border: #e2e8f0;
  --color-focus: #2563eb;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace;
}

/* Reset y base */
.main .block-container {
  padding-top: var(--space-lg);
  padding-bottom: var(--space-xl);
  max-width: 1200px;
}

/* Tipografía */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-sans);
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-text);
  margin-top: 0;
}

h1 { font-size: 1.875rem; margin-bottom: var(--space-xs); }
h2 { font-size: 1.5rem; margin-bottom: var(--space-sm); }
h3 { font-size: 1.25rem; margin-bottom: var(--space-sm); }

p, span, label, div { font-family: var(--font-sans); color: var(--color-text); }
small, .caption { font-size: 0.875rem; color: var(--color-text-secondary); }
.muted { color: var(--color-text-muted); }

/* Botones */
.stButton > button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
  font-weight: 500;
  font-size: 0.875rem;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: background-color var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast);
  min-height: 40px;
}

.stButton > button:hover {
  background-color: var(--color-primary-hover);
  box-shadow: var(--shadow-md);
}

.stButton > button:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.stButton > button:active {
  transform: scale(0.98);
}

.stButton > button[kind="secondary"] {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.stButton > button[kind="secondary"]:hover {
  background-color: var(--color-border);
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  padding: var(--space-sm) var(--space-md) !important;
  font-size: 0.875rem !important;
  font-family: var(--font-sans) !important;
  background-color: var(--color-bg) !important;
  color: var(--color-text) !important;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast) !important;
  min-height: 40px;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
  border-color: var(--color-focus) !important;
  box-shadow: 0 0 0 3px var(--color-primary-light) !important;
  outline: none !important;
}

.stTextInput > label,
.stSelectbox > label {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: var(--space-xs);
  display: block;
}

/* Tarjetas / contenedores */
.metric-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal);
}

.metric-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  font-family: var(--font-mono);
}

.metric-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin-bottom: var(--space-xs);
}

/* Tabla responsive */
.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
}

.table-wrapper table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.table-wrapper th,
.table-wrapper td {
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.875rem;
  white-space: nowrap;
}

.table-wrapper th {
  background: var(--color-bg-secondary);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.75rem;
  position: sticky;
  top: 0;
  z-index: 1;
}

.table-wrapper tr:last-child td {
  border-bottom: none;
}

.table-wrapper tr:hover td {
  background: var(--color-bg-secondary);
}

/* Estados vacíos */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl) var(--space-md);
  text-align: center;
  background: var(--color-bg-secondary);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
  min-height: 200px;
}

.empty-state-icon {
  font-size: 3rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
  opacity: 0.5;
}

.empty-state-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-xs);
}

.empty-state-message {
  color: var(--color-text-secondary);
  margin-bottom: var(--space-lg);
  max-width: 300px;
}

/* Skeletons */
.skeleton {
  background: linear-gradient(90deg, var(--color-bg-tertiary) 25%, var(--color-border) 50%, var(--color-bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1.5fr 2fr;
  gap: var(--space-md);
  padding: var(--space-sm) 0;
}

.skeleton-cell { height: 1rem; }

/* Badges / chips */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.badge-success { background: #d1fae5; color: var(--color-success); }
.badge-warning { background: #fef3c7; color: var(--color-warning); }
.badge-error { background: #fee2e2; color: var(--color-error); }
.badge-info { background: var(--color-primary-light); color: var(--color-primary); }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
}

section[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  justify-content: flex-start;
  text-align: left;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: var(--space-xs);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--space-xs);
}

.stTabs [data-baseweb="tab"] {
  background: transparent;
  border: none;
  padding: var(--space-sm) var(--space-md);
  font-weight: 500;
  color: var(--color-text-secondary);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  transition: color var(--transition-fast), background var(--transition-fast);
}

.stTabs [data-baseweb="tab"]:hover {
  color: var(--color-text);
  background: var(--color-bg-tertiary);
}

.stTabs [aria-selected="true"] {
  color: var(--color-primary) !important;
  background: var(--color-primary-light) !important;
  border-bottom: 2px solid var(--color-primary);
}

/* Toast notifications */
.stToast {
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}

/* Responsive: mobile-first */
@media (max-width: 640px) {
  .main .block-container {
    padding-left: var(--space-sm);
    padding-right: var(--space-sm);
  }

  h1 { font-size: 1.5rem; }
  h2 { font-size: 1.25rem; }
  h3 { font-size: 1.125rem; }

  .metric-card { padding: var(--space-sm); }
  .metric-value { font-size: 1.25rem; }

  .table-wrapper {
    border: none;
    border-radius: 0;
    margin: calc(-1 * var(--space-sm));
    padding: var(--space-sm);
  }

  .stTabs [data-baseweb="tab"] {
    padding: var(--space-sm) var(--space-sm);
    font-size: 0.875rem;
  }
}

/* Focus visible global para accesibilidad */
*:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

/* Reducir movimiento para usuarios que lo prefieren */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --color-border: #000;
    --color-text-secondary: #000;
    --color-primary: #0000ee;
  }
}
</style>
"""


# ── Funciones de utilidad ────────────────────────────────────────────────────


def _check_password() -> bool:
    """Verifica contraseña si STREAMLIT_PASSWORD está configurado.

    Returns:
        True si la contraseña es correcta o no está configurada.
    """
    settings = get_settings()
    if not settings.streamlit_password:
        return True

    expected_hash = hashlib.sha256(settings.streamlit_password.encode()).hexdigest()

    # Label asociado para accesibilidad
    password = st.text_input(
        "Contraseña",
        type="password",
        key="streamlit_password",
        placeholder="Introduce la contraseña",
        label_visibility="visible",
    )

    if not password:
        st.stop()

    input_hash = hashlib.sha256(password.encode()).hexdigest()
    if input_hash != expected_hash:
        st.error("Contraseña incorrecta", icon="⚠")
        st.stop()

    return True


def _format_fecha(fecha_str: str) -> str:
    """Formatea fecha ISO a formato legible DD/MM/YYYY HH:MM."""
    try:
        dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return fecha_str


def _format_price(precio: float, moneda: str, settings: Settings | None = None) -> str:
    """Formatea precio con símbolo monetario y código ISO.

    Args:
        precio: Valor numérico del precio.
        moneda: Código ISO de moneda (ARS, USD, EUR, GBP).
        settings: Configuración opcional para tasa de conversión a ARS.

    Returns:
        Precio formateado con símbolo e ISO, ej. "£51.77 GBP".
    """
    symbol_map = {"GBP": "£", "USD": "$", "EUR": "€", "ARS": "$"}
    symbol = symbol_map.get(moneda, "$")
    resultado = f"{symbol}{precio:,.2f} {moneda}"

    if settings and moneda != "ARS" and settings.gbp_to_ars_rate > 0:
        if moneda == "GBP":
            precio_ars = precio * settings.gbp_to_ars_rate
            resultado += f" (≈ ${precio_ars:,.2f} ARS)"

    return resultado


def _render_skeleton_rows(count: int = 5) -> None:
    """Renderiza filas skeleton para estado de carga."""
    skeleton_html = '<div class="table-wrapper"><div class="skeleton-row" style="display:grid;grid-template-columns:2fr 1.5fr 1fr 1.5fr 2fr;gap:16px;padding:8px 0;">'
    for _ in range(count):
        skeleton_html += (
            '<div class="skeleton skeleton-cell" style="height:1rem;"></div>'
            '<div class="skeleton skeleton-cell" style="height:1rem;"></div>'
            '<div class="skeleton skeleton-cell" style="height:1rem;"></div>'
            '<div class="skeleton skeleton-cell" style="height:1rem;"></div>'
            '<div class="skeleton skeleton-cell" style="height:1rem;"></div>'
        )
    skeleton_html += "</div></div>"
    st.markdown(skeleton_html, unsafe_allow_html=True)


def _render_empty_state(
    title: str, message: str, action_label: str | None = None, action_key: str | None = None
) -> None:
    """Renderiza un estado vacío accesible con acción opcional."""
    empty_html = f"""
    <div class="empty-state" role="status" aria-live="polite">
      <div class="empty-state-icon" aria-hidden="true">📭</div>
      <h3 class="empty-state-title">{title}</h3>
      <p class="empty-state-message">{message}</p>
    </div>
    """
    st.markdown(empty_html, unsafe_allow_html=True)

    if action_label and action_key:
        if st.button(action_label, key=action_key, use_container_width=True):
            st.rerun()


def _render_price_table(prices: list[dict[str, Any]], show_pagination: bool = False) -> None:
    """Renderiza tabla de precios accesible y responsive.

    Args:
        prices: Lista de diccionarios con datos de precios.
        show_pagination: Si True, muestra controles de paginación para >50 filas.
    """
    if not prices:
        _render_empty_state(
            "Sin datos de precios",
            "No hay precios registrados aún. Ejecuta el scraper para cargar datos.",
            "Actualizar",
            "refresh_empty",
        )
        return

    # Preparar DataFrame
    rows = []
    settings = get_settings()
    for p in prices:
        rows.append(
            {
                "Producto": p["producto"],
                "Tienda": p["tienda"],
                "Precio": _format_price(p["precio"], p["moneda"], settings),
                "Fecha": _format_fecha(p["fecha"]),
                "URL": p["url"] or "—",
            }
        )

    df = pd.DataFrame(rows)

    # Paginación si hay muchas filas
    if show_pagination and len(df) > PAGINATION_THRESHOLD:
        page_size = PAGINATION_THRESHOLD
        total_pages = (len(df) + page_size - 1) // page_size

        if "price_page" not in st.session_state:
            st.session_state.price_page = 1

        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button(
                "← Anterior",
                key="page_prev",
                disabled=st.session_state.price_page <= 1,
                use_container_width=True,
            ):
                st.session_state.price_page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f"<p style='text-align:center;margin:8px 0;color:var(--color-text-secondary);'>"
                f"Página {st.session_state.price_page} de {total_pages} ({len(df)} registros)"
                f"</p>",
                unsafe_allow_html=True,
            )
        with col_next:
            if st.button(
                "Siguiente →",
                key="page_next",
                disabled=st.session_state.price_page >= total_pages,
                use_container_width=True,
            ):
                st.session_state.price_page += 1
                st.rerun()

        start_idx = (st.session_state.price_page - 1) * page_size
        end_idx = start_idx + page_size
        df_display = df.iloc[start_idx:end_idx]
    else:
        df_display = df

    # Renderizar tabla con HTML personalizado para mejor control accesible
    table_html = '<div class="table-wrapper" role="region" aria-label="Tabla de precios" tabindex="0"><table>'
    table_html += "<thead><tr>"
    for col in df_display.columns:
        table_html += f"<th scope='col'>{col}</th>"
    table_html += "</tr></thead><tbody>"

    for _, row in df_display.iterrows():
        table_html += "<tr>"
        for col_name, val in row.items():
            if col_name == "URL" and val != "—":
                table_html += f"<td><a href='{val}' target='_blank' rel='noopener noreferrer' class='badge badge-info'>Abrir</a></td>"
            elif col_name == "Precio":
                table_html += f"<td><strong>{val}</strong></td>"
            else:
                table_html += f"<td>{val}</td>"
        table_html += "</tr>"

    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)


def _render_history_chart(history: list[dict[str, Any]], product_name: str) -> None:
    """Renderiza gráfico de historial de precios."""
    if not history:
        _render_empty_state(
            f"Sin historial para «{product_name}»",
            f"No hay datos de precios en los últimos {HISTORY_DAYS} días.",
        )
        return

    df = pd.DataFrame(history)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")

    # Línea de precios
    st.line_chart(
        df.set_index("fecha")["precio"],
        use_container_width=True,
        height=300,
    )

    # Tabla de historial
    st.subheader("Detalle de precios")
    _render_price_table(history)


# ── Componentes de UI ────────────────────────────────────────────────────────


def _render_header() -> None:
    """Renderiza cabecera principal con título y acción de actualizar."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1], gap="large")
    with col1:
        st.title("Monitor de Precios")
        st.caption("Seguimiento de precios de competencia con alertas automáticas")
    with col2:
        st.write("")  # Espaciado vertical
        if st.button("Actualizar", key="refresh_header", use_container_width=True):
            st.rerun()


def _render_sidebar() -> None:
    """Renderiza barra lateral con configuración y acciones."""
    settings = get_settings()

    with st.sidebar:
        st.header("Configuración")

        # Métricas de configuración
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Intervalo de scrapeo</div>
              <div class="metric-value">{settings.scrape_interval_hours} h</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-card" style="margin-top:12px;">
              <div class="metric-label">Nivel de log</div>
              <div class="metric-value">{settings.log_level}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.header("Acciones")

        if st.button("Test notificación", key="test_notify", use_container_width=True):
            st.toast("Enviando notificación de prueba...", icon="✉")

        st.divider()
        st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")


def _render_tab_recent() -> None:
    """Renderiza pestaña de precios recientes."""
    st.subheader("Últimos precios registrados")

    skeleton_placeholder = st.empty()
    with skeleton_placeholder.container():
        with st.spinner("Cargando precios..."):
            _render_skeleton_rows(3)

    prices = get_recent_prices(MAX_RECENT_ROWS)
    skeleton_placeholder.empty()

    show_pagination = len(prices) > PAGINATION_THRESHOLD
    _render_price_table(prices, show_pagination=show_pagination)

    # Auto-refresh si está disponible
    try:
        from streamlit_autorefresh import st_autorefresh

        st_autorefresh(interval=AUTO_REFRESH_INTERVAL_MS, key="price_refresh")
    except ImportError:
        pass


def _render_tab_history() -> None:
    """Renderiza pestaña de historial por producto."""
    st.subheader(f"Historial de precios (últimos {HISTORY_DAYS} días)")

    with st.spinner("Cargando historial..."):
        prices_all = get_recent_prices(MAX_HISTORY_ROWS)

    if not prices_all:
        _render_empty_state(
            "Sin datos disponibles",
            "No hay precios registrados para mostrar el historial.",
            "Ejecutar scraper",
            "run_scraper",
        )
        return

    productos_unicos = sorted({p["producto"] for p in prices_all})
    producto_sel = st.selectbox(
        "Seleccionar producto",
        productos_unicos,
        index=0,
        placeholder="Elige un producto...",
        label_visibility="collapsed",
    )

    if producto_sel:
        history = get_price_history(producto_sel, days=HISTORY_DAYS)
        _render_history_chart(history, producto_sel)


# ── Punto de entrada principal ──────────────────────────────────────────────


def main() -> None:
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=SIDEBAR_STATE,
    )

    init_db()
    _check_password()

    _render_header()
    _render_sidebar()

    tab1, tab2 = st.tabs(["Precios recientes", "Historial por producto"])

    with tab1:
        _render_tab_recent()

    with tab2:
        _render_tab_history()


if __name__ == "__main__":
    main()
