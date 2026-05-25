import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from data_loader import load_data
from nav import render_nav

st.set_page_config(page_title="Player Upgrade", layout="wide")
render_nav("upgrade")
st.title("⬆️ Player Upgrade Finder")
st.markdown("Find players who are **better on your priority metrics** and **similar on everything else**.")

df_defenders, df_midfielders, df_forwards, df_goalkeepers = load_data()

info_cols = ['Player', 'Team', 'Position', 'Age', 'Matches played', 'Minutes played', 'Role']

def get_metric_cols(df):
    return [c for c in df.columns if not c.endswith(' percentile') and c not in info_cols]

df_all = pd.concat([df_defenders, df_midfielders, df_forwards, df_goalkeepers], ignore_index=True)

# ── Player selection ──────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    teams = ['All'] + sorted(df_all['Team'].dropna().unique().tolist())
    selected_team = st.selectbox("Team", teams, key="upg_team")
with col2:
    pool = df_all if selected_team == 'All' else df_all[df_all['Team'] == selected_team]
    selected_player = st.selectbox("Player", [''] + sorted(pool['Player'].dropna().unique().tolist()), key="upg_player")
with col3:
    num_results = st.number_input("Number of results", min_value=1, max_value=50, value=10, step=1)

if not selected_player:
    st.info("Select a player above to find upgrades.")
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

st.markdown(f"**Role:** {role} — searching across {len(role_df) - 1} other {role.lower()}s")
st.markdown("---")

# ── Priority metric selection ─────────────────────────────────────────────────
st.subheader("Priority Metrics")
st.markdown("Select up to **5 metrics** where you want the replacement to be **better**. All other metrics will be used for similarity matching.")

with st.expander("Select Priority Metrics", expanded=True):
    cols = st.columns(4)
    priority_metrics = []
    for i, metric in enumerate(clean_metrics):
        with cols[i % 4]:
            already_5 = len(priority_metrics) >= 5
            current_val = st.session_state.get(f"upg_priority_{metric}", False)
            disabled = already_5 and not current_val
            if st.checkbox(
                metric,
                value=current_val,
                key=f"upg_priority_{metric}",
                disabled=disabled
            ):
                priority_metrics.append(metric)

if priority_metrics:
    st.success(f"Priority metrics ({len(priority_metrics)}/5): {', '.join(priority_metrics)}")

st.markdown("---")

# ── Scoring ───────────────────────────────────────────────────────────────────
# For each candidate player:
# - Upgrade score: average percentile improvement on priority metrics (higher = better)
# - Similarity score: weighted euclidean distance on non-priority metrics (lower = better)
# - Combined score: upgrade score - similarity penalty

other_players = role_df[role_df['Player'] != selected_player].copy()
non_priority_metrics = [m for m in clean_metrics if m not in priority_metrics]

results = []
for _, row in other_players.iterrows():

    # ── Upgrade score on priority metrics ──
    if priority_metrics:
        priority_diffs = []
        for m in priority_metrics:
            candidate_val = row[f'{m} percentile']
            player_val = player_row[f'{m} percentile']
            priority_diffs.append(candidate_val - player_val)
        upgrade_score = np.mean(priority_diffs)  # positive = better than selected player
    else:
        upgrade_score = 0

    # ── Similarity score on non-priority metrics ──
    if non_priority_metrics:
        non_priority_diffs = np.array([
            row[f'{m} percentile'] - player_row[f'{m} percentile']
            for m in non_priority_metrics
        ], dtype=float)
        similarity_penalty = np.sqrt(np.mean(non_priority_diffs ** 2))  # RMSE — lower = more similar
    else:
        similarity_penalty = 0

    # ── Combined score: reward being better, penalise being different elsewhere ──
    # Normalise both to roughly same scale — upgrade_score range ~-100 to 100, penalty ~0 to 100
    combined = upgrade_score - (similarity_penalty * 0.5)

    results.append({
        'Player': row['Player'],
        'Team': row['Team'],
        'Position': row['Position'],
        'Age': row['Age'],
        'Matches played': row['Matches played'],
        'Minutes played': row['Minutes played'],
        'Role': row['Role'],
        'upgrade_score': round(upgrade_score, 1),
        'similarity_penalty': round(similarity_penalty, 1),
        'combined_score': round(combined, 1),
    })

results_df = pd.DataFrame(results)

# Add priority metric percentiles to results
for m in priority_metrics:
    col_name = f'{m} percentile'
    results_df[col_name] = results_df['Player'].map(
        role_df.set_index('Player')[col_name]
    )

# ── Filter to only players who are better on at least one priority metric ──
if priority_metrics:
    better_mask = results_df['upgrade_score'] > -10  # allows slightly worse but still close
    results_df = results_df[better_mask]

results_df = results_df.sort_values('combined_score', ascending=False).head(int(num_results))

# ── Results table ─────────────────────────────────────────────────────────────
st.subheader(f"Top {int(num_results)} Upgrade Candidates for {selected_player}")

# Show selected player's values for reference
st.markdown("**Selected player's priority metric percentiles:**")
if priority_metrics:
    ref_data = {m: round(player_row[f'{m} percentile'], 1) for m in priority_metrics}
    st.dataframe(pd.DataFrame([ref_data]), use_container_width=True, hide_index=True)

st.markdown("**Upgrade candidates:**")

display_cols = ['Player', 'Team', 'Position', 'Age', 'upgrade_score', 'similarity_penalty'] + \
               [f'{m} percentile' for m in priority_metrics if f'{m} percentile' in results_df.columns]

st.dataframe(
    results_df[display_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        'upgrade_score': st.column_config.NumberColumn('Upgrade Score', help='Average percentile improvement on priority metrics. Positive = better than selected player.'),
        'similarity_penalty': st.column_config.NumberColumn('Similarity Gap', help='How different they are on non-priority metrics. Lower = more similar overall.'),
    }
)

# ── Radar comparison ──────────────────────────────────────────────────────────
if priority_metrics and len(results_df) > 0:
    st.markdown("---")
    st.subheader("Radar Comparison")

    compare_players = st.multiselect(
        "Select candidates to compare on radar",
        results_df['Player'].tolist(),
        default=results_df['Player'].tolist()[:2],
        key="upg_radar_select"
    )

    radar_metrics = priority_metrics if len(priority_metrics) >= 3 else clean_metrics[:10]

    if len(compare_players) >= 1 and len(radar_metrics) >= 3:
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[player_row[f'{m} percentile'] for m in radar_metrics] + [player_row[f'{radar_metrics[0]} percentile']],
            theta=radar_metrics + [radar_metrics[0]],
            fill='toself',
            name=f"{selected_player} (selected)",
            line_color='#1f77b4'
        ))

        colours = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        for idx, player in enumerate(compare_players):
            row = role_df[role_df['Player'] == player].iloc[0]
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
            title=f"Upgrade Comparison — {selected_player}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one candidate and 3 priority metrics to show the radar.")