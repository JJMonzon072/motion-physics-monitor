"""
Sistema de Monitoreo de Movimiento y Análisis Físico en Tiempo Real
Universidad Mariano Gálvez — Física 1 — Juan José Monzón

Ejecutar con: streamlit run app.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Motion Physics Monitor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Hide Streamlit chrome ── */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer,
    .stDeployButton { display: none !important; }

    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }

    /* ── Typography & base ── */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        color: #1E293B !important;
    }

    /* ── Forzar fondo claro en el área principal (evita tema oscuro del sistema) ── */
    html, body { background-color: #F8FAFC !important; }
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMain"] > div,
    section.main,
    .main .block-container,
    .block-container { background-color: #F8FAFC !important; }

    /* ── Header oscuro que Streamlit Cloud muestra ── */
    [data-testid="stHeader"] { background-color: #F8FAFC !important; border-bottom: 1px solid #E2E8F0 !important; }

    /* ── Sidebar base ── */
    [data-testid="stSidebar"] {
        background: #0F172A !important;
        border-right: 1px solid #1E293B !important;
        min-width: 220px !important;
    }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] hr { border-color: #1E293B !important; opacity: 1 !important; }

    /* ── Nav menu: transform radio buttons into menu items ── */

    /* 1. Hide the radio circle indicator (the actual dot/ring) */
    [data-testid="stSidebar"] [role="radio"] {
        display: none !important;
    }

    /* 2. Remove default gap between items */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        gap: 1px !important;
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
    }

    /* 3. Style each label as a full-width menu item */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        margin: 0 !important;
        cursor: pointer !important;
        border-left: 2px solid transparent !important;
        transition: background 0.12s ease, border-color 0.12s ease !important;
        box-sizing: border-box !important;
    }

    /* 4. Menu item text */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label span {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #64748B !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }

    /* 5. Hover state */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #1E293B !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover span {
        color: #E2E8F0 !important;
    }

    /* 6. Active / selected item — :has() targets label that contains the checked input */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has([aria-checked="true"]),
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #1E293B !important;
        border-left-color: #3B82F6 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has([aria-checked="true"]) p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has([aria-checked="true"]) span,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
        color: #60A5FA !important;
        font-weight: 600 !important;
    }

    /* ── Headings ── */
    h1 {
        font-size: 1.75rem !important; font-weight: 700 !important;
        color: #0F172A !important; letter-spacing: -0.025em !important;
        margin-bottom: 0.25rem !important;
    }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: #1E293B !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; color: #334155 !important; }

    /* ── Page header component ── */
    .page-header {
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 14px;
        margin-bottom: 24px;
    }
    .page-header .title {
        font-size: 1.4rem; font-weight: 700; color: #0F172A;
        letter-spacing: -0.02em; line-height: 1.2;
    }
    .page-header .subtitle {
        font-size: 0.85rem; color: #64748B; margin-top: 3px;
    }

    /* ── Metric card ── */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 16px 14px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: #3B82F6;
    }
    .metric-card .mc-label {
        font-size: 0.70rem; font-weight: 600; color: #64748B;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px;
    }
    .metric-card .mc-value {
        font-size: 1.5rem; font-weight: 700; color: #0F172A; line-height: 1;
    }
    .metric-card .mc-unit {
        font-size: 0.75rem; color: #94A3B8; margin-top: 4px;
    }

    /* accent colors per column index */
    .mc-accent-1::before { background: #3B82F6; }
    .mc-accent-2::before { background: #10B981; }
    .mc-accent-3::before { background: #F59E0B; }
    .mc-accent-4::before { background: #8B5CF6; }
    .mc-accent-5::before { background: #EF4444; }

    /* ── Stat row (hero page) ── */
    .stat-block {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px 18px;
        height: 100%;
    }
    .stat-block .sb-label {
        font-size: 0.68rem; font-weight: 700; color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.09em;
    }
    .stat-block .sb-title {
        font-size: 1rem; font-weight: 700; color: #0F172A; margin-top: 6px;
    }
    .stat-block .sb-desc {
        font-size: 0.82rem; color: #64748B; margin-top: 4px; line-height: 1.5;
    }

    /* ── Alert / notice boxes ── */
    .notice {
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.88rem;
        line-height: 1.55;
        border-left: 3px solid;
    }
    .notice-info  { background: #EFF6FF; border-color: #3B82F6; color: #1E3A5F; }
    .notice-warn  { background: #FFFBEB; border-color: #F59E0B; color: #78350F; }
    .notice-ok    { background: #F0FDF4; border-color: #22C55E; color: #14532D; }
    .notice-error { background: #FEF2F2; border-color: #EF4444; color: #7F1D1D; }

    /* ── Section divider ── */
    .section-label {
        font-size: 0.70rem; font-weight: 700; color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.10em;
        margin-bottom: 12px; margin-top: 8px;
    }

    /* ── Classification badge ── */
    .badge {
        display: inline-block; border-radius: 20px;
        padding: 3px 12px; font-size: 0.75rem; font-weight: 700;
        letter-spacing: 0.03em;
    }
    .badge-green  { background: #DCFCE7; color: #15803D; }
    .badge-yellow { background: #FEF9C3; color: #854D0E; }
    .badge-red    { background: #FEE2E2; color: #B91C1C; }
    .badge-blue   { background: #DBEAFE; color: #1D4ED8; }

    /* ── Numbered step ── */
    .step-row {
        display: flex; align-items: flex-start; margin-bottom: 14px; gap: 14px;
    }
    .step-num {
        min-width: 28px; height: 28px; border-radius: 6px;
        background: #EFF6FF; color: #2563EB;
        font-size: 0.75rem; font-weight: 700;
        display: flex; align-items: center; justify-content: center;
    }
    .step-body { flex: 1; }
    .step-title { font-size: 0.90rem; font-weight: 600; color: #0F172A; }
    .step-desc  { font-size: 0.82rem; color: #64748B; margin-top: 2px; }

    /* ── Action buttons (main content area only, not sidebar) ── */
    [data-testid="stMain"] .stButton > button {
        background: #2563EB !important; color: #FFFFFF !important;
        border: none !important; border-radius: 8px !important;
        padding: 10px 24px !important; font-weight: 600 !important;
        font-size: 0.88rem !important; letter-spacing: 0.01em !important;
        transition: background 0.15s, transform 0.1s !important;
        box-shadow: none !important;
    }
    [data-testid="stMain"] .stButton > button:hover  { background: #1D4ED8 !important; transform: translateY(-1px) !important; }
    [data-testid="stMain"] .stButton > button:active { transform: translateY(0) !important; }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {
        background: #0F172A !important; color: #F8FAFC !important;
        border: 1px solid #334155 !important; border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stDownloadButton"] > button:hover { background: #1E293B !important; }

    /* ── Inputs ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        border-color: #CBD5E1 !important; border-radius: 7px !important;
        font-size: 0.875rem !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
        overflow: hidden;
    }

    /* ── Progress ── */
    [data-testid="stProgressBar"] > div { background: #3B82F6 !important; }

    /* ── Expander ── */
    details[data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
        background: #FFFFFF !important; margin-bottom: 8px !important;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 600 !important; font-size: 0.9rem !important; color: #1E293B !important;
        padding: 14px 16px !important;
    }

    /* ── Native st.metric ── */
    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 10px; padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] { color: #64748B !important; font-size: 0.75rem !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: #0F172A !important; font-weight: 700 !important; }

    /* ── Radio horizontal ── */
    [data-testid="stRadio"] [role="radiogroup"] {
        gap: 6px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── helpers ───────────────────────────────────────────────────────────────────
def _s(df: pd.DataFrame, col: str) -> pd.Series:
    """Retorna df[col] como pd.Series; silencia la ambigüedad Series|DataFrame de Pyright."""
    return pd.Series(df[col])


def page_header(title: str, subtitle: str = "") -> None:
    """Renderiza un encabezado de página estilizado con título y subtítulo opcional."""
    sub = f"<div class='subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"<div class='page-header'>" f"<div class='title'>{title}</div>{sub}" f"</div>",
        unsafe_allow_html=True,
    )


def notice(text: str, kind: str = "info") -> None:
    """Renderiza un cuadro de aviso estilizado. kind: 'info' | 'warn' | 'ok' | 'error'."""
    cls = {
        "info": "notice-info",
        "warn": "notice-warn",
        "ok": "notice-ok",
        "error": "notice-error",
    }.get(kind, "notice-info")
    st.markdown(f"<div class='notice {cls}'>{text}</div>", unsafe_allow_html=True)


def metric_card(label: str, value: str, unit: str = "", accent: int = 1) -> None:
    """Renderiza una tarjeta KPI con etiqueta, valor y unidad opcional. accent elige el color (1–4)."""
    st.markdown(
        f"<div class='metric-card mc-accent-{accent}'>"
        f"<div class='mc-label'>{label}</div>"
        f"<div class='mc-value'>{value}</div>"
        f"<div class='mc-unit'>{unit}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    """Renderiza una etiqueta divisora de sección en mayúsculas."""
    st.markdown(f"<div class='section-label'>{text}</div>", unsafe_allow_html=True)


def spacer(px: int = 16) -> None:
    """Inserta un espacio vertical en blanco de px píxeles."""
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)


# ── session state ─────────────────────────────────────────────────────────────
def _init_state() -> None:
    """Inicializa las claves de session_state con valores por defecto en la primera carga."""
    defaults: dict = {
        "results_df": None,
        "video_info": None,
        "meters_per_pixel": None,
        "calibrated": False,
        "summary": None,
        "classification": None,
        "last_annotated_frame": None,
        "data_source": "none",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

# ── sidebar ───────────────────────────────────────────────────────────────────
NAV_PAGES = [
    "Inicio",
    "Cargar Video",
    "Procesar Video",
    "Analisis Fisico",
    "Graficas",
    "Simulacion",
    "Validacion",
    "Exportar",
    "Ayuda",
]

with st.sidebar:
    st.markdown(
        "<div style='padding:20px 4px 6px;'>"
        "<div style='font-size:1.1rem;font-weight:800;color:#F1F5F9;"
        "letter-spacing:-0.02em;'>Motion Physics</div>"
        "<div style='font-size:0.68rem;color:#475569;font-weight:600;"
        "text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;'>Monitor</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='background:#1E293B;border-radius:6px;padding:8px 10px;"
        "margin:8px 0 16px;'>"
        "<div style='font-size:0.68rem;color:#475569;font-weight:600;"
        "text-transform:uppercase;letter-spacing:0.07em;'>Universidad Mariano Galvez</div>"
        "<div style='font-size:0.78rem;color:#64748B;margin-top:2px;'>Fisica 1 — Proyecto Final</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    page = st.radio("nav", NAV_PAGES, label_visibility="collapsed")
    spacer(12)
    st.markdown(
        "<div style='font-size:0.68rem;color:#334155;padding-top:12px;"
        "border-top:1px solid #1E293B;'>v1.0.0 — Python + Streamlit</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# INICIO
# ─────────────────────────────────────────────────────────────────────────────
if page == "Inicio":
    # Top bar
    st.markdown(
        "<div style='background:#0F172A;border-radius:10px;padding:28px 32px 24px;"
        "margin-bottom:24px;'>"
        "<div style='font-size:0.68rem;font-weight:700;color:#475569;"
        "text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;'>"
        "Universidad Mariano Galvez — Fisica 1 — Proyecto Final"
        "</div>"
        "<div style='font-size:1.65rem;font-weight:800;color:#F8FAFC;"
        "letter-spacing:-0.025em;line-height:1.15;margin-bottom:8px;'>"
        "Sistema de Monitoreo de Movimiento"
        "</div>"
        "<div style='font-size:0.9rem;color:#64748B;'>"
        "Analisis fisico en tiempo real — Cinematica — OpenCV — Streamlit"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Stat blocks
    c1, c2, c3, c4 = st.columns(4, gap="small")
    blocks = [
        ("01", "Posicion", "Coordenadas x(t) e y(t) con conversion a metros"),
        ("02", "Velocidad", "Instantanea, promedio y maxima con suavizado"),
        ("03", "Aceleracion", "Instantanea y promedio por diferencias finitas"),
        ("04", "Clasificacion", "MRU, MRUV o Caida Libre automatica por regresion"),
    ]
    for col, (num, title, desc) in zip([c1, c2, c3, c4], blocks):
        with col:
            st.markdown(
                f"<div class='stat-block'>"
                f"<div class='sb-label'>{num}</div>"
                f"<div class='sb-title'>{title}</div>"
                f"<div class='sb-desc'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    spacer(24)
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        section_label("Como usar el sistema")
        steps = [
            ("Cargar Video", "Sube un archivo MP4 o AVI con el objeto en movimiento."),
            ("Configurar color", "Elige el color del objeto y ajusta el area minima."),
            ("Calibrar (opcional)", "Ingresa una referencia real para obtener metros."),
            ("Procesar", "El sistema rastrea el objeto frame a frame."),
            ("Analizar", "Revisa metricas, graficas y clasificacion del movimiento."),
            ("Validar", "Compara resultados experimentales con valores teoricos."),
        ]
        for i, (t, d) in enumerate(steps, 1):
            st.markdown(
                f"<div class='step-row'>"
                f"<div class='step-num'>0{i}</div>"
                f"<div class='step-body'>"
                f"<div class='step-title'>{t}</div>"
                f"<div class='step-desc'>{d}</div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

    with col_r:
        section_label("Fisica aplicada")
        st.markdown(
            "<div style='background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;"
            "padding:18px;font-size:0.87rem;color:#334155;'>"
            "<div style='margin-bottom:14px;'>"
            "<div style='font-size:0.70rem;font-weight:700;color:#64748B;"
            "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>MRU</div>"
            "<code style='background:#F8FAFC;padding:4px 8px;border-radius:4px;"
            "font-size:0.85rem;color:#1E293B;border:1px solid #E2E8F0;'>"
            "x = x&#8320; + v&#183;t</code>"
            "</div>"
            "<div style='margin-bottom:14px;'>"
            "<div style='font-size:0.70rem;font-weight:700;color:#64748B;"
            "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>MRUV</div>"
            "<code style='background:#F8FAFC;padding:4px 8px;border-radius:4px;"
            "font-size:0.85rem;color:#1E293B;border:1px solid #E2E8F0;'>"
            "x = x&#8320; + v&#8320;t + &frac12;at&sup2;</code>"
            "</div>"
            "<div>"
            "<div style='font-size:0.70rem;font-weight:700;color:#64748B;"
            "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>Caida Libre</div>"
            "<code style='background:#F8FAFC;padding:4px 8px;border-radius:4px;"
            "font-size:0.85rem;color:#1E293B;border:1px solid #E2E8F0;'>"
            "y = y&#8320; &minus; &frac12;gt&sup2;</code>"
            "</div>"
            "<div style='margin-top:14px;padding-top:12px;border-top:1px solid #F1F5F9;"
            "font-size:0.78rem;color:#94A3B8;'>"
            "g = 9.8 m/s&sup2; &nbsp;&#183;&nbsp; Media movil &nbsp;&#183;&nbsp; R&sup2; para clasificacion"
            "</div></div>",
            unsafe_allow_html=True,
        )
        spacer(12)
        notice(
            "<strong>Sin video disponible</strong><br>"
            "Usa <strong>Simulacion</strong> para generar datos de MRU, MRUV o Caida Libre "
            "y probar el sistema completo sin necesidad de grabar un video.",
            "info",
        )


# ─────────────────────────────────────────────────────────────────────────────
# CARGAR VIDEO
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Cargar Video":
    from src.tracking import PRESET_NAMES, get_config_for_color
    from src.utils import compute_meters_per_pixel
    from src.video_processing import get_video_info

    page_header("Cargar Video", "Sube el video y configura el rastreo del objeto")

    uploaded = st.file_uploader(
        "Archivo de video (MP4, AVI, MOV)",
        type=["mp4", "avi", "mov"],
        help="El objeto debe tener un color solido y contrastante con el fondo.",
    )

    if uploaded:
        suffix = Path(uploaded.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        try:
            info = get_video_info(tmp_path)
            st.session_state["video_info"] = info
            st.session_state["tmp_video_path"] = tmp_path

            spacer(8)
            section_label("Informacion del video")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            for col, lbl, val in [
                (c1, "FPS", f"{info.fps:.1f}"),
                (c2, "Duracion", info.duration_str),
                (c3, "Frames", str(info.frame_count)),
                (c4, "Ancho", f"{info.width} px"),
                (c5, "Alto", f"{info.height} px"),
                (c6, "A procesar", str(min(info.frame_count, 2000))),
            ]:
                col.metric(lbl, val)

            spacer(20)
            section_label("Configuracion de rastreo")
            col_a, col_b = st.columns(2, gap="large")

            with col_a:
                color_name = st.selectbox("Color del objeto", PRESET_NAMES)
                min_area = st.slider("Area minima (px²)", 100, 5000, 400, 50)
                skip_frames = st.slider("Procesar 1 de cada N frames", 1, 5, 1)

            with col_b:
                if color_name == "Personalizado":
                    section_label("Rango HSV personalizado")
                    h_lo = st.slider("H minimo", 0, 179, 0)
                    h_hi = st.slider("H maximo", 0, 179, 30)
                    s_lo = st.slider("S minimo", 0, 255, 100)
                    v_lo = st.slider("V minimo", 0, 255, 80)
                    cfg = get_config_for_color("Rojo", min_area)
                    cfg.lower_hsv = (h_lo, s_lo, v_lo)
                    cfg.upper_hsv = (h_hi, 255, 255)
                    cfg.lower_hsv2 = None
                    cfg.upper_hsv2 = None
                else:
                    cfg = get_config_for_color(color_name, min_area)
                    notice(
                        f"Color seleccionado: <strong>{color_name}</strong>. "
                        "Si el objeto no se detecta bien, prueba ajustar el area minima "
                        "o usa la opcion Personalizado para definir el rango HSV.",
                        "info",
                    )

            st.session_state["tracking_cfg"] = cfg
            st.session_state["skip_frames"] = skip_frames

            spacer(20)
            section_label("Calibracion pixel a metro")
            notice(
                "Sin calibracion los resultados se muestran en pixeles. "
                "Para obtener metros reales, coloca una referencia de tamano conocido en el video "
                "(regla, cinta metrica) y completa los campos siguientes.",
                "warn",
            )
            spacer(10)
            col_c, col_d = st.columns(2, gap="large")
            with col_c:
                real_dist = st.number_input("Distancia real (metros)", 0.01, 100.0, 1.0, 0.01)
            with col_d:
                pixel_dist = st.number_input("Esa distancia en pixeles", 1.0, 5000.0, 100.0, 1.0)

            use_cal = st.checkbox("Activar calibracion", value=False)
            if use_cal:
                mpp = compute_meters_per_pixel(real_dist, pixel_dist)
                st.session_state["meters_per_pixel"] = mpp
                st.session_state["calibrated"] = True
                st.success(f"Calibracion activa: {mpp:.6f} m/px")
            else:
                st.session_state["meters_per_pixel"] = None
                st.session_state["calibrated"] = False

            spacer(16)
            notice(
                "Video cargado correctamente. Continua en <strong>Procesar Video</strong>.",
                "ok",
            )

        except Exception as exc:
            notice(f"No se pudo leer el video: {exc}", "error")
    else:
        notice(
            "Sube un archivo de video para comenzar. "
            "Si no tienes un video listo puedes usar el modo <strong>Simulacion</strong>.",
            "info",
        )


# ─────────────────────────────────────────────────────────────────────────────
# PROCESAR VIDEO
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Procesar Video":
    from src.motion_classification import classify_motion
    from src.physics_calculations import (
        build_results_dataframe,
        build_time_array,
        compute_acceleration,
        compute_distance,
        compute_positions,
        compute_summary_stats,
        compute_velocity_2d,
    )
    from src.tracking import annotate_frame, detect_object
    from src.video_processing import frame_to_rgb, iter_frames

    page_header("Procesar Video", "Rastreo del objeto y calculo de variables cinematicas")

    if st.session_state.get("video_info") is None:
        notice("Primero carga un video en la seccion <strong>Cargar Video</strong>.", "warn")
    else:
        from src.tracking import TrackingConfig

        info = st.session_state["video_info"]
        cfg: TrackingConfig | None = st.session_state.get("tracking_cfg")
        skip: int = st.session_state.get("skip_frames", 1)

        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.markdown(
                f"<div style='font-size:0.88rem;color:#475569;padding:10px 14px;"
                f"background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;'>"
                f"<strong style='color:#1E293B;'>{Path(info.path).name}</strong>"
                f"&nbsp;&nbsp;·&nbsp;&nbsp;{info.fps:.1f} FPS"
                f"&nbsp;&nbsp;·&nbsp;&nbsp;{info.duration_str}"
                f"&nbsp;&nbsp;·&nbsp;&nbsp;{info.frame_count} frames"
                f"</div>",
                unsafe_allow_html=True,
            )

        spacer(16)

        if st.button("Analizar Video", use_container_width=True):
            if cfg is None:
                notice(
                    "Configura primero el color del objeto en <strong>Cargar Video</strong>.",
                    "warn",
                )
                st.stop()

            mpp: float | None = st.session_state.get("meters_per_pixel")
            calibrated: bool = st.session_state.get("calibrated", False)

            x_list: list[float | None] = []
            y_list: list[float | None] = []
            frame_ids: list[int] = []
            trajectory: list[tuple[float, float]] = []
            last_frame_rgb = None
            detection_count = 0

            prog = st.progress(0.0, text="Procesando frames...")
            preview_placeholder = st.empty()
            total_frames = min(info.frame_count, 2000)

            for frame_idx, bgr_frame in iter_frames(info.path, skip=skip, max_frames=2000):
                det = detect_object(bgr_frame, cfg)
                x_list.append(det.x if det else None)
                y_list.append(det.y if det else None)
                frame_ids.append(frame_idx)

                if det:
                    trajectory.append((det.x, det.y))
                    if len(trajectory) > 60:
                        trajectory = trajectory[-60:]
                    detection_count += 1

                annotated = annotate_frame(bgr_frame, det, trajectory)
                last_frame_rgb = frame_to_rgb(annotated)

                progress_val = min(len(frame_ids) / total_frames, 1.0)
                prog.progress(
                    progress_val,
                    text=f"Frame {frame_ids[-1]} — detectados: {detection_count}",
                )
                if len(frame_ids) % 15 == 0:
                    preview_placeholder.image(last_frame_rgb, width=420)

            prog.progress(1.0, text="Procesamiento completo")
            st.session_state["last_annotated_frame"] = last_frame_rgb

            if detection_count < 5:
                notice(
                    f"Solo se detectaron {detection_count} frames. "
                    "Verifica el color seleccionado, la iluminacion o reduce el area minima.",
                    "warn",
                )

            n = len(frame_ids)
            effective_fps = info.fps / skip
            time_arr = build_time_array(n, effective_fps)
            pos_df = compute_positions(x_list, y_list, mpp)

            frame_height = info.height
            if calibrated:
                pos_df["y_m"] = frame_height * (mpp or 1) - _s(pos_df, "y_m")
            else:
                pos_df["y_px"] = frame_height - _s(pos_df, "y_px")

            x_use: pd.Series = _s(pos_df, "x_m") if calibrated else _s(pos_df, "x_px")
            y_use: pd.Series = _s(pos_df, "y_m") if calibrated else _s(pos_df, "y_px")

            dist = compute_distance(x_use, y_use)
            vx, vy, speed = compute_velocity_2d(x_use, y_use, time_arr)
            acc = compute_acceleration(speed, time_arr)

            result_cls = classify_motion(
                time_arr,
                y_use,
                speed,
                acc,
                vy=vy,
                y_position=y_use,
                calibrated=calibrated,
            )
            summary = compute_summary_stats(speed, acc, dist)

            results_df = build_results_dataframe(
                frames=frame_ids,
                time=time_arr,
                x_px=_s(pos_df, "x_px"),
                y_px=_s(pos_df, "y_px"),
                x_m=_s(pos_df, "x_m"),
                y_m=_s(pos_df, "y_m"),
                distance=dist,
                vx=vx,
                vy=vy,
                speed=speed,
                acceleration=acc,
                movement_type=result_cls.movement_type,
                calibrated=calibrated,
            )

            st.session_state.update(
                {
                    "results_df": results_df,
                    "summary": summary,
                    "classification": result_cls,
                    "data_source": "video",
                }
            )

            notice(
                "Analisis completo. Continua en <strong>Analisis Fisico</strong> y <strong>Graficas</strong>.",
                "ok",
            )
            spacer(8)
            section_label("Vista previa de datos")
            st.dataframe(results_df.head(10), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANALISIS FISICO
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Analisis Fisico":
    page_header("Analisis Fisico", "Metricas cinematicas calculadas a partir del rastreo")

    from src.motion_classification import ClassificationResult

    results_df = st.session_state.get("results_df")
    summary: dict | None = st.session_state.get("summary")
    classification: ClassificationResult | None = st.session_state.get("classification")
    calibrated: bool = st.session_state.get("calibrated", False)
    unit = "m" if calibrated else "px"

    if results_df is None or summary is None or classification is None:
        notice(
            "No hay datos disponibles. Procesa un video o ejecuta una simulacion primero.",
            "warn",
        )
    else:
        section_label("Resumen de resultados")
        c1, c2, c3, c4, c5 = st.columns(5, gap="small")
        for col, label, value, u, acc_num in [
            (c1, "Distancia total", f"{summary['total_distance']:.3f}", unit, 1),
            (c2, "Velocidad promedio", f"{summary['avg_velocity']:.3f}", f"{unit}/s", 2),
            (c3, "Velocidad maxima", f"{summary['max_velocity']:.3f}", f"{unit}/s", 3),
            (c4, "Aceleracion prom.", f"{summary['avg_acceleration']:.3f}", f"{unit}/s²", 4),
            (c5, "Tipo de movimiento", classification.movement_type, "", 5),
        ]:
            with col:
                metric_card(label, value, u, acc_num)

        spacer(20)
        section_label("Clasificacion del movimiento")

        conf_badge = {
            "Alta": "<span class='badge badge-green'>Confianza Alta</span>",
            "Media": "<span class='badge badge-yellow'>Confianza Media</span>",
            "Baja": "<span class='badge badge-red'>Confianza Baja</span>",
        }.get(classification.confidence, "")

        st.markdown(
            f"<div style='background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;"
            f"padding:18px 20px;'>"
            f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>"
            f"<span style='font-size:1rem;font-weight:700;color:#0F172A;'>"
            f"{classification.movement_type}</span>{conf_badge}"
            f"</div>"
            f"<div style='font-size:0.87rem;color:#475569;line-height:1.6;'>"
            f"{classification.explanation}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if not calibrated:
            spacer(12)
            notice(
                "Sin calibracion activa — resultados en pixeles, no en metros. "
                "Activa la calibracion en <strong>Cargar Video</strong> para obtener unidades fisicas reales.",
                "warn",
            )

        if st.session_state.get("last_annotated_frame") is not None:
            spacer(16)
            section_label("Ultimo frame analizado")
            st.image(st.session_state["last_annotated_frame"], width=520)

        spacer(16)
        section_label("Datos completos")
        st.dataframe(results_df, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# GRAFICAS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Graficas":
    from src.plotting import (
        plot_acceleration,
        plot_combined_dashboard,
        plot_position,
        plot_trajectory,
        plot_velocity,
    )

    page_header(
        "Graficas Cinematicas", "Visualizacion interactiva de posicion, velocidad y aceleracion"
    )

    results_df = st.session_state.get("results_df")
    calibrated = st.session_state.get("calibrated", False)
    unit = "m" if calibrated else "px"

    if results_df is None:
        notice("No hay datos. Procesa un video o genera una simulacion primero.", "warn")
    else:
        view = st.radio(
            "Vista",
            ["Panel combinado", "Graficas individuales"],
            horizontal=True,
        )
        spacer(8)

        if view == "Panel combinado":
            st.plotly_chart(
                plot_combined_dashboard(results_df, unit=unit), use_container_width=True
            )
        else:
            st.plotly_chart(plot_position(results_df, unit=unit), use_container_width=True)
            st.plotly_chart(plot_velocity(results_df, unit=f"{unit}/s"), use_container_width=True)
            st.plotly_chart(
                plot_acceleration(results_df, unit=f"{unit}/s²"), use_container_width=True
            )
            traj = plot_trajectory(results_df, unit=unit)
            if traj:
                st.plotly_chart(traj, use_container_width=True)
            else:
                notice(
                    "La trayectoria 2D no esta disponible para datos de simulacion 1D.",
                    "info",
                )


# ─────────────────────────────────────────────────────────────────────────────
# SIMULACION
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Simulacion":
    from src.motion_classification import ClassificationResult, classify_motion
    from src.physics_calculations import compute_summary_stats
    from src.plotting import plot_combined_dashboard
    from src.simulation import simulate_free_fall, simulate_mru, simulate_mruv

    page_header("Simulacion Cinematica", "Genera datos sinteticos sin necesidad de un video")

    notice(
        "Selecciona el tipo de movimiento y ajusta los parametros. "
        "Los datos simulados pasan por los mismos calculos que el modo video.",
        "info",
    )
    spacer(16)

    mov_type = st.selectbox("Tipo de movimiento", ["MRU", "MRUV", "Caida Libre"])
    spacer(8)
    col1, col2 = st.columns(2, gap="large")

    if mov_type == "MRU":
        with col1:
            section_label("Parametros")
            v0 = st.number_input("Velocidad constante (m/s)", 0.1, 50.0, 2.0, 0.1)
            x0 = st.number_input("Posicion inicial (m)", 0.0, 100.0, 0.0, 0.1)
        with col2:
            section_label("Tiempo")
            total_t = st.number_input("Tiempo total (s)", 1.0, 60.0, 5.0, 0.5)
            st.markdown(
                "<div class='notice notice-info' style='margin-top:12px;'>"
                "<strong>MRU</strong>: velocidad constante, aceleracion = 0."
                "</div>",
                unsafe_allow_html=True,
            )
        if st.button("Generar simulacion MRU", use_container_width=True):
            df = simulate_mru(v0=v0, x0=x0, total_time=total_t)
            summary = compute_summary_stats(
                _s(df, "speed_m_s"), _s(df, "acceleration_m_s2"), _s(df, "distance_m")
            )
            cls = classify_motion(
                _s(df, "time_s").to_numpy(),
                _s(df, "position_m"),
                _s(df, "speed_m_s"),
                _s(df, "acceleration_m_s2"),
            )
            st.session_state.update(
                {
                    "results_df": df,
                    "summary": summary,
                    "classification": cls,
                    "calibrated": True,
                    "data_source": "simulation",
                }
            )
            notice(
                "Datos MRU generados. Revisa <strong>Analisis Fisico</strong> y <strong>Graficas</strong>.",
                "ok",
            )

    elif mov_type == "MRUV":
        with col1:
            section_label("Parametros")
            v0 = st.number_input("Velocidad inicial (m/s)", 0.0, 50.0, 0.0, 0.1)
            a0 = st.number_input("Aceleracion (m/s²)", -20.0, 20.0, 2.0, 0.1)
        with col2:
            section_label("Condiciones iniciales")
            x0 = st.number_input("Posicion inicial (m)", 0.0, 100.0, 0.0, 0.1)
            total_t = st.number_input("Tiempo total (s)", 1.0, 60.0, 5.0, 0.5)
        if st.button("Generar simulacion MRUV", use_container_width=True):
            df = simulate_mruv(v0=v0, a0=a0, x0=x0, total_time=total_t)
            summary = compute_summary_stats(
                _s(df, "speed_m_s"), _s(df, "acceleration_m_s2"), _s(df, "distance_m")
            )
            cls = classify_motion(
                _s(df, "time_s").to_numpy(),
                _s(df, "position_m"),
                _s(df, "speed_m_s"),
                _s(df, "acceleration_m_s2"),
            )
            st.session_state.update(
                {
                    "results_df": df,
                    "summary": summary,
                    "classification": cls,
                    "calibrated": True,
                    "data_source": "simulation",
                }
            )
            notice(
                "Datos MRUV generados. Revisa <strong>Analisis Fisico</strong> y <strong>Graficas</strong>.",
                "ok",
            )

    else:
        with col1:
            section_label("Parametros")
            y0 = st.number_input("Altura inicial (m)", 0.5, 100.0, 10.0, 0.5)
            v0 = st.number_input("Velocidad inicial vertical (m/s)", -10.0, 10.0, 0.0, 0.1)
        with col2:
            section_label("Condiciones")
            g = st.number_input("Gravedad (m/s²)", 1.0, 25.0, 9.8, 0.1)
            use_custom_time = st.checkbox("Definir tiempo total manualmente", value=False)
            total_t_ff = None
            if use_custom_time:
                total_t_ff = st.number_input("Tiempo total (s)", 0.1, 30.0, 2.0, 0.1)
        if st.button("Generar simulacion Caida Libre", use_container_width=True):
            df = simulate_free_fall(y0=y0, v0=v0, g=g, total_time=total_t_ff)
            summary = compute_summary_stats(
                _s(df, "speed_m_s"), _s(df, "acceleration_m_s2"), _s(df, "distance_m")
            )
            cls = ClassificationResult(
                movement_type="Caida Libre",
                confidence="Alta",
                explanation=f"Simulacion de caida libre con g = {g} m/s² desde {y0} m de altura.",
            )
            st.session_state.update(
                {
                    "results_df": df,
                    "summary": summary,
                    "classification": cls,
                    "calibrated": True,
                    "data_source": "simulation",
                }
            )
            notice(
                "Datos de Caida Libre generados. Revisa <strong>Analisis Fisico</strong> y <strong>Graficas</strong>.",
                "ok",
            )

    if (
        st.session_state.get("data_source") == "simulation"
        and st.session_state.get("results_df") is not None
    ):
        spacer(16)
        section_label("Vista previa")
        st.plotly_chart(
            plot_combined_dashboard(st.session_state["results_df"], unit="m"),
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# VALIDACION
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Validacion":
    from src.validation import (
        results_to_dataframe,
        validate_free_fall,
        validate_mru,
        validate_mruv,
        validate_single,
    )

    page_header("Validacion de Resultados", "Comparacion de valores experimentales contra teoricos")

    notice(
        "Selecciona el tipo de validacion e ingresa el valor teorico esperado. "
        "El sistema calcula el error absoluto y porcentual.",
        "info",
    )
    spacer(16)

    summary = st.session_state.get("summary")
    classification = st.session_state.get("classification")

    if summary is None:
        notice("Procesa un video o genera una simulacion antes de validar.", "warn")
    else:
        val_type = st.selectbox(
            "Tipo de validacion",
            ["MRU — Velocidad", "MRUV — Aceleracion", "Caida Libre — Gravedad", "Personalizada"],
        )
        spacer(12)

        if val_type == "MRU — Velocidad":
            theo_v = st.number_input(
                "Velocidad teorica (m/s)", 0.001, 100.0, 1.0, 0.001, format="%.4f"
            )
            if st.button("Calcular error"):
                r = validate_mru(theo_v, summary["avg_velocity"])
                st.dataframe(results_to_dataframe([r]), use_container_width=True)
                notice(r.interpretation, "info")

        elif val_type == "MRUV — Aceleracion":
            theo_a = st.number_input(
                "Aceleracion teorica (m/s²)", 0.001, 100.0, 2.0, 0.001, format="%.4f"
            )
            if st.button("Calcular error"):
                r = validate_mruv(theo_a, abs(summary["avg_acceleration"]))
                st.dataframe(results_to_dataframe([r]), use_container_width=True)
                notice(r.interpretation, "info")

        elif val_type == "Caida Libre — Gravedad":
            notice("Se compara la aceleracion promedio experimental contra g = 9.8 m/s².", "info")
            if st.button("Calcular error"):
                r = validate_free_fall(abs(summary["avg_acceleration"]))
                st.dataframe(results_to_dataframe([r]), use_container_width=True)
                notice(r.interpretation, "info")

        else:
            col1, col2 = st.columns(2, gap="large")
            with col1:
                variable_name = st.text_input("Nombre de la variable", "Velocidad")
                unit_str = st.text_input("Unidad", "m/s")
            with col2:
                theo_val = st.number_input("Valor teorico", format="%.6f")
                exp_val = st.number_input(
                    "Valor experimental", value=summary["avg_velocity"], format="%.6f"
                )
            if st.button("Calcular error"):
                r = validate_single(variable_name, theo_val, exp_val, unit_str)
                st.dataframe(results_to_dataframe([r]), use_container_width=True)
                notice(r.interpretation, "info")

        spacer(24)
        section_label("Referencia de ecuaciones")
        st.markdown("""
