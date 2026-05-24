import streamlit as st

st.set_page_config(page_title="Player Dashboard", layout="wide")

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from nav import render_nav
render_nav("home")

# ── Disclaimer ─────────────────────────────────────────────────────────────────
if 'disclaimer_acknowledged' not in st.session_state:
    st.session_state.disclaimer_acknowledged = False

if not st.session_state.disclaimer_acknowledged:
    @st.dialog("Important Notice")
    def show_disclaimer():
        st.write("""All data presented in this application is sourced from publicly available sources 
        and has been processed to allow comparisons and performance measurements.

This data relates to players' personal, physical and technical attributes and must be 
treated in accordance with GDPR regulations.

Please use this data solely to assist with recruitment or development decisions 
regarding player suitability.

Do not share or reproduce this data outside of Chroely Football Club.

Thank you.""")
        if st.button("I Acknowledge", use_container_width=True):
            st.session_state.disclaimer_acknowledged = True
            st.rerun()
    show_disclaimer()
    st.stop()

st.title("⚽ Player Dashboard")
st.markdown("Select a role from the navigation to view player data.")