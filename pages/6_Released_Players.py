import streamlit as st
import pandas as pd
import sys
import os
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

released_path = Path(__file__).resolve().parents[1] / "Players" / "Released Players.xlsx"

if not released_path.exists():
    st.error(f"Missing file:\n{released_path}")
    st.stop()

df_released = pd.read_excel(released_path)

# ── CLEANING ───────────────────────────────────────────────────────────────────
def clean(x):
    if pd.isna(x):
        return ""
    x = str(x)
    x = unicodedata.normalize("NFKD", x)
    x = re.sub(r"[^\w\s]", "", x)
    return x.lower().strip()

def get_surname(x):
    return str(x).split()[-1].lower().strip() if pd.notna(x) else ""

# ── BUILD KEYS ────────────────────────────────────────────────────────────────
df_all["team_key"] = df_all["Team"].apply(clean)
df_all["surname_key"] = df_all["Player"].apply(get_surname)
df_all["first_initial"] = df_all["Player"].apply(
    lambda x: str(x)[0].lower() if pd.notna(x) else ""
)

df_all = df_all.drop_duplicates(subset=["Player", "Team"]).copy()

df_released["team_key"] = df_released.iloc[:, 2].fillna("").astype(str).apply(clean)

df_released["surname_key"] = (
    df_released.iloc[:, 0].fillna("").astype(str) + " " +
    df_released.iloc[:, 1].fillna("").astype(str)
).apply(clean).apply(lambda x: x.split()[-1] if x else "")

df_released["first_initial"] = df_released.iloc[:, 0].fillna("").astype(str).apply(
    lambda x: x[0].lower() if x else ""
)

df_released = df_released.drop_duplicates()

# ── MATCHING ENGINE (BALANCED FIX) ────────────────────────────────────────────
matched_rows = []

for _, r in df_released.iterrows():

    r_surname = r["surname_key"]
    r_team = r["team_key"]
    r_initial = r["first_initial"]

    if not r_surname:
        continue

    # STEP 1: primary match (surname)
    pool = df_all[df_all["surname_key"] == r_surname].copy()

    # STEP 2: fallback match (initial if surname fails)
    if pool.empty:
        pool = df_all[df_all["first_initial"] == r_initial].copy()

    # STEP 3: if still empty, skip
    if pool.empty:
        continue

    # STEP 4: scoring system (no blocking, just ranking)
    def score(row):
        team_score = 1 if (
            r_team in row["team_key"] or row["team_key"] in r_team
        ) else 0

        initial_score = 1 if row["first_initial"] == r_initial else 0

        return (team_score * 2) + initial_score

    pool["score"] = pool.apply(score, axis=1)

    best_match = pool.sort_values("score", ascending=False).iloc[0]

    matched_rows.append(best_match)

matched = pd.DataFrame(matched_rows)

# final dedupe safety (only here, not earlier)
matched = matched.drop_duplicates(subset=["Player", "Team"])

st.write(f"Matched players: {len(matched)}")

if matched.empty:
    st.warning("No matches found — check naming or dataset structure")
    st.stop()

# ── DISPLAY ───────────────────────────────────────────────────────────────────
info_cols = [
    "Player", "Team", "Position", "Age",
    "Matches played", "Minutes played", "Role"
]

def metric_cols(df):
    return [
        c for c in df.columns
        if c not in info_cols and not c.endswith(" percentile")
    ]

with st.sidebar:
    st.subheader("Filters")

    if "Role" in matched.columns:
        roles = ["All"] + sorted(matched["Role"].dropna().astype(str).unique().tolist())
    else:
        roles = ["All"]

    role = st.selectbox("Role", roles)

    if role == "All":
        filtered = matched.copy()
    else:
        filtered = matched[matched["Role"].astype(str) == role].copy()

    metrics = metric_cols(filtered)

    selected_metrics = [
        m for m in metrics
        if st.checkbox(m, key=f"m_{m}")
    ]

display_df = filtered.copy()

cols = info_cols + selected_metrics if selected_metrics else info_cols
cols = [c for c in cols if c in display_df.columns]

st.markdown(f"**{len(display_df)} released players found**")

if display_df.empty:
    st.warning("No players match the current filters.")
    st.stop()

st.dataframe(
    display_df[cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)