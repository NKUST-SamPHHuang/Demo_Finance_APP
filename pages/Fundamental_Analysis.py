
import streamlit as st
from modules.nav import Navbar
from modules.write_table import show_list



# 導覽頁面
def main():
    Navbar()



# Page Config
st.set_page_config(page_title='基本分析',  layout='wide')



# 待辦事項
header = "待辦事項"
todo_list = [
    '1. 可以複選財報指標和週期',
]
show_list(header, todo_list)



if __name__ == '__main__':
    main()





