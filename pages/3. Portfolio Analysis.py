# 投資組合分析

import streamlit as st
from modules.nav import Navbar



# 導覽頁面
def main():
    Navbar()



# Page Config
st.set_page_config(page_title='投資組合分析',  layout='wide')



todo_list = [
    '1. 確認使用者',
    '2. 依使用者權限讀取雲端的投資組合清單',
    '3. 持有過程分析',
    '4. 最適化過程調整',
]
st.header('待辦事項')
st.table(todo_list)



if __name__ == '__main__':
    main()




