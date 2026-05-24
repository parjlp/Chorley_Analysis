import streamlit as st

# ── Disclaimer popup ──────────────────────────────────────────────────────────
if 'disclaimer_acknowledged' not in st.session_state:
    st.session_state.disclaimer_acknowledged = False

if not st.session_state.disclaimer_acknowledged:
    @st.dialog("Important Notice")
    def show_disclaimer():
        st.write("All of the data presented in this application is from a number of publicly available data sources. There has then been some alteration of the data to allow comparisons and measurements./nHowever, this is still data relating to players physical and technical abilities and as such it should be treated in line with GDPR/nPlease only use the data to assist with decision making about players suitability to perform at the required level./nPlease do not share or reproduce this data to anyone outside of Chorley Football Club/nMany thanks")
        if st.button("I Acknowledge", use_container_width=True):
            st.session_state.disclaimer_acknowledged = True
            st.rerun()
    show_disclaimer()
    st.stop()

pg = st.navigation([
    st.Page("pages/0_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/1_Radar.py", title="Radar", icon="📡"),
    st.Page("pages/2_Released_Players.py", title="Released Players")
])

pg.run()
