from datetime import datetime
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from charts import make_phase_chart, make_transformation_chart, make_jominy_screening
from theme import apply_theme
from engine import MEDIUMS, simulate
from grade_library import GRADES, ELEMENTS, get_grade, chemistry_summary
from guide import render_guide
from logbook import render_logbook

st.set_page_config(page_title="QuenchIQ 2.3", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
apply_theme()
if "runs" not in st.session_state: st.session_state.runs=[]

st.markdown("""<div class="hero"><div class="hero-kicker">VIRTUAL HEAT-TREATMENT LABORATORY</div><h1>Quench<span>IQ</span> <small>2.3</small></h1><p>Explore how steel chemistry, austenitizing and cooling influence transformation — now with grade-aware alloy chemistry.</p><div class="hero-tagline">HEAT → TRANSFORM → UNDERSTAND</div></div>""",unsafe_allow_html=True)
tab_sim,tab_compare,tab_log,tab_guide=st.tabs(["🔥 Simulator","⇄ Compare & Explore","▣ Logbook","◈ Learn & Limits"])

with tab_sim:
    st.markdown('<div class="section-label">1 · CHOOSE YOUR STEEL</div>',unsafe_allow_html=True)
    grade=st.selectbox("Steel grade / chemistry preset",list(GRADES),help="Representative screening chemistry. For engineering use, replace with certified heat-analysis values.")
    comp=get_grade(grade)
    st.markdown(f'<div class="scope-strip"><b>{grade}</b> · {comp["family"]}<br>{comp["note"]}<br><span class="muted">Composition:</span> {chemistry_summary(comp)}</div>',unsafe_allow_html=True)
    with st.expander("View / edit alloy chemistry"):
        edited={}; cols=st.columns(5)
        for i,e in enumerate(ELEMENTS):
            with cols[i%5]: edited[e]=st.number_input(e+" (wt%)",0.0,5.0,float(comp.get(e,0)),0.001,key=f"chem_{e}")
        comp.update(edited)
        st.caption("The edited chemistry is used for the screening calculation. Values are representative, not a material certificate.")

    st.markdown('<div class="section-label">2 · HEAT & QUENCH</div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns([1.15,1.15,1.25,1.1])
    with c1: carbon=st.number_input("Carbon (wt%)",0.10,1.40,float(comp.get("C",0.45)),0.01,key="grade_carbon")
    with c2: aust_temp=st.slider("Austenitizing temperature (°C)",750,1100,850,5,key="aust_input")
    with c3: medium=st.selectbox("Cooling medium",list(MEDIUMS),index=1,help="Medium changes screening severity; no measured heat-transfer coefficient is claimed.",key="medium_input")
    with c4: cooling_rate=st.slider("Base cooling rate (°C/s)",0.5,100.0,25.0,0.5,key="rate_input")
    t1,t2=st.columns([1.2,1])
    with t1: temper=st.checkbox("Apply simplified tempering trend",False)
    with t2: temper_temp=st.slider("Tempering temperature (°C)",150,650,350,10,disabled=not temper)
    result=simulate(carbon,aust_temp,medium,cooling_rate,temper,temper_temp,grade,comp)
    if not result["aust_temp_ok"]: st.warning(f"Austenitizing temperature is below the screening target: {result['critical_boundary']} ≈ {result['critical_temperature']:.0f} °C; suggested screening target ≈ {result['aust_target']:.0f} °C.")
    st.markdown(f'<div class="scope-strip"><b>Grade-aware Ms model:</b> Andrews {result["Ms_andrews"]:.0f} °C · Barbier-style {result["Ms_barbier"]:.0f} °C · blended screening Ms <b>{result["Ms"]:.0f} °C</b>.</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">3 · TRANSFORMATION READOUT</div>',unsafe_allow_html=True)
    cards=st.columns(5); metrics=[("DOMINANT PRODUCT",result["primary_phase"],"phase"),("EST. HARDNESS",f'~{result["hardness"]:.1f} HRC',"gold"),("EST. TENSILE",f'~{result["tensile"]:.0f} MPa',"violet"),("Ms · BLENDED",f'{result["Ms"]:.0f} °C',"green"),("Mf† SCREENING",f'{result["Mf"]:.0f} °C',"rose")]
    for col,(label,value,kind) in zip(cards,metrics):
        with col: st.markdown(f'<div class="metric-card {kind}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.65,1])
    with left:
        st.markdown('<div class="panel-title">Cooling path & transformation map</div>',unsafe_allow_html=True); st.caption("SCHEMATIC / EDUCATIONAL — NOT EXPERIMENTAL CCT DATA"); st.plotly_chart(make_transformation_chart(result,carbon,aust_temp,cooling_rate),width="stretch",config={"displayModeBar":False,"responsive":True})
    with right:
        st.markdown('<div class="panel-title">Estimated transformation products</div>',unsafe_allow_html=True); st.plotly_chart(make_phase_chart(result),width="stretch",config={"displayModeBar":False,"responsive":True}); st.markdown(f'<div class="phase-note"><b>{result["grade"]}</b><br>{result["classification"]} · {result["explanation"]}<br><br><span class="muted">Effective screening rate:</span> {result["effective_cooling_rate"]:.1f} °C/s<br><span class="muted">Chemistry:</span> {chemistry_summary(result["composition"])}</div>',unsafe_allow_html=True)

    d1,d2,d3=st.columns(3)
    with d1:
        st.markdown("#### Transformation estimate")
        for name,value in result["phases"].items():
            if value>.05: st.progress(float(value)/100,text=f"{name}  {value:.1f}%")
    with d2:
        st.markdown("#### Ms model comparison"); st.write(f"**Andrews:** {result['Ms_andrews']:.0f} °C"); st.write(f"**Barbier-style:** {result['Ms_barbier']:.0f} °C"); st.write(f"**Blended screening:** {result['Ms']:.0f} °C"); st.caption("Model spread is shown transparently; it is not a validated uncertainty interval.")
    with d3:
        st.markdown("#### Process readout"); st.write(f"**{result['critical_boundary']} boundary:** {result['critical_temperature']:.0f} °C"); st.write(f"**Austenitizing target:** {result['aust_target']:.0f} °C"); st.write(f"**Base rate:** {cooling_rate:.1f} °C/s"); st.write(f"**Effective screening rate:** {result['effective_cooling_rate']:.1f} °C/s")
    st.markdown(f'<div class="why-card"><b>WHY THIS RESULT?</b><br>{result["explanation"]}<br><br><span class="muted">Grade:</span> {grade} &nbsp; • &nbsp; <span class="muted">C:</span> {carbon:.2f} wt% &nbsp; • &nbsp; <span class="muted">Ms:</span> {result["Ms"]:.0f} °C</div>',unsafe_allow_html=True)
    if temper: st.info("Tempering remains a simplified hardness/strength trend. Detailed tempering reactions and carbide precipitation are not modeled.")
    with st.expander("What changed in QuenchIQ 2.3?"):
        st.markdown("**Grade Library:** representative chemistry presets for 1045, 1080, 4140, 4340, 52100 and 8620.\n\n**Alloy-sensitive Ms:** Mn, Ni, Cr and Mo now influence the Ms calculation; additional chemistry terms are retained for future models.\n\n**Model transparency:** Andrews and Barbier-style estimates are shown side-by-side.\n\n**Still not claimed:** experimental CCT/TTT kinetics, measured cooling curves, geometry, hardenability validation or certified mechanical properties.")
    a1,a2=st.columns(2)
    with a1:
        if st.button("＋ Save run",width="stretch"):
            st.session_state.runs.append({"saved_at":datetime.now().strftime("%Y-%m-%d %H:%M"),"grade":grade,"carbon":carbon,"aust_temp":aust_temp,"medium":medium,"cooling_rate":cooling_rate,"temper":temper,"temper_temp":temper_temp,"result":result}); st.success("Run saved.")
    with a2:
        report=("QuenchIQ 2.3 Simulation Report\n\n"+f"Grade: {grade}\nChemistry: {chemistry_summary(result['composition'])}\nAustenitizing: {aust_temp} °C\nCooling medium: {medium}\nBase rate: {cooling_rate:.1f} °C/s\nEffective screening rate: {result['effective_cooling_rate']:.1f} °C/s\n\nMs Andrews: {result['Ms_andrews']:.1f} °C\nMs Barbier-style: {result['Ms_barbier']:.1f} °C\nBlended Ms: {result['Ms']:.1f} °C\nMf† screening marker: {result['Mf']:.1f} °C\nEstimated hardness: {result['hardness']:.1f} HRC\nEstimated tensile: {result['tensile']:.0f} MPa\n\nPhases:\n"+"\n".join(f"- {k}: {v:.1f}%" for k,v in result["phases"].items())+"\n\nScope:\n"+result["model_scope"])
        st.download_button("↓ Export report",report,file_name="quenchiq_2_3_report.txt",mime="text/plain",width="stretch")
    st.markdown('<div class="method-note"><b>Scientific boundary:</b> Grade chemistry now influences Ms/Mf screening. QuenchIQ still does not claim grade-specific experimental TTT/CCT kinetics, real component cooling curves, or certified mechanical properties.</div>',unsafe_allow_html=True)

with tab_compare:
    st.markdown('<div class="section-label">COMPARE & EXPLORE</div>',unsafe_allow_html=True)
    if len(st.session_state.runs)<2: st.info("Save at least two simulations in the Simulator to compare them.")
    else:
        labels=[f"Run {i+1} — {r.get('grade','Custom')} — {r['medium']}" for i,r in enumerate(st.session_state.runs)]; ca,cb=st.columns(2)
        with ca: ia=st.selectbox("Run A",range(len(labels)),format_func=lambda i:labels[i],key="cmp_a")
        with cb: ib=st.selectbox("Run B",range(len(labels)),index=1,format_func=lambda i:labels[i],key="cmp_b")
        a,b=st.session_state.runs[ia],st.session_state.runs[ib]; ra,rb=a["result"],b["result"]
        fig=go.Figure()
        for i,r in [(ia,a),(ib,b)]:
            temp=np.linspace(r["aust_temp"],60,180); rate=max(r["result"]["effective_cooling_rate"],.01); t=np.maximum((r["aust_temp"]-temp)/rate,.001); fig.add_trace(go.Scatter(x=t,y=temp,mode="lines",name=f"Run {i+1} — {r.get('grade','Custom')}"))
        fig.update_xaxes(type="log",title="Time (s)"); fig.update_yaxes(title="Temperature (°C)"); fig.update_layout(height=430,plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)"); st.plotly_chart(fig,width="stretch")
        st.dataframe({"Metric":["Ms °C","Martensite %","Retained austenite %","Hardness HRC","Tensile MPa"],"Run A":[ra["Ms"],ra["phases"]["Martensite"],ra["phases"]["Retained austenite"],ra["hardness"],ra["tensile"]],"Run B":[rb["Ms"],rb["phases"]["Martensite"],rb["phases"]["Retained austenite"],rb["hardness"],rb["tensile"]]},width="stretch",hide_index=True)
    st.markdown("### Jominy-style hardenability explorer"); st.caption("Educational screening only — not measured grade-specific Jominy data.")
    jc=st.selectbox("Jominy screening grade",list(GRADES),key="j_grade"); jc_data=get_grade(jc); jr=st.slider("Base cooling rate (°C/s)",.5,100.,25.,.5,key="j_rate"); jm=st.selectbox("Quenchant",list(MEDIUMS),index=1,key="j_medium"); ja=st.slider("Austenitizing temperature (°C)",750,1100,850,5,key="j_aust")
    st.plotly_chart(make_jominy_screening(jc_data.get("C",.45),ja,jm,jr),width="stretch",config={"displayModeBar":False})

with tab_log: render_logbook()
with tab_guide: render_guide()
