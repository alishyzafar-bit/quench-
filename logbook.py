import pandas as pd
import streamlit as st


def _run_label(index, run):
    result = run["result"]
    return (
        f"Run {index + 1} — {run.get('saved_at', '—')} | "
        f"{run['carbon']:.2f}% C | {run['cooling_rate']:.1f} °C/s | {result['primary_phase']}"
    )


def render_logbook():
    st.markdown("### Run logbook")
    st.caption("Saved simulations live in the current browser session and can be exported as CSV.")

    if not st.session_state.runs:
        st.info("No saved runs yet. Return to Simulator, adjust the inputs, and press “Save run”.")
        return

    rows = []
    for index, run in enumerate(st.session_state.runs, 1):
        result = run["result"]
        rows.append(
            {
                "#": index,
                "Saved": run.get("saved_at", "—"),
                "C (wt%)": round(run["carbon"], 2),
                "Aust. (°C)": run["aust_temp"],
                "Medium": run["medium"],
                "Rate (°C/s)": round(run["cooling_rate"], 1),
                "Primary phase": result["primary_phase"],
                "Hardness (HRC)": round(result["hardness"], 1),
                "Tensile (MPa)": round(result["tensile"]),
                "Ms (°C)": round(result["Ms"]),
                "Mf* (°C)": round(result["Mf"]),
            }
        )

    table = pd.DataFrame(rows)
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("### Compare saved runs")
    if len(st.session_state.runs) < 2:
        st.caption("Save at least two runs to compare how changing the inputs affects the screening results.")
    else:
        labels = [_run_label(i, run) for i, run in enumerate(st.session_state.runs)]
        c1, c2 = st.columns(2)
        with c1:
            first_index = st.selectbox("First run", range(len(labels)), format_func=lambda i: labels[i], index=0, key="compare_first")
        with c2:
            default_second = 1 if first_index == 0 else 0
            second_index = st.selectbox("Second run", range(len(labels)), format_func=lambda i: labels[i], index=default_second, key="compare_second")

        if first_index == second_index:
            st.warning("Choose two different runs to compare.")
        else:
            a = st.session_state.runs[first_index]["result"]
            b = st.session_state.runs[second_index]["result"]
            ca, cb, cd = st.columns(3)
            with ca:
                st.markdown("**Run A**")
                st.write(f"{st.session_state.runs[first_index]['carbon']:.2f}% C • {st.session_state.runs[first_index]['cooling_rate']:.1f} °C/s")
                st.write(f"Primary: **{a['primary_phase']}**")
            with cb:
                st.markdown("**Run B**")
                st.write(f"{st.session_state.runs[second_index]['carbon']:.2f}% C • {st.session_state.runs[second_index]['cooling_rate']:.1f} °C/s")
                st.write(f"Primary: **{b['primary_phase']}**")
            with cd:
                st.markdown("**B − A**")
                st.write(f"Hardness: **{b['hardness'] - a['hardness']:+.1f} HRC**")
                st.write(f"Tensile: **{b['tensile'] - a['tensile']:+.0f} MPa**")
                st.write(f"Martensite: **{b['phases']['Martensite'] - a['phases']['Martensite']:+.1f} pp**")

            comparison = pd.DataFrame(
                {
                    "Metric": ["Martensite", "Bainite", "Pearlite", "Ferrite", "Cementite", "Hardness", "Tensile", "Yield", "Ms", "Mf*"],
                    "Run A": [a["phases"][p] for p in ["Martensite", "Bainite", "Pearlite", "Ferrite", "Cementite"]] + [a["hardness"], a["tensile"], a["yield_strength"], a["Ms"], a["Mf"]],
                    "Run B": [b["phases"][p] for p in ["Martensite", "Bainite", "Pearlite", "Ferrite", "Cementite"]] + [b["hardness"], b["tensile"], b["yield_strength"], b["Ms"], b["Mf"]],
                }
            )
            comparison["B − A"] = comparison["Run B"] - comparison["Run A"]
            st.dataframe(comparison.round(2), use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "↓ Export logbook CSV",
            table.to_csv(index=False).encode("utf-8"),
            file_name="quenchiq_logbook.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        if st.button("Clear logbook", use_container_width=True):
            st.session_state.runs = []
            st.rerun()