| Movimiento | Posicion | Velocidad | Aceleracion |
|---|---|---|---|
| MRU | x = x₀ + v·t | v = constante | a = 0 |
| MRUV | x = x₀ + v₀·t + ½·a·t² | v = v₀ + a·t | a = constante |
| Caida Libre | y = y₀ + v₀·t − ½·g·t² | v = v₀ − g·t | a = −9.8 m/s² |
""")


# ─────────────────────────────────────────────────────────────────────────────
# EXPORTAR
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Exportar":
    from src.utils import dataframe_to_csv_bytes, ensure_output_dir

    page_header("Exportar Resultados", "Descarga los datos calculados en formato CSV")

    results_df = st.session_state.get("results_df")

    if results_df is None:
        notice("No hay datos para exportar. Procesa un video o genera una simulacion.", "warn")
    else:
        source = st.session_state.get("data_source", "")
        source_label = "video" if source == "video" else "simulacion"

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Fuente", source_label.capitalize())
        col_b.metric("Filas", str(len(results_df)))
        col_c.metric("Columnas", str(len(results_df.columns)))

        spacer(16)
        section_label("Vista previa")
        st.dataframe(results_df.head(20), use_container_width=True)

        spacer(16)
        csv_bytes = dataframe_to_csv_bytes(results_df)
        st.download_button(
            label="Descargar CSV",
            data=csv_bytes,
            file_name="motion_analysis.csv",
            mime="text/csv",
            use_container_width=True,
        )

        try:
            out_dir = ensure_output_dir()
            out_path = out_dir / "motion_analysis.csv"
            results_df.to_csv(out_path, index=False)
            spacer(8)
            notice(f"Archivo guardado localmente en: <code>{out_path}</code>", "ok")
        except Exception as e:
            notice(f"No se pudo guardar localmente: {e}", "warn")


# ─────────────────────────────────────────────────────────────────────────────
# AYUDA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Ayuda":
    page_header("Guia de Uso", "Instrucciones para grabar, calibrar y usar la aplicacion")

    with st.expander("Como grabar el video demostrativo", expanded=True):
        st.markdown("""
