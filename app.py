"""Streamlit dashboard for the AMD MindOre AI mineral-sorting MVP."""

from html import escape

import matplotlib.pyplot as plt
import streamlit as st

from agent import MiningAgent
from generator import generar_muestra_espectral


ROCK_LABELS = {
    "Cu_alto": "Cobre de alta ley",
    "Estéril": "Estéril / baja señal",
    "Arsénico_Alto": "Alto arsénico",
}

DECISION_TONES = {
    "DESVIAR A DEPOSITO DE ALTA PENALIZACIÓN": "risk",
    "ENVIAR A PLANTA CONCENTRADORA (MOLIENDA)": "concentrator",
    "ENVIAR A PAD DE LIXIVIACIÓN": "leach",
    "BOTADERO (DESMONTE/ESTÉRIL)": "waste",
}


st.set_page_config(page_title="AMD MindOre AI", page_icon="⛏️", layout="wide")
st.markdown(
    """
    <style>
    :root {
        --ink: #17332d;
        --muted: #60716a;
        --paper: #f2f5f0;
        --white: #ffffff;
        --pine: #173d33;
        --copper: #c8734b;
        --line: #dce4dc;
    }
    [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem; }
    [data-testid="stMainBlockContainer"] { gap: 1rem; }
    .hero-band {
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        padding: 2rem 2.2rem;
        border-radius: 5px;
        color: #f6f8f3;
        background-color: var(--pine);
        background-image: repeating-linear-gradient(132deg, transparent 0 28px, rgba(255,255,255,.035) 29px 30px);
        border-bottom: 4px solid var(--copper);
    }
    .hero-copy { position: relative; z-index: 1; }
    .eyebrow, .scan-meta, .status-label {
        font-family: "Bahnschrift", "Arial Narrow", sans-serif;
        font-size: .72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--muted);
    }
    .hero-band .eyebrow { color: #b8d0c2; margin-bottom: .8rem; }
    .hero-band h1 {
        margin: 0;
        color: #fff;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2.65rem;
        font-weight: 500;
        line-height: 1.1;
    }
    .hero-band h1 span { color: #efaa7e; }
    .hero-subtitle { color: #d1ded5; margin-top: .6rem; font-size: .95rem; }
    .hero-status {
        position: relative;
        z-index: 1;
        flex: 0 0 auto;
        padding: .8rem 1rem;
        border: 1px solid rgba(229,241,232,.25);
        border-radius: 3px;
        color: #e1ebe3;
        font-family: "Bahnschrift", "Arial Narrow", sans-serif;
        font-size: .72rem;
        font-weight: 700;
        line-height: 1.6;
        text-transform: uppercase;
    }
    .hero-status span { display: block; color: #a8c4b0; font-weight: 500; }
    .live-dot { display: inline-block !important; width: 7px; height: 7px; margin-right: .45rem; border-radius: 50%; background: #a4c977; }
    .section-head { display: flex; align-items: baseline; gap: .7rem; margin: 1.8rem 0 .7rem; }
    .section-number { color: var(--copper); font-family: "Bahnschrift", "Arial Narrow", sans-serif; font-size: .8rem; font-weight: 800; }
    .section-head h2 { margin: 0; color: var(--ink); font-family: Georgia, "Times New Roman", serif; font-size: 1.35rem; font-weight: 500; }
    [data-testid="stSelectbox"] label { color: var(--muted); font-size: .8rem; font-weight: 700; }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div { min-height: 3rem; border-color: #cbd8ce; border-radius: 3px; background: var(--white); }
    [data-testid="stButton"] { padding-top: 1.65rem; }
    [data-testid="stButton"] button[kind="primary"] {
        min-height: 3rem;
        border: 1px solid var(--copper);
        border-radius: 3px;
        background: var(--copper);
        color: #fff;
        font-weight: 700;
        transition: background-color .16s ease, transform .16s ease;
    }
    [data-testid="stButton"] button[kind="primary"]:hover { background: #a95836; border-color: #a95836; transform: translateY(-1px); }
    .scan-meta { display: flex; gap: 1.6rem; margin: .15rem 0 1rem; font-size: .67rem; }
    .scan-meta strong { color: var(--ink); margin-left: .3rem; }
    .idle-strip {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-top: 1.5rem;
        padding: 1rem 1.2rem;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        color: var(--muted);
        font-family: "Bahnschrift", "Arial Narrow", sans-serif;
        font-size: .76rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .idle-strip strong { color: var(--ink); }
    .idle-range { color: var(--copper); }
    .sample-line { display: flex; flex-wrap: wrap; justify-content: space-between; gap: .5rem; margin: -.2rem 0 1rem; color: var(--muted); font-size: .82rem; }
    .sample-code { color: var(--pine); font-family: monospace; font-weight: 700; }
    [data-testid="stMetric"] {
        padding: .75rem .9rem;
        border: 1px solid var(--line);
        border-top: 2px solid #abc2b1;
        border-radius: 3px;
        background: var(--white);
    }
    [data-testid="stMetricLabel"] p { color: var(--muted); font-size: .75rem; }
    [data-testid="stMetricValue"] { color: var(--ink); font-family: Georgia, "Times New Roman", serif; font-size: 1.5rem; }
    .result-panel { padding: 1.2rem; border: 1px solid var(--line); border-left: 4px solid var(--pine); border-radius: 3px; background: var(--white); }
    .result-panel.risk { border-left-color: #b84c3c; }
    .result-panel.concentrator { border-left-color: #287b68; }
    .result-panel.leach { border-left-color: #c18b31; }
    .result-panel.waste { border-left-color: #75827b; }
    .result-panel .status-label { margin-bottom: .55rem; }
    .result-panel h3 { margin: 0 0 .7rem; color: var(--ink); font-family: Georgia, "Times New Roman", serif; font-size: 1.25rem; font-weight: 500; line-height: 1.25; }
    .result-panel p { margin: 0; color: var(--muted); font-size: .88rem; line-height: 1.55; }
    .json-label { margin: 1.2rem 0 .45rem; color: var(--muted); font-family: "Bahnschrift", "Arial Narrow", sans-serif; font-size: .7rem; font-weight: 700; text-transform: uppercase; }
    [data-testid="stJson"] { border: 1px solid var(--line); border-radius: 3px; background: var(--white); }
    [data-testid="stAlert"] { border-radius: 3px; }
    @media (max-width: 720px) {
        .block-container { padding: 1rem 1rem 2rem; }
        .hero-band { align-items: flex-start; flex-direction: column; padding: 1.4rem; gap: 1rem; }
        .hero-band h1 { font-size: 1.8rem; }
        .hero-status { padding: .55rem .75rem; }
        [data-testid="stButton"] { padding-top: .2rem; }
        .scan-meta { flex-wrap: wrap; gap: .6rem 1rem; }
        .idle-strip { align-items: flex-start; flex-direction: column; gap: .4rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <header class="hero-band">
      <div class="hero-copy">
        <div class="eyebrow">INTELLIGENT INDUSTRY / MINERAL SORTING</div>
        <h1>⛏️ AMD MindOre AI <span>— Agentic Mineral Sorting</span></h1>
        <div class="hero-subtitle">Caracterización espectral para decisiones metalúrgicas en tiempo real</div>
      </div>
      <div class="hero-status"><span><i class="live-dot"></i>Entorno de demostración</span>XRF · Simulación activa</div>
    </header>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-head"><span class="section-number">01</span>'
    "<h2>Preparar lectura</h2></div>",
    unsafe_allow_html=True,
)
selector_column, button_column = st.columns([1.6, 1], vertical_alignment="bottom")
with selector_column:
    mineral_type = st.selectbox(
        "Tipo de roca",
        options=list(ROCK_LABELS),
        format_func=lambda value: ROCK_LABELS[value],
    )
with button_column:
    scan_clicked = st.button(
        "Escanear Muestra con Rayos X",
        type="primary",
        icon=":material/radar:",
        width="stretch",
    )

st.markdown(
    '<div class="scan-meta"><span>VENTANA<strong>0–10 keV</strong></span>'
    '<span>RESOLUCIÓN<strong>100 canales</strong></span>'
    '<span>MODO<strong>Sintético</strong></span></div>',
    unsafe_allow_html=True,
)

if scan_clicked:
    sample = generar_muestra_espectral("MINDORE-001", mineral_type)
    st.session_state["last_sample"] = sample
    st.session_state["last_result"] = MiningAgent().analyze_spectrum(sample)

sample = st.session_state.get("last_sample")
result = st.session_state.get("last_result")

if sample is None or result is None:
    st.markdown(
        '<div class="idle-strip"><strong>● Sistema en espera</strong>'
        '<span>Sin lectura activa</span><span class="idle-range">Canal XRF · 0–10 keV</span></div>',
        unsafe_allow_html=True,
    )
else:
    mineral_label = ROCK_LABELS[sample["mineral_type"]]
    tone = DECISION_TONES[result["decision"]]
    st.markdown(
        '<div class="section-head"><span class="section-number">02</span>'
        "<h2>Resultado de caracterización</h2></div>"
        f'<div class="sample-line"><span>{escape(mineral_label)}</span>'
        f'<span class="sample-code">MUESTRA / {escape(sample["sample_id"])}</span></div>',
        unsafe_allow_html=True,
    )

    grades = sample["simulated_grades"]
    metric_columns = st.columns(4)
    metrics = [
        ("Cobre", f'{grades["Cu_pct"]:.3f} %'),
        ("Hierro", f'{grades["Fe_pct"]:.3f} %'),
        ("Oro", f'{grades["Au_gpt"]:.3f} g/t'),
        ("Arsénico", f'{grades["As_pct"]:.3f} %'),
    ]
    for column, (label, value) in zip(metric_columns, metrics):
        column.metric(label, value)

    st.markdown(
        '<div class="section-head"><span class="section-number">03</span>'
        "<h2>Espectro y decisión</h2></div>",
        unsafe_allow_html=True,
    )
    chart_column, result_column = st.columns([1.65, 1], gap="large")
    with chart_column:
        spectrum = sample["spectral_wave"]
        energies = [point["energy_keV"] for point in spectrum]
        intensities = [point["intensity"] for point in spectrum]

        figure, axis = plt.subplots(figsize=(10, 4.4), facecolor="#f2f5f0")
        axis.set_facecolor("#ffffff")
        axis.plot(energies, intensities, color="#267b69", linewidth=2.1, zorder=3)
        axis.fill_between(energies, intensities, color="#267b69", alpha=0.10)
        axis.set(
            xlabel="Energía (keV)",
            ylabel="Intensidad (u.a.)",
            xlim=(0, 10),
            title=f"RESPUESTA ESPECTRAL · {sample['sample_id']}",
        )
        axis.set_axisbelow(True)
        axis.grid(axis="y", color="#e3e9e3", linewidth=0.8)
        axis.tick_params(colors="#60716a", labelsize=9)
        axis.xaxis.label.set_color("#60716a")
        axis.yaxis.label.set_color("#60716a")
        axis.title.set_color("#17332d")
        axis.title.set_fontsize(10)
        axis.title.set_fontweight("bold")
        for side in ("top", "right"):
            axis.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            axis.spines[side].set_color("#dce4dc")

        if sample["mineral_type"] == "Cu_alto":
            axis.axvline(8.04, color="#c8734b", linestyle=(0, (4, 3)), linewidth=1.2)
            axis.annotate(
                "Cu Kα · 8.04 keV",
                xy=(8.04, max(intensities) * 0.72),
                xytext=(6.15, max(intensities) * 0.9),
                color="#a95836",
                fontsize=8,
                arrowprops={"arrowstyle": "-", "color": "#c8734b", "lw": 0.9},
            )

        figure.tight_layout(pad=1.5)
        st.pyplot(figure, width="stretch")
        plt.close(figure)

        if sample["mineral_type"] == "Arsénico_Alto":
            st.info(
                "La línea de As modelada a 11.7 keV queda fuera de la ventana "
                "de escaneo actual (0–10 keV); la ley simulada sí se usa para "
                "la decisión de desvío."
            )

    with result_column:
        st.markdown(
            f'<div class="result-panel {tone}">'
            '<div class="status-label">DICTAMEN DEL AGENTE</div>'
            f'<h3>{escape(result["decision"])}</h3>'
            f'<p>{escape(result["justification"])}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="json-label">Leyes simuladas · JSON</div>', unsafe_allow_html=True)
        st.json(grades, expanded=True)