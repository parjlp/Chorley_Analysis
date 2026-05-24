import streamlit as st

def render_nav(current_page=""):
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(8)
    pages = [
        ("🏠 Home",             "app.py"),
        ("🛡 Defenders",        "pages/3_Defenders.py"),
        ("⚙️ Midfielders",      "pages/4_Midfielders.py"),
        ("⚡ Forwards",         "pages/5_Forwards.py"),
        ("🧤 Goalkeepers",      "pages/6_Goalkeepers.py"),
        ("📡 Radar",            "pages/1_Radar.py"),
        ("🔓 Released Players", "pages/2_Released_Players.py"),
    ]
    for i, (label, path) in enumerate(pages):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"nav_{current_page}_{i}"):
                st.switch_page(path)
    st.markdown("---")