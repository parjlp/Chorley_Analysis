import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/1_Radar.py", title="Radar", icon="📡"),
    st.Page("pages/2_Released_Players.py", title="Released Players")
])

pg.run()