import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_data
from nav import render_nav

st.set_page_config(page_title="Defenders", layout="wide")
render_nav("defenders")

st.title("🛡 Defenders")

df_defenders, _, _, _ = load_data()

info_cols = ['Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

all_metrics = get_metric_cols(df_defenders)

# ── Filters ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    min_minutes = st.slider(
        "Minimum minutes played",
        min_value=0,
        max_value=int(df_defenders['Minutes played'].max()),
        value=0,
        step=50
    )
with col2:
    view_mode = st.radio(
        "View mode",
        ["Actual values", "Percentiles"],
        horizontal=True
    )

# ── Metric selection ───────────────────────────────────────────────────────────
with st.expander("Select Metrics", expanded=False):
    btn_col1, btn_col2, _ = st.columns([1, 1, 6])
    with btn_col1:
        if st.button("Select All", key="def_select_all"):
            for m in all_metrics:
                st.session_state[f"def_metric_{m}"] = True
    with btn_col2:
        if st.button("Deselect All", key="def_deselect_all"):
            for m in all_metrics:
                st.session_state[f"def_metric_{m}"] = False

    cols = st.columns(4)
    selected_metrics = []
    for i, metric in enumerate(all_metrics):
        with cols[i % 4]:
            if st.checkbox(metric, value=st.session_state.get(f"def_metric_{metric}", False), key=f"def_metric_{metric}"):
                selected_metrics.append(metric)

# ── Table ──────────────────────────────────────────────────────────────────────
filtered = df_defenders[df_defenders['Minutes played'] >= min_minutes]

if view_mode == "Actual values":
    display_cols = info_cols + [c for c in selected_metrics if c in filtered.columns]
else:
    display_cols = info_cols + [f'{c} percentile' for c in selected_metrics if f'{c} percentile' in filtered.columns]

st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)