- Usa una pelota de **color solido y brillante** (roja, azul, verde, naranja).
- Graba con **buena iluminacion** y fondo claro y uniforme.
- Mantén la **camara completamente fija** — usa un tripode o apoya el celular.
- Graba de forma **perpendicular al plano del movimiento**.
- Coloca una **referencia de escala visible** (regla o cinta metrica) para poder calibrar.
- Evita objetos del mismo color en el fondo.
- Para **caida libre**: suelta la pelota desde una altura conocida (1–3 m).
- Resolucion recomendada: 1080p o 720p, 30 FPS minimo.
- **El alumno debe aparecer en el video** (requisito del proyecto).
""")

    with st.expander("Como calibrar pixeles a metros"):
        st.markdown("""
1. Coloca una referencia de tamano conocido visible en el video (ej. regla de 30 cm).
2. En **Cargar Video**, activa la calibracion.
3. Mide cuantos pixeles ocupa esa referencia en el video.
4. Ingresa la distancia real y la distancia en pixeles.
5. Factor calculado: `m/px = distancia_real_m / distancia_px`.

Sin calibracion los resultados se muestran en pixeles. El sistema aun puede
clasificar el tipo de movimiento y mostrar graficas relativas.
""")

    with st.expander("Como interpretar las graficas"):
        st.markdown("""
