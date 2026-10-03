from datetime import datetime
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from charts import make_phase_chart, make_transformation_chart
from theme import apply_theme
from engine import MEDIUMS, simulate
from guide import render_guide
from logbook import render_logbook

st.set_page_config(page_title="QuenchIQ 2.2", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
apply_theme()
if "runs" not in st.session_state: st.session_state.runs = []

st.markdown("""
<div class="hero"><div class="hero-kicker">VIRTUAL HEAT-TREATMENT LABORATORY</div><h1>Quench<span>IQ</span> <small>2.2</small></h1><p>Explore how composition, heat treatment and cooling influence transformation in plain-carbon steel.</p><div class="hero-tagline">HEAT → TRANSFORM → UNDERSTAND</div></div>
""", unsafe_allow_html=True)

tab_sim, tab_compare, tab_log, tab_guide = st.tabs(["🔥 Simulator", "⇄ Compare & Explore", "▣ Logbook", "◈ Learn & Limits"])

with tab_sim:
    st.markdown('<div class="section-label">START AN EXPERIMENT</div>', unsafe_allow_html=True)
    preset = st.selectbox("Quick-start preset", ["Custom", "1045-style plain-carbon screening", "1080-style plain-carbon screening", "High-carbon 1.20% C screening"], help="Presets are educational starting points, not grade-certified recipes.")
    preset_values = {
        "1045-style plain-carbon screening": (0.45, 850, "Water", 25.0),
        "1080-style plain-carbon screening": (0.80, 850, "Oil", 12.0),
        "High-carbon 1.20% C screening": (1.20, 825, "Oil", 8.0),
    }
    defaults = preset_values.get(preset, (0.45, 850, "Water", 25.0))
    c1,c2,c3,c4 = st.columns([1.15,1.15,1.25,1.1])
    with c1: carbon=st.slider("Carbon content (wt%)",0.10,1.40,defaults[0],0.01,key="carbon_input")
    with c2: aust_temp=st.slider("Austenitizing temperature (°C)",750,1100,defaults[1],5,key="aust_input")
    with c3: medium=st.selectbox("Cooling medium",list(MEDIUMS),index=list(MEDIUMS).index(defaults[2]),help="Medium changes the screening severity factor; it does not generate a measured heat-transfer curve.",key="medium_input")
    with c4: cooling_rate=st.slider("Base cooling rate (°C/s)",0.5,100.0,defaults[3],0.5,key="rate_input")
    medium_hint={"Brine":"Very severe","Water":"Severe","Oil":"Moderate","Air":"Gentle","Furnace":"Very gentle"}[medium]
    st.markdown(f'<div class="scope-strip"><b>{medium}:</b> {medium_hint} screening condition. The entered rate is multiplied by a transparent medium factor; geometry, agitation and quenchant temperature are not simulated.</div>',unsafe_allow_html=True)

    t1,t2=st.columns([1.2,1])
    with t1: temper=st.checkbox("Apply simplified tempering trend",value=False)
    with t2: temper_temp=st.slider("Tempering temperature (°C)",150,650,350,10,disabled=not temper)
    result=simulate(carbon,aust_temp,medium,cooling_rate,temper,temper_temp)
    if not result["aust_temp_ok"]: st.warning(f"Austenitizing temperature is below the screening target. Approximate {result['critical_boundary']} boundary: {result['critical_temperature']:.0f} °C; screening target: {result['aust_target']:.0f} °C.")
    st.markdown(f'<div class="scope-strip"><b>Model scope:</b> {result["model_scope"]} Values are screening estimates, not grade-specific certification.</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">TRANSFORMATION READOUT</div>',unsafe_allow_html=True)
    cards=st.columns(5); metrics=[("DOMINANT PRODUCT",result["primary_phase"],"phase"),("EST. HARDNESS",f'~{result["hardness"]:.1f} HRC',"gold"),("EST. TENSILE",f'~{result["tensile"]:.0f} MPa',"violet"),("EST. Ms",f'{result["Ms"]:.0f} °C',"green"),("Mf† SCREENING",f'{result["Mf"]:.0f} °C',"rose")]
    for col,(label,value,kind) in zip(cards,metrics):
        with col: st.markdown(f'<div class="metric-card {kind}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)

    left,right=st.columns([1.65,1])
    with left:
        st.markdown('<div class="panel-title">Cooling path & transformation map</div>',unsafe_allow_html=True); st.caption("SCHEMATIC / EDUCATIONAL — NOT EXPERIMENTAL CCT DATA")
        st.plotly_chart(make_transformation_chart(result,carbon,aust_temp,cooling_rate),use_container_width=True,config={"displayModeBar":False,"responsive":True})
    with right:
        st.markdown('<div class="panel-title">Estimated transformation products</div>',unsafe_allow_html=True); st.plotly_chart(make_phase_chart(result),use_container_width=True,config={"displayModeBar":False,"responsive":True})
        st.markdown(f'<div class="phase-note"><b>{result["classification"]} steel</b><br>{result["explanation"]}<br><br><span class="muted">Medium:</span> {medium}<br><span class="muted">Effective screening rate:</span> {result["effective_cooling_rate"]:.1f} °C/s<br><span class="muted">Context:</span> {result["medium_note"]}</div>',unsafe_allow_html=True)

    d1,d2,d3=st.columns(3)
    with d1:
        st.markdown("#### Transformation estimate")
        for name,value in result["phases"].items():
            if value>0.05: st.progress(float(value)/100,text=f"{name}  {value:.1f}%")
    with d2:
        st.markdown("#### Property trend"); st.write(f"**Estimated hardness:** {result['hardness']:.1f} HRC"); st.write(f"**Estimated tensile:** {result['tensile']:.0f} MPa"); st.write(f"**Estimated yield:** {result['yield_strength']:.0f} MPa"); st.caption("Trend indicators only; actual properties require validated grade/process data and testing.")
    with d3:
        st.markdown("#### Process readout"); st.write(f"**Classification:** {result['classification']}"); st.write(f"**{result['critical_boundary']} boundary:** {result['critical_temperature']:.0f} °C"); st.write(f"**Austenitizing target:** {result['aust_target']:.0f} °C"); st.write(f"**Base rate:** {cooling_rate:.1f} °C/s"); st.write(f"**Effective screening rate:** {result['effective_cooling_rate']:.1f} °C/s")

    st.markdown(f'<div class="why-card"><b>WHY THIS RESULT?</b><br>{result["explanation"]}<br><br><span class="muted">Carbon:</span> {carbon:.2f} wt% &nbsp; • &nbsp; <span class="muted">Cooling:</span> {cooling_rate:.1f} °C/s &nbsp; • &nbsp; <span class="muted">Ms:</span> {result["Ms"]:.0f} °C</div>',unsafe_allow_html=True)
    if temper:
        st.info("Tempering is represented as a simplified hardness/strength trend. The app does not simulate carbide precipitation, tempering kinetics or grade-specific tempered-martensite microstructure.")

    with st.expander("How the screening model works"):
        st.markdown("**1. Classification:** carbon is compared with the approximate 0.76 wt% eutectoid composition.\n\n**2. Critical boundary:** hypoeutectoid → Ac3, eutectoid → A1, hypereutectoid → Acm.\n\n**3. Ms:** carbon-only empirical estimate because alloying chemistry is not entered.\n\n**4. Martensite:** Koistinen–Marburger room-temperature estimate combined with a transparent cooling-path screening factor.\n\n**5. Other products:** qualitative allocation among diffusional/intermediate products; retained austenite is shown separately as a screening estimate.\n\n**6. Properties:** simplified trend correlations, not grade-specific material properties.")

    a1,a2=st.columns(2)
    with a1:
        if st.button("＋ Save run",use_container_width=True):
            st.session_state.runs.append({"saved_at":datetime.now().strftime("%Y-%m-%d %H:%M"),"carbon":carbon,"aust_temp":aust_temp,"medium":medium,"cooling_rate":cooling_rate,"temper":temper,"temper_temp":temper_temp,"result":result}); st.success("Run saved to the logbook.")
    with a2:
        report=("QuenchIQ 2.2 Simulation Report\n\n"+f"Carbon: {carbon:.2f} wt%\nAustenitizing: {aust_temp} °C\nCooling medium: {medium}\nBase cooling rate: {cooling_rate:.1f} °C/s\nEffective screening rate: {result['effective_cooling_rate']:.1f} °C/s\nTempering: {'Yes, '+str(temper_temp)+' °C' if temper else 'No'}\n\nClassification: {result['classification']} steel\nPrimary product: {result['primary_phase']}\nEstimated hardness: {result['hardness']:.1f} HRC\nEstimated tensile: {result['tensile']:.0f} MPa\nEstimated Ms: {result['Ms']:.0f} °C\nMf† screening marker: {result['Mf']:.0f} °C\n\nEstimated transformation products:\n"+"\n".join(f"- {k}: {v:.1f}%" for k,v in result["phases"].items())+"\n\nScientific scope:\n"+result["model_scope"])
        st.download_button("↓ Export report",report,file_name="quenchiq_report.txt",mime="text/plain",use_container_width=True)
    st.markdown('<div class="method-note"><b>Scientific boundary:</b> QuenchIQ is an educational plain-carbon steel screening tool. Real transformation depends on alloy chemistry, austenite grain size, austenitizing history, section size, geometry and the actual cooling curve. Use validated grade-specific data and laboratory measurements for engineering decisions.</div>',unsafe_allow_html=True)

with tab_compare:
    st.markdown('<div class="section-label">COMPARE & EXPLORE</div>',unsafe_allow_html=True)
    if len(st.session_state.runs)<2:
        st.info("Save at least two simulations in the Simulator to unlock visual run comparison.")
    else:
        labels=[f"Run {i+1} — {r['medium']}, {r['carbon']:.2f}% C, {r['cooling_rate']:.1f} °C/s" for i,r in enumerate(st.session_state.runs)]
        x,y=st.columns(2)
        with x: ia=st.selectbox("Run A",range(len(labels)),format_func=lambda i:labels[i],key="cmp_a")
        with y: ib=st.selectbox("Run B",range(len(labels)),format_func=lambda i:labels[i],index=1 if len(labels)>1 else 0,key="cmp_b")
        if ia!=ib:
            a,b=st.session_state.runs[ia],st.session_state.runs[ib]; ra,rb=a["result"],b["result"]
            st.markdown(f'<div class="change-strip"><b>Run A → Run B</b><br>Hardness: {ra["hardness"]:.1f} → {rb["hardness"]:.1f} HRC &nbsp; • &nbsp; Martensite: {ra["phases"]["Martensite"]:.1f}% → {rb["phases"]["Martensite"]:.1f}% &nbsp; • &nbsp; Retained austenite: {ra["phases"]["Retained austenite"]:.1f}% → {rb["phases"]["Retained austenite"]:.1f}%</div>',unsafe_allow_html=True)
            fig=go.Figure()
            for i,r in [(ia,a),(ib,b)]:
                temp=np.linspace(r["aust_temp"],60,180); rate=max(r["result"]["effective_cooling_rate"],.01); t=np.maximum((r["aust_temp"]-temp)/rate,.001); fig.add_trace(go.Scatter(x=t,y=temp,mode="lines",name=f"Run {i+1} — {r['medium']}"))
            fig.update_xaxes(type="log",title="Time (s)",gridcolor="#E5E8E5"); fig.update_yaxes(title="Temperature (°C)",gridcolor="#E5E8E5"); fig.update_layout(height=430,plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#68747A"),legend=dict(orientation="h")); st.plotly_chart(fig,use_container_width=True)
            st.dataframe({"Metric":["Martensite %","Retained austenite %","Bainite %","Pearlite %","Hardness HRC","Tensile MPa","Ms °C"],"Run A":[ra["phases"]["Martensite"],ra["phases"]["Retained austenite"],ra["phases"]["Bainite"],ra["phases"]["Pearlite"],ra["hardness"],ra["tensile"],ra["Ms"]],"Run B":[rb["phases"]["Martensite"],rb["phases"]["Retained austenite"],rb["phases"]["Bainite"],rb["phases"]["Pearlite"],rb["hardness"],rb["tensile"],rb["Ms"]]},use_container_width=True,hide_index=True)

    st.markdown("### Jominy-style hardenability explorer")
    st.caption("Educational screening only — this is not a measured Jominy end-quench curve.")
    jc1,jc2,jc3,jc4=st.columns(4)
    with jc1: jc=st.slider("Carbon (wt%)",0.10,1.40,0.45,0.01,key="j_c")
    with jc2: ja=st.slider("Austenitizing (°C)",750,1100,850,5,key="j_a")
    with jc3: jm=st.selectbox("Quenchant",list(MEDIUMS),index=1,key="j_m")
    with jc4: jr=st.slider("Base rate (°C/s)",0.5,100.0,25.0,0.5,key="j_r")
    dist=np.linspace(0,100,120); mf={"Brine":1.55,"Water":1.25,"Oil":.75,"Air":.28,"Furnace":.10}; local=np.maximum(.5,jr*(1.55/(1+.085*dist))*mf[jm]); nose=650-80*jc; critical=max(.1,(ja-nose)/(8+6*jc)); sev=local/critical; hard=np.clip(28+34*(sev/(1+sev))+9*jc,15,68)
    jf=go.Figure(go.Scatter(x=dist,y=hard,mode="lines",line=dict(color="#1597A8",width=3),fill="tozeroy",fillcolor="rgba(21,151,168,.10)",name="Screening curve")); jf.update_xaxes(title="Distance from quenched end (mm)"); jf.update_yaxes(title="Screening hardness (HRC)",range=[15,70]); jf.update_layout(height=390,plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#68747A"),title="Jominy-style screening — not experimental data"); st.plotly_chart(jf,use_container_width=True)

with tab_log: render_logbook()
with tab_guide: render_guide()
