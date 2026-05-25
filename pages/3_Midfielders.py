import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_data
from nav import render_nav

st.set_page_config(page_title="Midfielders", layout="wide")
render_nav("midfielders")

st.title("⚙️ Midfielders")

_, df_midfielders, _, _ = load_data()

info_cols = ['Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

all_metrics = get_metric_cols(df_midfielders)

col1, col2 = st.columns(2)
with col1:
    min_minutes = st.slider(
        "Minimum minutes played",
        min_value=0,
        max_value=int(df_midfielders['Minutes played'].max()),
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
        if st.button("Select All", key="mid_select_all"):
            for m in all_metrics:
                st.session_state[f"mid_metric_{m}"] = True
    with btn_col2:
        if st.button("Deselect All", key="mid_deselect_all"):
            for m in all_metrics:
                st.session_state[f"mid_metric_{m}"] = False

    cols = st.columns(4)
    selected_metrics = []
    for i, metric in enumerate(all_metrics):
        with cols[i % 4]:
            if st.checkbox(metric, value=st.session_state.get(f"mid_metric_{metric}", False), key=f"mid_metric_{metric}"):
                selected_metrics.append(metric)

filtered = df_midfielders[df_midfielders['Minutes played'] >= min_minutes]

if view_mode == "Actual values":
    display_cols = info_cols + [c for c in selected_metrics if c in filtered.columns]
else:
    display_cols = info_cols + [f'{c} percentile' for c in selected_metrics if f'{c} percentile' in filtered.columns]
# ── Shared metric columns (IMPORTANT: reuse for both tables) ────────────────

if view_mode == "Actual values":
    metric_cols = [
        c for c in selected_metrics
        if c in filtered.columns
    ]
else:
    metric_cols = [
        f"{c} percentile"
        for c in selected_metrics
        if f"{c} percentile" in filtered.columns
    ]

display_cols = info_cols + metric_cols
display_cols = [c for c in display_cols if c in filtered.columns]

st.markdown("### 🔵 Chorley Players")

chorley_df = filtered[
    filtered["Team"].str.contains("Chorley", case=False, na=False)
].copy()

if chorley_df.empty:
    st.info("No Chorley players in current selection.")
else:
    st.dataframe(
        chorley_df[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
