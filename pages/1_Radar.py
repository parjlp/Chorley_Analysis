import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os


from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from data_loader import load_data

st.set_page_config(page_title="Player Radar", layout="wide")


st.markdown("---")
st.title("📡 Player Radar")

df_defenders, df_midfielders, df_forwards, df_goalkeepers = load_data()

info_cols = ['Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

df_all = pd.concat([df_defenders, df_midfielders, df_forwards, df_goalkeepers], ignore_index=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Player 1")
    teams_1 = ['All'] + sorted(df_all['Team'].dropna().unique().tolist())
    team_1 = st.selectbox("Team", teams_1, key="team_1")
    pool_1 = df_all if team_1 == 'All' else df_all[df_all['Team'] == team_1]
    player_1 = st.selectbox("Player", [''] + sorted(pool_1['Player'].dropna().unique().tolist()), key="player_1")

    st.markdown("---")

    st.header("Player 2")
    teams_2 = ['All'] + sorted(df_all['Team'].dropna().unique().tolist())
    team_2 = st.selectbox("Team", teams_2, key="team_2")
    pool_2 = df_all if team_2 == 'All' else df_all[df_all['Team'] == team_2]
    player_2 = st.selectbox("Player", [''] + sorted(pool_2['Player'].dropna().unique().tolist()), key="player_2")

    st.markdown("---")

    # ── Metric selection based on first selected player's role ──
    st.header("Metrics")
    ref_player = player_1 or player_2
    if ref_player:
        role = df_all[df_all['Player'] == ref_player].iloc[0]['Role']
        role_df_map = {
            "Defender": df_defenders,
            "Midfielder": df_midfielders,
            "Forward": df_forwards,
            "Goalkeeper": df_goalkeepers,
        }
        role_df = role_df_map.get(role, df_all)
        available_metrics = get_metric_cols(role_df)
        selected_metrics = []
        for metric in available_metrics:
            if st.checkbox(metric, value=False, key=f"radar_cb_{metric}"):
                selected_metrics.append(metric)
    else:
        st.info("Select a player to see available metrics.")
        selected_metrics = []

# ── Main content ─────────────────────────────────────────────────────────────
if not player_1 and not player_2:
    st.info("Select at least one player from the sidebar to get started.")
else:
    # Build percentile cols from selected metrics
    percentile_cols = [f'{c} percentile' for c in selected_metrics if f'{c} percentile' in df_all.columns]
    radar_labels = [c for c in selected_metrics if f'{c} percentile' in df_all.columns]

    if len(percentile_cols) < 3:
        st.info("Select at least 3 metrics in the sidebar to display the radar chart.")
    else:
        fig = go.Figure()

        if player_1:
            row_1 = df_all[df_all['Player'] == player_1].iloc[0]
            fig.add_trace(go.Scatterpolar(
                r=[row_1[c] for c in percentile_cols] + [row_1[percentile_cols[0]]],
                theta=radar_labels + [radar_labels[0]],
                fill='toself',
                name=player_1,
                line_color='#1f77b4'
            ))

        if player_2:
            row_2 = df_all[df_all['Player'] == player_2].iloc[0]
            fig.add_trace(go.Scatterpolar(
                r=[row_2[c] for c in percentile_cols] + [row_2[percentile_cols[0]]],
                theta=radar_labels + [radar_labels[0]],
                fill='toself',
                name=player_2,
                line_color='#ff7f0e',
                opacity=0.7
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=600,
            title="Player Comparison — Percentile Radar"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Stat comparison table ──
        if selected_metrics:
            st.markdown("---")
            st.subheader("Stats Comparison")

            rows = []
            for metric in selected_metrics:
                pct_col = f'{metric} percentile'
                row = {'Metric': metric}
                if player_1:
                    r1 = df_all[df_all['Player'] == player_1].iloc[0]
                    row[f'{player_1} (value)'] = r1.get(metric, 'N/A')
                    row[f'{player_1} (percentile)'] = r1.get(pct_col, 'N/A')
                if player_2:
                    r2 = df_all[df_all['Player'] == player_2].iloc[0]
                    row[f'{player_2} (value)'] = r2.get(metric, 'N/A')
                    row[f'{player_2} (percentile)'] = r2.get(pct_col, 'N/A')
                rows.append(row)

            comparison_df = pd.DataFrame(rows)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)