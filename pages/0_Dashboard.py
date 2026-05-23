import streamlit as st
import pandas as pd
import sys
from pathlib import Path

st.title("⚽ Player Dashboard")

# ── Data loading ────────────────────────────────────────────────────────────────


from data_loader import load_data
df_defenders, df_midfielders, df_forwards, df_goalkeepers = load_data()

# ── Helpers ─────────────────────────────────────────────────────────────────────

info_cols = [
    'Player',
    'Team',
    'Position',
    'Age',
    'Matches played',
    'Minutes played',
    'Role'
]

def get_metric_cols(df):
    return [
        c for c in df.columns
        if not c.endswith(' percentile') and c not in info_cols
    ]

def render_tab(df, role_name, selected_metrics):

    st.subheader(f"{role_name}s")

    col1, col2 = st.columns(2)

    with col1:
        min_minutes = st.slider(
            "Minimum minutes played",
            min_value=0,
            max_value=int(df['Minutes played'].max()),
            value=0,
            step=50,
            key=f"mins_{role_name}"
        )

    with col2:
        view_mode = st.radio(
            "View mode",
            ["Actual values", "Percentiles"],
            horizontal=True,
            key=f"mode_{role_name}"
        )

    filtered = df[df['Minutes played'] >= min_minutes]

    if view_mode == "Actual values":
        display_cols = info_cols + [
            c for c in selected_metrics if c in filtered.columns
        ]
    else:
        display_cols = info_cols + [
            f'{c} percentile'
            for c in selected_metrics
            if f'{c} percentile' in filtered.columns
        ]

    st.dataframe(
        filtered[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# ── Sidebar ─────────────────────────────────────────────────────────────────────

role_df_map = {
    "Defender": df_defenders,
    "Midfielder": df_midfielders,
    "Forward": df_forwards,
    "Goalkeeper": df_goalkeepers,
}

with st.sidebar:

    active_role = st.selectbox(
        "Select Role",
        list(role_df_map.keys())
    )

    st.markdown("---")

    st.header(f"{active_role} Metrics")

    metrics = get_metric_cols(role_df_map[active_role])

    selected_metrics = []

    for metric in metrics:
        if st.checkbox(
            metric,
            value=False,
            key=f"cb_{active_role}_{metric}"
        ):
            selected_metrics.append(metric)

# ── Tabs ────────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🛡 Defenders",
    "⚙️ Midfielders",
    "⚡ Forwards",
    "🧤 Goalkeepers"
])

with tab1:
    render_tab(
        df_defenders,
        "Defender",
        selected_metrics if active_role == "Defender"
        else get_metric_cols(df_defenders)
    )

with tab2:
    render_tab(
        df_midfielders,
        "Midfielder",
        selected_metrics if active_role == "Midfielder"
        else get_metric_cols(df_midfielders)
    )

with tab3:
    render_tab(
        df_forwards,
        "Forward",
        selected_metrics if active_role == "Forward"
        else get_metric_cols(df_forwards)
    )

with tab4:
    render_tab(
        df_goalkeepers,
        "Goalkeeper",
        selected_metrics if active_role == "Goalkeeper"
        else get_metric_cols(df_goalkeepers)
    )