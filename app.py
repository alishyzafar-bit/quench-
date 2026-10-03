from datetime import datetime

import streamlit as st

from charts import make_phase_chart, make_transformation_chart
from theme import apply_theme
from engine import MEDIUMS, simulate
from guide import render_guide
from logbook import render_logbook

st.set_page_config(page_title="QuenchIQ 2.2", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
apply_theme()

if "runs" not in st.session_state:
    st.session_state.runs = []

st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">VIRTUAL HEAT-TREATMENT LABORATORY</div>
      <h1>Quench<span>IQ</span> <small>2.2</small></h1>
      <p>Explore how composition, austenitizing conditions and cooling rate influence transformation in plain-carbon steel.</p>
      <div class="hero-tagline">HEAT → TRANSFORM → UNDERSTAND</div>
    </div>
    """, unsafe_allow_html=True,
)

tab_sim, tab_log, tab_guide = st.tabs(["🔥  Simulator", "▣  Logbook", "◈  Learn & Limits"])

with tab_sim:
    st.markdown('<div class="section-label">MATERIAL & PROCESS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.15, 1.15, 1.25, 1.1])
    with c1:
        carbon = st.slider("Carbon content (wt%)", 0.10, 1.40, 0.45, 0.01)
    with c2:
        aust_temp = st.slider("Austenitizing temperature (°C)", 750, 1100, 850, 5)
    with c3:
        medium = st.selectbox("Cooling medium", list(MEDIUMS), help="Context only: the entered cooling rate drives the numerical screening model.")
    with c4:
        cooling_rate = st.slider("Estimated cooling rate (°C/s)", 0.5, 100.0, 25.0, 0.5, help="Use a measured or estimated rate for the section studied.")

    t1, t2 = st.columns([1.2, 1])
    with t1:
        temper = st.checkbox("Apply simplified tempering trend", value=False)
    with t2:
        temper_temp = st.slider("Tempering temperature (°C)", 150, 650, 350, 10, disabled=not temper)

    result = simulate(carbon, aust_temp, medium, cooling_rate, temper, temper_temp)

    if not result["aust_temp_ok"]:
        st.warning(
            f"Austenitizing temperature is below the screening target. Approximate {result['critical_boundary']} boundary: "
            f"{result['critical_temperature']:.0f} °C; screening target: {result['aust_target']:.0f} °C."
        )

    st.markdown(
        f'<div class="scope-strip"><b>Current model:</b> {result["model_scope"]} '
        'The values below are screening estimates, not grade-specific certification.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">TRANSFORMATION READOUT</div>', unsafe_allow_html=True)
    cards = st.columns(5)
    metrics = [
        ("DOMINANT PRODUCT", result["primary_phase"], "phase"),
        ("EST. HARDNESS", f'~{result["hardness"]:.1f} HRC', "gold"),
        ("EST. TENSILE", f'~{result["tensile"]:.0f} MPa', "violet"),
        ("EST. Ms", f'{result["Ms"]:.0f} °C', "green"),
        ("Mf† SCREENING", f'{result["Mf"]:.0f} °C', "rose"),
    ]
    for col, (label, value, kind) in zip(cards, metrics):
        with col:
            st.markdown(f'<div class="metric-card {kind}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.65, 1])
    with left:
        st.markdown('<div class="panel-title">Cooling path & transformation map</div>', unsafe_allow_html=True)
        st.caption("SCHEMATIC / EDUCATIONAL — NOT EXPERIMENTAL CCT DATA")
        st.plotly_chart(make_transformation_chart(result, carbon, aust_temp, cooling_rate), use_container_width=True, config={"displayModeBar": False, "responsive": True})
    with right:
        st.markdown('<div class="panel-title">Estimated transformation products</div>', unsafe_allow_html=True)
        st.plotly_chart(make_phase_chart(result), use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown(f'<div class="phase-note"><b>{result["classification"]} steel</b><br>{result["explanation"]}<br><br><span class="muted">Medium:</span> {medium}<br><span class="muted">Context:</span> {result["medium_note"]}</div>', unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("#### Transformation estimate")
        for name, value in result["phases"].items():
            if value > 0.05:
                st.progress(float(value) / 100, text=f"{name}  {value:.1f}%")
    with d2:
        st.markdown("#### Property trend")
        st.write(f"**Estimated hardness:** {result['hardness']:.1f} HRC")
        st.write(f"**Estimated tensile:** {result['tensile']:.0f} MPa")
        st.write(f"**Estimated yield:** {result['yield_strength']:.0f} MPa")
        st.caption("Trend indicators only; actual properties require validated grade/process data and testing.")
    with d3:
        st.markdown("#### Process readout")
        st.write(f"**Classification:** {result['classification']}")
        st.write(f"**{result['critical_boundary']} boundary:** {result['critical_temperature']:.0f} °C")
        st.write(f"**Austenitizing target:** {result['aust_target']:.0f} °C")
        st.write(f"**Cooling rate:** {cooling_rate:.1f} °C/s")
        st.write(f"**Tempering:** {'Yes — ' + str(temper_temp) + ' °C' if temper else 'No'}")

    st.markdown(
        f'<div class="why-card"><b>WHY THIS RESULT?</b><br>{result["explanation"]}<br><br>'
        f'<span class="muted">Carbon:</span> {carbon:.2f} wt% &nbsp; • &nbsp; '
        f'<span class="muted">Cooling:</span> {cooling_rate:.1f} °C/s &nbsp; • &nbsp; '
        f'<span class="muted">Ms:</span> {result["Ms"]:.0f} °C</div>', unsafe_allow_html=True
    )

    if st.session_state.get("last_result") is not None:
        previous = st.session_state.last_result
        changes = []
        for key, label, threshold in [("Martensite", "Martensite", .5)]:
            delta = result["phases"][key] - previous["phases"][key]
            if abs(delta) > threshold:
                changes.append(f"{label} {'↑' if delta > 0 else '↓'} {abs(delta):.1f} percentage points")
        delta_h = result["hardness"] - previous["hardness"]
        if abs(delta_h) > .2:
            changes.append(f"Estimated hardness {'↑' if delta_h > 0 else '↓'} {abs(delta_h):.1f} HRC")
        if changes:
            st.markdown('<div class="change-strip"><b>What changed from the previous live result?</b><br>' + " • ".join(changes) + '</div>', unsafe_allow_html=True)
    st.session_state.last_result = result

    with st.expander("How the screening model works"):
        st.markdown(
            "**1. Classification:** carbon is compared with the approximate 0.76 wt% eutectoid composition.\n\n"
            "**2. Critical boundary:** hypoeutectoid → Ac3, eutectoid → A1, hypereutectoid → Acm.\n\n"
            "**3. Ms:** carbon-only empirical estimate because alloying chemistry is not entered.\n\n"
            "**4. Martensite:** Koistinen–Marburger room-temperature estimate combined with a transparent cooling-path screening factor.\n\n"
            "**5. Other products:** qualitative allocation among diffusional/intermediate products. These are not experimental phase fractions.\n\n"
            "**6. Properties:** simplified trend correlations for educational comparison, not grade-specific material properties."
        )

    a1, a2 = st.columns(2)
    with a1:
        if st.button("＋ Save run", use_container_width=True):
            st.session_state.runs.append({"saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "carbon": carbon, "aust_temp": aust_temp, "medium": medium, "cooling_rate": cooling_rate, "temper": temper, "temper_temp": temper_temp, "result": result})
            st.success("Run saved to the logbook.")
    with a2:
        report = (
            "QuenchIQ 2.2 Simulation Report\n\n"
            f"Carbon: {carbon:.2f} wt%\nAustenitizing: {aust_temp} °C\nCooling medium: {medium}\n"
            f"Estimated cooling rate: {cooling_rate:.1f} °C/s\nTempering: {'Yes, ' + str(temper_temp) + ' °C' if temper else 'No'}\n\n"
            f"Classification: {result['classification']} steel\nPrimary product: {result['primary_phase']}\n"
            f"Estimated hardness: {result['hardness']:.1f} HRC\nEstimated tensile: {result['tensile']:.0f} MPa\n"
            f"Estimated yield: {result['yield_strength']:.0f} MPa\nEstimated Ms: {result['Ms']:.0f} °C\nMf† screening marker: {result['Mf']:.0f} °C\n"
            f"{result['critical_boundary']} boundary: {result['critical_temperature']:.0f} °C\n"
            f"Austenitizing screening target: {result['aust_target']:.0f} °C\n\n"
            "Estimated transformation products:\n" + "\n".join(f"- {k}: {v:.1f}%" for k, v in result["phases"].items()) +
            "\n\nScientific scope:\n" + result["model_scope"]
        )
        st.download_button("↓ Export report", report, file_name="quenchiq_report.txt", mime="text/plain", use_container_width=True)

    st.markdown('<div class="method-note"><b>Scientific boundary:</b> QuenchIQ is an educational plain-carbon steel screening tool. Real transformation behavior depends on alloy chemistry, austenite grain size, austenitizing history, section size, geometry and the actual cooling curve. Use validated grade-specific data and laboratory measurements for engineering decisions.</div>', unsafe_allow_html=True)

with tab_log:
    render_logbook()

with tab_guide:
    render_guide()
