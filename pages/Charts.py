# 股價繪圖

import re
import time
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from modules.nav import Navbar
from modules.stock_ids import get_twse_stock_ids, reform_stock_infos, get_stock_id_input
from modules.write_table import show_list
from plotly.subplots import make_subplots



def get_yfinance_suffix(Symbol):
    stock_tw = yf.Ticker(f"{Symbol}.TW")
    if not stock_tw.history(period="5d").empty:
        return f"{Symbol}.TW"
    
    stock_two = yf.Ticker(f"{Symbol}.TWO")
    if not stock_two.history(period="5d").empty:
        return f"{Symbol}.TWO"
    
    stock = yf.Ticker(f"{Symbol}")
    if not stock.history(period="5d").empty:
        return f"{Symbol}"

    return None



def check_variable_exist(Variable):
    try:
        Variable
    except NameError:
        return None
    else:
        return Variable



def get_df_from_time_index(Stock, Index):
    if Index == 0:
        return Stock.history(period="ytd")
    if Index == 1:
        return Stock.history(period='1mo')
    if Index == 2:
        return Stock.history(period='3mo')
    if Index == 3:
        return Stock.history(period='6mo')
    if Index == 4:
        return Stock.history(period='1y')
    if Index == 5:
        return Stock.history(period='2y')
    if Index == 6:
        return Stock.history(period='5y')



# 導覽頁面
def main():
    Navbar()



# Page Config
st.set_page_config(page_title='股價繪圖',  layout='wide')



header = "待辦事項"
todo_list = [
    ""
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



col_a1 = st.columns(1)
container_a1 = col_a1[0].container(border=True)
with container_a1:
    # 版面設計
    col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns([1.5, 1.5, 3, 2.5, 3, 1], vertical_alignment="bottom")



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
        股票名稱選擇 = st.selectbox(
            label='選擇股票名稱與代號',
            options=股票名稱_options,
            key='stock_id',
            index=None,
            placeholder="選取股票名稱與代號...",
        )



    # 建立選時清單: Radio
    with col_b5:
        time_list = ['本年至今', '近1個月', '近3個月', '近6個月', '近1年', '近2年', '近5年']
        selected_time = st.radio(
            "選擇週期：",
            options=range(len(time_list)),
            format_func=lambda x: time_list[x],
            horizontal=True,
            index=None,
        )



    # 建立執行按鈕: Button
    with col_b6:
        button_clicked = st.button(label='執行', use_container_width=True)



    # 點擊執行後，下載資料
    if button_clicked:
        if st.session_state.stock_id is None:
            st.warning('請選擇股票！')
        else:
            symbol = get_stock_id_input(st.session_state.stock_id)
            symbol_with_suffix = get_yfinance_suffix(symbol)
            if symbol_with_suffix:
                placeholder = st.empty()
                with placeholder:
                    with st.status("資料下載中...", expanded=True) as status:
                        stock = yf.Ticker(symbol_with_suffix)
                        df = get_df_from_time_index(stock, selected_time)
                        st.dataframe(df)
                        # time.sleep(1)
                        status.update(
                            label="資料下載完成!", state="complete", expanded=False
                        )
            else:
                with st.status("資料下載中...", expanded=True) as status:
                    time.sleep(1)
                    status.update(
                        label=f'No Data: {symbol} {symbol_with_suffix}', state="complete", expanded=False
                    )



    # 下載資料後，繪製圖形
    if button_clicked and 'df' in locals():
        if not df.empty:
            # time.sleep(1)
            placeholder.empty()

            # 判斷成交量的顏色：如果收盤價高於前一日，顏色為紅色，否則為綠色
            volume_colors = ['black'] + [
                'red' if df['Close'].iloc[i] > df['Close'].iloc[i-1] else 
                'green' if df['Close'].iloc[i] < df['Close'].iloc[i-1] else 
                'black' 
                for i in range(1, len(df))
            ]
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
            data_candlestick = go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color='red',
                decreasing_line_color='green',
                name="股價"
            )
            data_volume = go.Bar(
                x=df.index,
                y=df['Volume'],
                name='成交量',
                marker_color=volume_colors
            )
            fig.add_trace(
                data_candlestick,
                row=1, col=1
            )
            fig.add_trace(
                data_volume,
                row=2, col=1
            )
            fig.update_layout(
                title=f"{st.session_state.stock_id}<br>日期：{df.index[-1]:%Y-%m-%d}，開盤價：{df['Open'].iloc[-1]:,.2f}，最高價：{df['High'].iloc[-1]:,.2f}，最低價：{df['Low'].iloc[-1]:,.2f}，收盤價：{df['Close'].iloc[-1]:,.2f}",
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                showlegend=False
            )
            fig.update_xaxes(
                title_text='日期',
                row=2, col=1
            )
            fig.update_yaxes(
                title_text='股價',
                row=1, col=1
            )
            fig.update_yaxes(
                title_text='成交量',
                row=2, col=1
            )

            # 排除非交易日的X軸位置
            full_date_range = pd.date_range(start=df.index.min(), end=df.index.max())
            missing_dates = full_date_range.difference(df.index)
            fig.update_xaxes(
                rangebreaks=[
                    dict(values=missing_dates)
                ]
            )

            st.plotly_chart(fig, use_container_width=True, theme='streamlit')



if __name__ == '__main__':
    main()



