import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def render_nav(current_page=""):
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    pages = [
    ("🏠 Home",             "app.py"),
    ("🧤 Goalkeepers",      "pages/1_Goalkeepers.py"),
    ("🛡 Defenders",        "pages/2_Defenders.py"),
    ("⚙️ Midfielders",      "pages/3_Midfielders.py"),
    ("⚡ Forwards",         "pages/4_Forwards.py"),
    ("📡 Radar",            "pages/5_Radar.py"),
    ("🔓 Released Players", "pages/6_Released_Players.py"),
    ("🔍 Similar Players",  "pages/7_Similar_Players.py"),
]

    cols = st.columns(len(pages))
    for i, (label, path) in enumerate(pages):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"nav_{current_page}_{i}"):
                st.switch_page(str(path))
    st.markdown("---")