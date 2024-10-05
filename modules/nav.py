import streamlit as st

def Navbar():
    with st.sidebar:
        st.page_link('Finance Evaluation System.py', label='投資組合評估系統', icon='🔥')
        st.page_link('pages/1. Charts.py', label='股價繪圖', icon='🛡️')
        st.page_link('pages/2. Portfolio Selections.py', label='自選投資組合', icon='🛡️')
        st.page_link('pages/3. Portfolio Analysis.py', label='投資組合分析', icon='🛡️')



