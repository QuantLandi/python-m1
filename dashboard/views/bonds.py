import streamlit as st


def render() -> None:
    st.header(":material/stacked_line_chart: Bonds")
    st.caption("US Treasury curve, OECD peers, and spread analytics.")
    st.info("Phase 4 — build bonds analytics here (FRED API).")


render()
