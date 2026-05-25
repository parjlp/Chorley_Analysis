import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from data_loader import load_data
from nav import render_nav

st.set_page_config(page_title="Released Players", layout="wide")
render_nav("released")
st.title("🔓 Released Players")

# ── Load data ──────────────────────────────────────────────────────────────────
df_defenders, df_midfielders, df_forwards, df_goalkeepers = load_data()

df_all = pd.concat(
    [df_defenders, df_midfielders, df_forwards, df_goalkeepers],
    ignore_index=True
)

# ── Filter to released players ─────────────────────────────────────────────────
if 'Due For Release' not in df_all.columns:
    st.error("Column 'Due For Release' not found in data. Please check your all_divisions.xlsx file.")
    st.stop()

released = df_all[df_all['Due For Release'] == 1].copy()

if released.empty:
    st.warning("No released players found.")
    st.stop()

st.markdown(f"**{len(released)} released players found**")

# ── Helpers ────────────────────────────────────────────────────────────────────
info_cols = ['Player', 'Team', 'Division', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

# ── Filters ────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    roles = ['All'] + sorted(released['Role'].dropna().unique().tolist())
    selected_role = st.selectbox("Filter by Role", roles)
with col2:
    divisions = ['All'] + sorted(released['Division'].dropna().unique().tolist())
    selected_division = st.selectbox("Filter by Division", divisions)
with col3:
    view_mode = st.radio("View mode", ["Actual values", "Percentiles"], horizontal=True)

filtered = released.copy()
if selected_role != 'All':
    filtered = filtered[filtered['Role'] == selected_role]
if selected_division != 'All':
    filtered = filtered[filtered['Division'] == selected_division]

# ── Metric selection ───────────────────────────────────────────────────────────
all_metrics = get_metric_cols(filtered)

with st.expander("Select Metrics", expanded=False):
    btn_col1, btn_col2, _ = st.columns([1, 1, 6])
    with btn_col1:
        if st.button("Select All", key="rel_select_all"):
            for m in all_metrics:
                st.session_state[f"rel_metric_{m}"] = True
    with btn_col2:
        if st.button("Deselect All", key="rel_deselect_all"):
            for m in all_metrics:
                st.session_state[f"rel_metric_{m}"] = False

    cols = st.columns(4)
    selected_metrics = []
    for i, metric in enumerate(all_metrics):
        with cols[i % 4]:
            if st.checkbox(metric, value=st.session_state.get(f"rel_metric_{metric}", False), key=f"rel_metric_{metric}"):
                selected_metrics.append(metric)

# ── Build display columns ──────────────────────────────────────────────────────
if view_mode == "Actual values":
    display_cols = info_cols + [c for c in selected_metrics if c in filtered.columns]
else:
    display_cols = info_cols + [f'{c} percentile' for c in selected_metrics if f'{c} percentile' in filtered.columns]

display_cols = [c for c in display_cols if c in filtered.columns]

# ── Table ──────────────────────────────────────────────────────────────────────
st.dataframe(
    filtered[display_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)
