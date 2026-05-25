import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from data_loader import load_data
from nav import render_nav

st.set_page_config(page_title="Similar Players", layout="wide")
render_nav("similar")
st.title("🔍 Similar Players")

df_defenders, df_midfielders, df_forwards, df_goalkeepers = load_data()

info_cols = ['Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

df_all = pd.concat([df_defenders, df_midfielders, df_forwards, df_goalkeepers], ignore_index=True)

# ── Player selection ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    teams = ['All'] + sorted(df_all['Team'].dropna().unique().tolist())
    selected_team = st.selectbox("Team", teams, key="sim_team")
with col2:
    pool = df_all if selected_team == 'All' else df_all[df_all['Team'] == selected_team]
    selected_player = st.selectbox("Player", [''] + sorted(pool['Player'].dropna().unique().tolist()), key="sim_player")

if not selected_player:
    st.info("Select a player above to find similar players.")
    st.stop()

# ── Get player role and role dataframe ────────────────────────────────────────
player_row = df_all[df_all['Player'] == selected_player].iloc[0]
role = player_row['Role']

role_df_map = {
    "Defender": df_defenders,
    "Midfielder": df_midfielders,
    "Forward": df_forwards,
    "Goalkeeper": df_goalkeepers,
}
role_df = role_df_map.get(role, df_all)
clean_metrics = [m for m in get_metric_cols(role_df) if f'{m} percentile' in role_df.columns]

st.markdown(f"**Role:** {role} — finding similar players from {len(role_df) - 1} other {role.lower()}s")
st.markdown("---")

# ── Priority metric selection ─────────────────────────────────────────────────
st.subheader("Priority Metrics")
st.markdown("Select up to **5 metrics** to prioritise — these will be weighted **5x** higher than all others.")

with st.expander("Select Priority Metrics", expanded=True):
    cols = st.columns(4)
    priority_metrics = []
    for i, metric in enumerate(clean_metrics):
        with cols[i % 4]:
            already_5 = len(priority_metrics) >= 5
            current_val = st.session_state.get(f"priority_{metric}", False)
            disabled = already_5 and not current_val
            if st.checkbox(
                metric,
                value=current_val,
                key=f"priority_{metric}",
                disabled=disabled
            ):
                priority_metrics.append(metric)

if len(priority_metrics) > 0:
    st.success(f"Priority metrics ({len(priority_metrics)}/5): {', '.join(priority_metrics)}")

st.markdown("---")

# ── Similarity calculation ────────────────────────────────────────────────────
# Build weight array — priority metrics get 5, others get 1
weight_array = np.array([5.0 if m in priority_metrics else 1.0 for m in clean_metrics])
weight_array = weight_array / weight_array.sum()

player_percentiles = np.array([player_row[f'{m} percentile'] for m in clean_metrics], dtype=float)

other_players = role_df[role_df['Player'] != selected_player].copy()

distances = []
for _, row in other_players.iterrows():
    other_percentiles = np.array([row[f'{m} percentile'] for m in clean_metrics], dtype=float)
    diff = player_percentiles - other_percentiles
    weighted_dist = np.sqrt(np.sum(weight_array * diff ** 2))
    distances.append(weighted_dist)

other_players['similarity_score'] = distances
other_players['similarity_%'] = (1 - other_players['similarity_score'] / 100).clip(0, 1) * 100

top5 = other_players.nsmallest(5, 'similarity_score')

# ── Results table ─────────────────────────────────────────────────────────────
st.subheader(f"Top 5 Most Similar Players to {selected_player}")

show_cols = info_cols + ['similarity_%']
if priority_metrics:
    show_cols += [f'{m} percentile' for m in priority_metrics if f'{m} percentile' in top5.columns]

display_df = top5[show_cols].reset_index(drop=True)
display_df['similarity_%'] = display_df['similarity_%'].round(1)
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Radar comparison ──────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Radar Comparison")

radar_metrics = priority_metrics if priority_metrics else clean_metrics[:10]

compare_players = st.multiselect(
    "Select players from the top 5 to compare on radar",
    top5['Player'].tolist(),
    default=top5['Player'].tolist()[:2],
    key="sim_radar_select"
)

if len(compare_players) >= 1 and len(radar_metrics) >= 3:
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[player_row[f'{m} percentile'] for m in radar_metrics] + [player_row[f'{radar_metrics[0]} percentile']],
        theta=radar_metrics + [radar_metrics[0]],
        fill='toself',
        name=selected_player,
        line_color='#1f77b4'
    ))

    colours = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for idx, player in enumerate(compare_players):
        row = top5[top5['Player'] == player].iloc[0]
        fig.add_trace(go.Scatterpolar(
            r=[row[f'{m} percentile'] for m in radar_metrics] + [row[f'{radar_metrics[0]} percentile']],
            theta=radar_metrics + [radar_metrics[0]],
            fill='toself',
            name=player,
            line_color=colours[idx % len(colours)],
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=600,
        title=f"{selected_player} vs Similar Players"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select at least one comparison player and ensure at least 3 priority metrics are chosen to display the radar.")
