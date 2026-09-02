from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent

st.set_page_config(
    page_title="Cross-Asset Market Monitor",
    page_icon=":material/trending_up:",
    layout="wide",
)

equities_page = st.Page(
    page=str(APP_DIR / "views" / "equities.py"),
    title="Stocks",
    icon=":material/table_chart_view:",
    default=True,
)

bonds_page = st.Page(
    page=str(APP_DIR / "views" / "bonds.py"),
    title="Bonds",
    icon=":material/stacked_line_chart:",
)

commodities_page = st.Page(
    page=str(APP_DIR / "views" / "commodities.py"),
    title="Commodities",
    icon=":material/oil_barrel:",
)

currencies_page = st.Page(
    page=str(APP_DIR / "views" / "currencies.py"),
    title="Currencies",
    icon=":material/euro_symbol:",
)

navigator = st.navigation(
    pages=[
        equities_page,
        bonds_page,
        commodities_page,
        currencies_page,
    ]
)

navigator.run()
