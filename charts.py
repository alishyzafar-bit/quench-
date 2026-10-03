import numpy as np
import plotly.graph_objects as go
from engine import screening_nose

PHASE_COLORS = {
    "Martensite": "#E85D2A", "Bainite": "#F3A33B", "Pearlite": "#1597A8",
    "Ferrite": "#6F9E8F", "Cementite": "#71808A", "Retained austenite": "#B58C4A",
}

def _base_layout(height=430):
    return dict(height=height, margin=dict(l=58,r=20,t=48,b=55), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF", font=dict(color="#68747A",family="DM Sans, sans-serif"), hoverlabel=dict(bgcolor="#182126",font_color="#FFFFFF"), legend=dict(orientation="h",y=1.04,x=0))

def make_phase_chart(result):
    labels=[name for name,value in result["phases"].items() if value>0.05]
    values=[result["phases"][name] for name in labels]
    colors=[PHASE_COLORS[name] for name in labels]
    fig=go.Figure(go.Pie(labels=labels,values=values,hole=.68,marker=dict(colors=colors,line=dict(color="#FFFFFF",width=3)),textinfo="percent",textfont=dict(color="#182126"),hovertemplate="%{label}: %{value:.1f}%<extra></extra>",sort=False))
    fig.add_annotation(text=f"<b>{result['primary_phase']}</b><br><span style='font-size:12px'>dominant estimate</span>",x=.5,y=.5,showarrow=False,font=dict(size=14,color="#182126"))
    layout=_base_layout(320); layout["margin"]=dict(l=10,r=10,t=15,b=15); fig.update_layout(**layout); fig.update_layout(legend=dict(orientation="h",y=-.02,x=.02)); return fig

def make_transformation_chart(result, carbon, aust_temp, cooling_rate):
    time=np.logspace(-2,4,360); log_t=np.log10(time); nose_temp,nose_time,_=screening_nose(carbon,aust_temp); width=1.0
    pearlite_start=nose_temp-35*np.exp(-((log_t-np.log10(nose_time))/width)**2); pearlite_finish=pearlite_start-75
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=time,y=pearlite_start,mode="lines",name="Diffusional start (schematic)",line=dict(color="#1597A8",width=2),hovertemplate="t=%{x:.3g} s<br>T=%{y:.0f} °C<extra></extra>"))
    fig.add_trace(go.Scatter(x=time,y=pearlite_finish,mode="lines",name="Diffusional finish (schematic)",line=dict(color="#1597A8",width=2,dash="dash"),hovertemplate="t=%{x:.3g} s<br>T=%{y:.0f} °C<extra></extra>"))
    path_temp=np.linspace(aust_temp,60,240); path_time=np.maximum((aust_temp-path_temp)/max(result["effective_cooling_rate"],0.01),0.001)
    fig.add_trace(go.Scatter(x=path_time,y=path_temp,mode="lines",name=f"Selected path ({result['inputs'].medium})",line=dict(color="#E85D2A",width=3),hovertemplate="t=%{x:.3g} s<br>T=%{y:.0f} °C<extra></extra>"))
    fig.add_hline(y=result["Ms"],line=dict(color="#1597A8",dash="dot",width=1.5),annotation_text=f"Ms {result['Ms']:.0f} °C",annotation_position="top right")
    fig.add_hline(y=result["Mf"],line=dict(color="#1597A8",dash="dot",width=1.5),annotation_text=f"Mf† {result['Mf']:.0f} °C",annotation_position="bottom right")
    bt=result["critical_temperature"]; bl="A1 727 °C" if result["critical_boundary"]=="A1" else f"{result['critical_boundary']} {bt:.0f} °C"
    fig.add_hline(y=bt,line=dict(color="#71808A",dash="dot",width=1),annotation_text=bl,annotation_position="left")
    fig.add_annotation(text="SCHEMATIC / EDUCATIONAL — NOT EXPERIMENTAL CCT DATA",xref="paper",yref="paper",x=.5,y=1.08,showarrow=False,font=dict(size=11,color="#E85D2A"))
    fig.update_xaxes(type="log",title="Time (s)",gridcolor="#E5E8E5",color="#68747A"); fig.update_yaxes(title="Temperature (°C)",range=[50,max(850,aust_temp+40)],gridcolor="#E5E8E5",color="#68747A"); fig.update_layout(**_base_layout(475)); return fig

def make_cooling_comparison(runs):
    fig=go.Figure()
    for i,run in enumerate(runs):
        r=run["result"]; temp=np.linspace(run["aust_temp"],60,180); rate=max(r["effective_cooling_rate"],.01); t=np.maximum((run["aust_temp"]-temp)/rate,.001)
        fig.add_trace(go.Scatter(x=t,y=temp,mode="lines",name=f"Run {i+1} — {run['medium']}, {run['cooling_rate']:.1f} °C/s"))
    fig.update_xaxes(type="log",title="Time (s)",gridcolor="#E5E8E5"); fig.update_yaxes(title="Temperature (°C)",gridcolor="#E5E8E5"); fig.update_layout(**_base_layout(390)); return fig