| Grafica | Que buscar |
|---|---|
| Posicion vs Tiempo | Linea recta = MRU · Curva = MRUV o Caida Libre |
| Velocidad vs Tiempo | Horizontal = MRU · Linea inclinada = MRUV |
| Aceleracion vs Tiempo | Cerca de cero = MRU · Constante ≠ 0 = MRUV · ~9.8 m/s² = Caida Libre |
| Trayectoria 2D | Recta = movimiento horizontal · Parabola = caida libre |
""")

    with st.expander("Limitaciones del sistema"):
        st.markdown("""
- La precision depende directamente de la calidad del video.
- La iluminacion afecta la deteccion del color del objeto.
- El objeto necesita un color distinguible del fondo.
- La camara debe estar fija durante toda la grabacion.
- Sin calibracion, los resultados no estan en unidades fisicas reales.
- La aceleracion puede presentar ruido porque se calcula como segunda derivada numerica.
- El sistema es una aproximacion educativa, no un instrumento de laboratorio profesional.
""")

    with st.expander("Recomendaciones para mejorar la precision"):
        st.markdown("""
- Usa mayor FPS si tu camara lo permite (60 FPS mejora los resultados).
- Elige un objeto de color muy saturado y uniforme, sin degradados.
- Ajusta el rango HSV si el objeto no se detecta bien con los presets.
- Usa una referencia de calibracion lo mas grande posible.
- Graba en condiciones de luz constante, evita parpadeos o sombras moviles.
- Aplica suavizado mayor si la grafica de aceleracion es muy ruidosa.
""")
