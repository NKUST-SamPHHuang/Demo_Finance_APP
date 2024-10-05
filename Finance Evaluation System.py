# 投資組合評估系統

import streamlit as st
from modules.nav import Navbar

# Page Config
st.set_page_config(page_title='投資組合評估系統',  layout='wide')



# 導覽頁面
def main():
    Navbar()


todo_list = [
    '1. 股價繪圖',
    '2. 自選投資組合',
    '3. 投資組合分析',
]
st.header('系統說明')
st.table(todo_list)


if __name__ == '__main__':
    main()


