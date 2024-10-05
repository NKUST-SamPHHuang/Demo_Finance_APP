import streamlit as st

def Navbar():
    with st.sidebar:
        st.page_link('Finance_Evaluation_System.py', label='投資組合評估系統', icon='🔥')
        st.page_link('pages/Charts.py', label='股價繪圖', icon='🛡️')
        st.page_link('pages/Portfolio_Selections.py', label='自選投資組合', icon='🛡️')
        st.page_link('pages/Portfolio_Analysis.py', label='投資組合分析', icon='🛡️')



