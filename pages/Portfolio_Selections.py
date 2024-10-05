# 自選投資組合

import re
import time
import requests
import pandas as pd
import streamlit as st
from io import StringIO
from modules.nav import Navbar



# 導覽頁面
def main():
    Navbar()



@st.cache_data
def get_twse_stock_ids(URLs):

    result = []
    for url in URLs:
        res = requests.get(url)
        text = StringIO(res.text)
        df = pd.read_html(text)[0]
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        result.append(df)
    
    
    all_df = pd.concat(result)
    all_df = all_df.set_index('有價證券代號')
    all_df = all_df.sort_index()

    return all_df



def reform_stock_infos(Data):
    return f"{Data['有價證券名稱']} ({Data.name})" \
    if pd.isna(Data['產業別']) \
    else f"{Data['有價證券名稱']} ({Data.name})"



def get_stock_id_input(Text):
    match = re.search(r'\((.*?)\)', Text)

    if match:
        return match.group(1)
    else:
        return "沒有找到括號內的內容"



# Page Config
st.set_page_config(page_title='自選投資組合',  layout='wide')



import streamlit as st
import pandas as pd
from datetime import date



todo_list = [
    '1. 雲端儲存',
    '2. 雲端讀取',
    '3. 確認使用者',
    '4. 依使用者權限存取',
]
st.header('待辦事項')
st.table(todo_list)



# 建立股票名單後，用以放到 selectbox
urls = [
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y",
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y",
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I&industry_code=&Page=1&chklike=Y",
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=3&industry_code=&Page=1&chklike=Y",
]
stock_id_df = get_twse_stock_ids(urls)
data_list = stock_id_df.apply(lambda row: reform_stock_infos(row), axis=1).values



# 初始化 Session 狀態中的股票清單
if 'stock_list' not in st.session_state:
    st.session_state.stock_list = pd.DataFrame(columns=['股票代號', '進場日期', '進場成本'])



# 分頁：顯示所有清單、新增股票、管理股票（更新、刪除）
tab1, tab2, tab3 = st.tabs(["目前股票清單", "新增股票", "管理股票(更新、刪除)"])



# 分頁 1：顯示股票清單的表格形式
with tab1:
    st.subheader("股票清單")
    if st.session_state.stock_list.empty:
        st.write("目前沒有股票紀錄")
    else:
        st.write("所有股票清單：")
        st.dataframe(st.session_state.stock_list)



# 分頁 2：新增股票功能
with tab2:
    st.subheader("新增股票")
    stock_code = st.selectbox(
            label='股票名稱與代號：',
            options=data_list,
            key='stock_code',
            index=None,
            placeholder="選取股票...",
        )
    entry_date = st.date_input("進場日期", value=date.today(), key="entry_date")
    entry_price = st.number_input("進場成本", min_value=0.0, format="%.2f", key="entry_price")

    if st.button("新增股票"):
        if stock_code and entry_price > 0:
            new_entry = pd.DataFrame({
                '股票代號': [get_stock_id_input(stock_code)],
                '進場日期': [entry_date],
                '進場成本': [entry_price]
            })
            if st.session_state.stock_list.empty:
                st.session_state.stock_list = pd.concat([new_entry], ignore_index=True)
            else:
                st.session_state.stock_list = pd.concat([st.session_state.stock_list, new_entry], ignore_index=True)
            st.success(f"股票 {stock_code} 已成功新增！")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("請輸入有效的股票代號和進場成本")



# 分頁 3：管理股票（更新、刪除功能）
with tab3:
    st.subheader("管理股票清單")
    
    if st.session_state.stock_list.empty:
        st.write("目前沒有股票紀錄")
    else:
        st.write("選擇要操作的股票")
        selected_stock = st.radio(
            "選擇一個股票進行操作",
            options=st.session_state.stock_list.index,
            format_func=lambda x: f"{st.session_state.stock_list.iloc[x]['股票代號']} | 進場日期: {st.session_state.stock_list.iloc[x]['進場日期']} | 進場成本: {st.session_state.stock_list.iloc[x]['進場成本']}",
            index=None,
        )
        
        if selected_stock is not None:
            if st.button("刪除選定股票"):
                st.session_state.stock_list = st.session_state.stock_list.drop(selected_stock).reset_index(drop=True)
                st.success("選定的股票已刪除")
                time.sleep(0.5)
                st.rerun()

            selected_row = st.session_state.stock_list.iloc[selected_stock]
            with st.expander(f"更新股票: {selected_row['股票代號']}", expanded=True):
                update_code = st.text_input("股票代號", value=selected_row['股票代號'], key="update_code")
                update_date = st.date_input("進場日期", value=pd.to_datetime(selected_row['進場日期']), key="update_date")
                update_price = st.number_input("進場成本", min_value=0.0, value=float(selected_row['進場成本']), format="%.2f", key="update_price")

                if st.button("確認更新"):
                    st.session_state.stock_list.loc[selected_stock, '股票代號'] = update_code
                    st.session_state.stock_list.loc[selected_stock, '進場日期'] = update_date
                    st.session_state.stock_list.loc[selected_stock, '進場成本'] = update_price
                    st.success(f"股票 {update_code} 已成功更新")
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.warning("請先選擇一個股票來進行操作")



if __name__ == '__main__':
    main()


