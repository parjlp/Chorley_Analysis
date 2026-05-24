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
        ("🏠 Home",             ROOT / "app.py"),
        ("🧤 Goalkeepers",      ROOT / "pages/1_Goalkeepers.py"),
        ("🛡 Defenders",        ROOT / "pages/2_Defenders.py"),
        ("⚙️ Midfielders",      ROOT / "pages/3_Midfielders.py"),
        ("⚡ Forwards",         ROOT / "pages/4_Forwards.py"),
        ("📡 Radar",            ROOT / "pages/5_Radar.py"),
        ("🔓 Released Players", ROOT / "pages/6_Released_Players.py"),
    ]

    cols = st.columns(len(pages))
    for i, (label, path) in enumerate(pages):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"nav_{current_page}_{i}"):
                st.switch_page(str(path))
    st.markdown("---")