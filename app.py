from datetime import datetime

import streamlit as st

from charts import make_phase_chart, make_transformation_chart
from theme import apply_theme
from engine import MEDIUMS, simulate
from guide import render_guide
from logbook import render_logbook

st.set_page_config(
    page_title="QuenchIQ 2.1",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()

if "runs" not in st.session_state:
    st.session_state.runs = []

st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">HEAT TREATMENT • TRANSFORMATION • MICROSTRUCTURE</div>
      <h1>Quench<span>IQ</span> <small>2.1</small></h1>
      <p>Explore how carbon content, austenitizing temperature and cooling conditions
         influence the predicted transformation of plain-carbon steel.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_sim, tab_log, tab_guide = st.tabs(["⚙  Simulator", "▣  Logbook", "◈  Phase Guide"])

with tab_sim:
    st.markdown('<div class="section-label">SIMULATION SETUP</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([1.15, 1.15, 1.25, 1.1])
    with c1:
        carbon = st.slider("Carbon content (wt%)", 0.10, 1.40, 0.45, 0.01)
    with c2:
        aust_temp = st.slider("Austenitizing temperature (°C)", 750, 1100, 850, 5)
    with c3:
        medium = st.selectbox(
            "Cooling medium",
            list(MEDIUMS),
            help="The medium is descriptive context. The entered cooling rate is the quantity used by the screening model.",
        )
    with c4:
        cooling_rate = st.slider(
            "Estimated cooling rate (°C/s)",
            0.5,
            100.0,
            25.0,
            0.5,
            help="Use a measured or estimated rate for the section being studied. Actual rates vary with geometry, agitation and position.",
        )

    t1, t2 = st.columns([1.2, 1])
    with t1:
        temper = st.checkbox("Apply tempering", value=False)
    with t2:
        temper_temp = st.slider(
            "Tempering temperature (°C)",
            150,
            650,
            350,
            10,
            disabled=not temper,
        )

    result = simulate(
        carbon=carbon,
        aust_temp=aust_temp,
        medium=medium,
        cooling_rate=cooling_rate,
        temper=temper,
        temper_temp=temper_temp,
    )

    if not result["aust_temp_ok"]:
        st.warning(
            f"Austenitizing temperature is below the screening target for this composition. "
            f"Approximate {result['critical_boundary']} boundary: {result['critical_temperature']:.0f} °C; "
            f"the screening target is {result['aust_target']:.0f} °C (boundary + 20 °C). "
            "Increase the temperature or treat this run as intentionally non-austenitized."
        )

    st.markdown(
        f'<div class="scope-strip"><b>Model scope:</b> {result["model_scope"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">LIVE RESULT</div>', unsafe_allow_html=True)
    cards = st.columns(5)
    metrics = [
        ("PRIMARY PHASE", result["primary_phase"], "phase"),
        ("EST. HARDNESS", f'~{result["hardness"]:.1f} HRC', "gold"),
        ("EST. TENSILE", f'~{result["tensile"]:.0f} MPa', "violet"),
        ("Ms", f'{result["Ms"]:.0f} °C', "green"),
        ("Mf*", f'{result["Mf"]:.0f} °C', "rose"),
    ]
    for col, (label, value, kind) in zip(cards, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card {kind}"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.65, 1])

    with left:
        st.markdown('<div class="panel-title">Transformation map</div>', unsafe_allow_html=True)
        st.caption(
            "SCHEMATIC / EDUCATIONAL SCREENING MAP — NOT EXPERIMENTAL CCT DATA. "
            "The selected cooling path and Ms respond to the current inputs."
        )
        st.plotly_chart(
            make_transformation_chart(result, carbon, aust_temp, cooling_rate),
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )

    with right:
        st.markdown('<div class="panel-title">Predicted microstructure</div>', unsafe_allow_html=True)
        st.plotly_chart(
            make_phase_chart(result),
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        st.markdown(
            f'<div class="phase-note"><b>{result["classification"]} steel</b><br>'
            f'{result["explanation"]}<br><br>'
            f'<span class="muted">Cooling medium:</span> {medium}<br>'
            f'<span class="muted">Medium note:</span> {result["medium_note"]}</div>',
            unsafe_allow_html=True,
        )

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("#### Estimated transformation products")
        for name, value in result["phases"].items():
            if value > 0.05:
                st.progress(float(value) / 100, text=f"{name}  {value:.1f}%")

    with d2:
        st.markdown("#### Mechanical estimate")
        st.write(f"**Yield strength:** {result['yield_strength']:.0f} MPa")
        st.write(f"**Tensile strength:** {result['tensile']:.0f} MPa")
        st.write(f"**Hardness:** {result['hardness']:.1f} HRC")
        st.caption(
            "Trend estimates only. These are not grade-specific property predictions or certification values."
        )

    with d3:
        st.markdown("#### Transformation notes")
        st.write(f"**Cooling medium:** {medium}")
        st.write(f"**Estimated cooling rate:** {cooling_rate:.1f} °C/s")
        st.write(f"**Austenitizing:** {aust_temp} °C")
        st.write(f"**{result['critical_boundary']} screening boundary:** {result['critical_temperature']:.0f} °C")
        st.write(f"**Tempering:** {'Yes — ' + str(temper_temp) + ' °C' if temper else 'No'}")

    if st.session_state.get("last_result") is not None:
        previous = st.session_state.last_result
        changes = []
        if result["phases"]["Martensite"] > previous["phases"]["Martensite"] + 0.5:
            changes.append("Martensite ↑")
        elif result["phases"]["Martensite"] < previous["phases"]["Martensite"] - 0.5:
            changes.append("Martensite ↓")
        if result["hardness"] > previous["hardness"] + 0.2:
            changes.append("Estimated hardness ↑")
        elif result["hardness"] < previous["hardness"] - 0.2:
            changes.append("Estimated hardness ↓")
        if result["tensile"] > previous["tensile"] + 5:
            changes.append("Estimated tensile strength ↑")
        elif result["tensile"] < previous["tensile"] - 5:
            changes.append("Estimated tensile strength ↓")
        if changes:
            st.markdown(
                '<div class="change-strip"><b>What changed from the previous live result?</b><br>'
                + " • ".join(changes) + '</div>', unsafe_allow_html=True
            )
    st.session_state.last_result = result

    with st.expander("How QuenchIQ calculates this result"):
        st.markdown(
            f"""
            **1. Steel classification**  
            Carbon content is compared with the approximate 0.76 wt% eutectoid composition.

            **2. Austenitizing check**  
            Hypoeutectoid steel uses Ac3, eutectoid steel uses A1, and hypereutectoid steel uses Acm.
            The selected temperature is screened against a target 20 °C above that boundary.

            **3. Martensite start (Ms)**  
            Ms uses a carbon-only form of the Barbier empirical relation. Because alloying elements
            are not entered, their terms are set to zero and the result remains an estimate.

            **4. Martensite fraction**  
            The room-temperature martensite estimate uses the Koistinen–Marburger relationship
            with α = 0.011, then applies a transparent cooling-path screening factor.

            **5. Other products**  
            The remaining fraction is allocated qualitatively between pearlite, ferrite/cementite,
            and an intermediate bainitic tendency. These fractions are **not experimental CCT data**.

            **6. Properties**  
            Hardness and strength are trend estimates intended for comparison inside the app.
            """
        )

    a1, a2 = st.columns([1, 1])
    with a1:
        if st.button("＋ Save run", use_container_width=True):
            st.session_state.runs.append(
                {
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "carbon": carbon,
                    "aust_temp": aust_temp,
                    "medium": medium,
                    "cooling_rate": cooling_rate,
                    "temper": temper,
                    "temper_temp": temper_temp,
                    "result": result,
                }
            )
            st.success("Run saved to the logbook.")

    with a2:
        report = (
            "QuenchIQ 2.1 Simulation Report\n\n"
            f"Carbon: {carbon:.2f} wt%\n"
            f"Austenitizing: {aust_temp} °C\n"
            f"Cooling medium: {medium}\n"
            f"Estimated cooling rate: {cooling_rate:.1f} °C/s\n"
            f"Tempering: {'Yes, ' + str(temper_temp) + ' °C' if temper else 'No'}\n\n"
            f"Classification: {result['classification']} steel\n"
            f"Primary phase: {result['primary_phase']}\n"
            f"Hardness estimate: {result['hardness']:.1f} HRC\n"
            f"Tensile strength estimate: {result['tensile']:.0f} MPa\n"
            f"Yield strength estimate: {result['yield_strength']:.0f} MPa\n"
            f"Ms: {result['Ms']:.0f} °C\n"
            f"Mf*: {result['Mf']:.0f} °C\n"
            f"{result['critical_boundary']} screening boundary: {result['critical_temperature']:.0f} °C\n"
            f"Austenitizing screening target: {result['aust_target']:.0f} °C\n\n"
            "Estimated transformation products:\n"
            + "\n".join(f"- {k}: {v:.1f}%" for k, v in result["phases"].items())
            + "\n\nScientific scope:\n"
            + result["model_scope"]
        )
        st.download_button(
            "↓ Export report",
            report,
            file_name="quenchiq_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown(
        '<div class="method-note"><b>Scientific boundary:</b> QuenchIQ is an educational '
        'plain-carbon steel screening tool. Real CCT/TTT behavior depends on alloy chemistry, '
        'austenite grain size, prior microstructure, austenitizing history, section size and '
        'the actual cooling curve. Use measured or validated grade-specific data for engineering decisions.'
        '</div>',
        unsafe_allow_html=True,
    )

with tab_log:
    render_logbook()

with tab_guide:
    render_guide()
