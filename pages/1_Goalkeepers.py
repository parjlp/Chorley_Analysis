import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_data
from nav import render_nav

st.set_page_config(page_title="Goalkeepers", layout="wide")
render_nav("goalkeepers")

st.title("🧤 Goalkeepers")

_, _, _, df_goalkeepers = load_data()

info_cols = ['Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

all_metrics = get_metric_cols(df_goalkeepers)

col1, col2 = st.columns(2)
with col1:
    min_minutes = st.slider(
        "Minimum minutes played",
        min_value=0,
        max_value=int(df_goalkeepers['Minutes played'].max()),
        value=0,
        step=50
    )
with col2:
    view_mode = st.radio(
        "View mode",
        ["Actual values", "Percentiles"],
        horizontal=True
    )

with st.expander("Select Metrics", expanded=False):
    btn_col1, btn_col2, _ = st.columns([1, 1, 6])
    with btn_col1:
        if st.button("Select All", key="gk_select_all"):
            for m in all_metrics:
                st.session_state[f"gk_metric_{m}"] = True
    with btn_col2:
        if st.button("Deselect All", key="gk_deselect_all"):
            for m in all_metrics:
                st.session_state[f"gk_metric_{m}"] = False

    cols = st.columns(4)
    selected_metrics = []
    for i, metric in enumerate(all_metrics):
        with cols[i % 4]:
            if st.checkbox(metric, value=st.session_state.get(f"gk_metric_{metric}", False), key=f"gk_metric_{metric}"):
                selected_metrics.append(metric)

filtered = df_goalkeepers[df_goalkeepers['Minutes played'] >= min_minutes]

if view_mode == "Actual values":
    display_cols = info_cols + [c for c in selected_metrics if c in filtered.columns]
else:
    display_cols = info_cols + [f'{c} percentile' for c in selected_metrics if f'{c} percentile' in filtered.columns]

st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)