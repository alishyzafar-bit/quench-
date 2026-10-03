import numpy as np
import plotly.graph_objects as go

from simulation.engine import screening_nose

PHASE_COLORS = {
    "Martensite": "#F07C8E",
    "Bainite": "#F5B942",
    "Pearlite": "#8B7CF6",
    "Ferrite": "#55D6BE",
    "Cementite": "#A8B0BE",
}


def _base_layout(height=430):
    return dict(
        height=height,
        margin=dict(l=58, r=20, t=35, b=55),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#10141C",
        font=dict(color="#9299A8"),
        hoverlabel=dict(bgcolor="#151A24", font_color="#F4F1EA"),
        legend=dict(orientation="h", y=1.04, x=0),
    )


def make_phase_chart(result):
    labels = [name for name, value in result["phases"].items() if value > 0.05]
    values = [result["phases"][name] for name in labels]
    colors = [PHASE_COLORS[name] for name in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        marker=dict(colors=colors, line=dict(color="#10141C", width=3)),
        textinfo="percent",
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        sort=False,
    ))
    fig.add_annotation(
        text=f"<b>{result['primary_phase']}</b><br><span style='font-size:12px'>dominant estimate</span>",
        x=.5, y=.5, showarrow=False, font=dict(size=14, color="#F4F1EA")
    )
    layout = _base_layout(320)
    layout["margin"] = dict(l=10, r=10, t=15, b=15)
    fig.update_layout(**layout)
    fig.update_layout(legend=dict(orientation="h", y=-0.02, x=0.02))
    return fig


def make_transformation_chart(result, carbon, aust_temp, cooling_rate):
    """Create a clearly labelled CCT-style educational screening map.

    The transformation boundaries are illustrative, not experimental data. The
    cooling path, Ms and Mf are internally linked to the current inputs.
    """
    time = np.logspace(-2, 4, 360)
    log_t = np.log10(time)

    # The nose shifts with carbon in a qualitative way. This is intentionally
    # labelled as a screening map rather than an alloy-specific CCT diagram.
    nose_temp, nose_time, _critical_rate = screening_nose(carbon, aust_temp)
    width = 1.0

    pearlite_start = nose_temp - 35 * np.exp(-((log_t - np.log10(nose_time)) / width) ** 2)
    pearlite_finish = pearlite_start - 75

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time, y=pearlite_start, mode="lines", name="Diffusional start (schematic)",
        line=dict(color="#8B7CF6", width=2),
        hovertemplate="t=%{x:.3g} s<br>T=%{y:.0f} °C<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=time, y=pearlite_finish, mode="lines", name="Diffusional finish (schematic)",
        line=dict(color="#8B7CF6", width=2, dash="dash"),
        hovertemplate="t=%{x:.3g} s<br>T=%{y:.0f} °C<extra></extra>",
    ))

    # Cooling path for a constant nominal rate: t = ΔT / rate.
    path_temp = np.linspace(aust_temp, 60, 240)
    path_time = np.maximum((aust_temp - path_temp) / cooling_rate, 0.001)
    fig.add_trace(go.Scatter(
        x=path_time, y=path_temp, mode="lines", name="Selected cooling path",
        line=dict(color="#F5B942", width=3),
        hovertemplate="t=%{x:.3g} s<br>T=%{y:.0f} °C<extra></extra>",
    ))

    fig.add_hline(
        y=result["Ms"], line=dict(color="#55D6BE", dash="dot", width=1.5),
        annotation_text=f"Ms {result['Ms']:.0f} °C", annotation_position="top right"
    )
    fig.add_hline(
        y=result["Mf"], line=dict(color="#55D6BE", dash="dot", width=1.5),
        annotation_text=f"Mf* {result['Mf']:.0f} °C", annotation_position="bottom right"
    )
    boundary = result["critical_boundary"]
    boundary_temp = result["critical_temperature"]
    if boundary == "A1":
        boundary_label = "A1 727 °C"
    else:
        boundary_label = f"{boundary} {boundary_temp:.0f} °C"
    fig.add_hline(
        y=boundary_temp, line=dict(color="#A8B0BE", dash="dot", width=1),
        annotation_text=boundary_label, annotation_position="left"
    )
    fig.add_annotation(
        text="SCHEMATIC / EDUCATIONAL — NOT EXPERIMENTAL CCT DATA",
        xref="paper", yref="paper", x=0.5, y=1.08, showarrow=False,
        font=dict(size=11, color="#F5B942")
    )

    fig.update_xaxes(type="log", title="Time (s)", gridcolor="#252C38", color="#9299A8")
    fig.update_yaxes(
        title="Temperature (°C)",
        range=[50, max(850, aust_temp + 40)],
        gridcolor="#252C38", color="#9299A8",
    )
    fig.update_layout(**_base_layout(475))
    return fig
