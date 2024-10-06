# Financial Independence Retire Early, FIRE

import streamlit as st
from modules.nav import Navbar
from modules.write_table import show_list



# 導覽頁面
def main():
    Navbar()



# Page Config
st.set_page_config(page_title='財務獨立分析',  layout='wide')



# 待辦事項
header = "待辦事項"
todo_list = [
    '1. 可以基於目前的商品評估現金流',
]
show_list(header, todo_list)



header = "FIRE是什麼？"
text = """
所謂 FIRE（Financial Independence Retire Early）意思是「財務獨立，提早退休」。透過理財投資，累積財富買回自己人生的時間，在擁有了支配時間的權利後，就可以做自己想做的事情，實踐自我價值。簡單來說，道理與財富自由的概念相同。
"""
with st.container():
    st.header(header)
    st.markdown(text)



if __name__ == '__main__':
    main()





