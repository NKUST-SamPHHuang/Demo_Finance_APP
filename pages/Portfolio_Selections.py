# 自選投資組合

import re
import time
import pandas as pd
import streamlit as st
from modules.nav import Navbar
from modules.stock_ids import get_twse_stock_ids, reform_stock_infos, get_stock_id_input
from modules.write_table import show_list



# 導覽頁面
def main():
    Navbar()



# Page Config
st.set_page_config(page_title='自選投資組合',  layout='wide')



import streamlit as st
import pandas as pd
from datetime import date



header = "待辦事項"
todo_list = [
    '1. 雲端儲存',
    '2. 雲端讀取',
    '3. 確認使用者',
    '4. 依使用者權限存取',
]
show_list(header, todo_list)



# 建立股票名單後，用以放到 selectbox
# 股票名單來源：
# 證交所證券編碼查詢： https://isin.twse.com.tw/isin/class_i.jsp?kind=1
urls = [
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y",
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y",
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I&industry_code=&Page=1&chklike=Y",
    "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=3&industry_code=&Page=1&chklike=Y",
]
stock_ids_df = get_twse_stock_ids(urls)



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
    # 版面設計
    col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 1], vertical_alignment="bottom")
    # 建立選股清單: SelectBox
    with col_b1:
        # 第1個下拉清單: 市場別
        市場別_options = ['ALL'] + list(stock_ids_df['市場別'].unique())
        市場別選擇 = st.selectbox(
            label='選擇市場別',
            options=市場別_options,
            key='listed_id',
            index=None,
            placeholder="選取市場別...",
        )

        # 根據市場別選擇過濾資料清單
        filtered_data = stock_ids_df if 市場別選擇 == 'ALL' else stock_ids_df[stock_ids_df['市場別'] == 市場別選擇]

    with col_b2:
        # 第2個下拉清單: 有價證券別
        有價證券別_options = ['ALL'] + list(filtered_data['有價證券別'].dropna().unique())
        有價證券別選擇 = st.selectbox(
            label='選擇有價證券別',
            options=有價證券別_options,
            key='category_id',
            index=None,
            placeholder="有價證券別...",
        )

        # 根據市場別和有價證券別選擇過濾資料清單
        filtered_data = filtered_data if 有價證券別選擇 == 'ALL' or pd.isna(有價證券別選擇) else filtered_data[filtered_data['有價證券別'] == 有價證券別選擇]

    with col_b3:
        # 第3個下拉清單: 產業別
        產業別_options = ['ALL'] + list(filtered_data['產業別'].dropna().unique())
        產業別選擇 = st.selectbox(
            label='選擇產業別',
            options=產業別_options,
            key='industry_id',
            index=None,
            placeholder="選取產業別...",
        )

        # 根據市場別、有價證券別和產業別選擇過濾資料清單
        filtered_data = filtered_data if 產業別選擇 == 'ALL' or pd.isna(產業別選擇) else filtered_data[filtered_data['產業別'] == 產業別選擇]

    with col_b4:
        # 第4個下拉清單: 股票名稱與代號
        股票名稱_options = filtered_data.apply(lambda row: reform_stock_infos(row), axis=1).values
        stock_code = st.selectbox(
            label='選擇股票名稱與代號',
            options=股票名稱_options,
            key='stock_code',
            index=None,
            placeholder="選取股票名稱與代號...",
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


