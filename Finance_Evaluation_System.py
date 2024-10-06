# 投資組合評估系統

import streamlit as st
from modules.nav import Navbar
from modules.write_table import show_list

# Page Config
st.set_page_config(page_title='投資組合評估系統',  layout='wide')



# 導覽頁面
def main():
    Navbar()



header = "系統說明"
todo_list = [
    '1. 股價繪圖',
    '2. 技術分析',
    '3. 基本分析',
    '4. 自選投資組合',
    '5. 投資組合分析',
    '6. 財務獨立分析',
]
show_list(header, todo_list)



if __name__ == '__main__':
    main()


