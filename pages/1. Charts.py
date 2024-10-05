# 股價繪圖

import re
import time
import requests
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from io import StringIO
from modules.nav import Navbar
from plotly.subplots import make_subplots



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



def get_stock_id_input(Text):
    match = re.search(r'\((.*?)\)', Text)

    if match:
        return match.group(1)
    else:
        return "沒有找到括號內的內容"



def reform_stock_infos(Data):
    return f"{Data['有價證券名稱']} ({Data.name})" \
    if pd.isna(Data['產業別']) \
    else f"{Data['有價證券名稱']} ({Data.name})"
    # return f"{Data['有價證券名稱']} ({Data.name}) - {Data['市場別']}" \
    # if pd.isna(Data['產業別']) \
    # else f"{Data['有價證券名稱']} ({Data.name}) - {Data['市場別']} - {Data['產業別']}"



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


col_a1 = st.columns(1)
container_a1 = col_a1[0].container(border=True)
with container_a1:
    # 版面設計
    col_b1, col_b2, col_b3 = st.columns([1, 3, 1], vertical_alignment="bottom")



    # 建立股票名單後，用以放到 selectbox
    urls = [
        "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y",
        "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y",
        "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=I&industry_code=&Page=1&chklike=Y",
        "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=3&industry_code=&Page=1&chklike=Y",
    ]
    stock_id_df = get_twse_stock_ids(urls)
    data_list = stock_id_df.apply(lambda row: reform_stock_infos(row), axis=1).values
    


    # 建立選股清單: SelectBox
    with col_b1:
        st.selectbox(
            label='股票名稱與代號：',
            options=data_list,
            key='stock_id',
            index=None,
            placeholder="選取股票...",
        )
        


    # 建立選時清單: Radio
    with col_b2:
        time_list = ['本年至今', '近1個月', '近3個月', '近6個月', '近1年', '近2年', '近5年']
        selected_time = st.radio(
            "選擇週期",
            options=range(len(time_list)),
            format_func=lambda x: time_list[x],
            horizontal=True,
            index=None,
        )



    # 建立執行按鈕: Button
    with col_b3:
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


