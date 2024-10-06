


import re
import requests
import pandas as pd
import streamlit as st
from io import StringIO



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
    return f"{Data['有價證券名稱']} ({Data.name})"



def get_stock_id_input(Text):
    match = re.search(r'\((.*?)\)', Text)

    if match:
        return match.group(1)
    else:
        return "沒有找到括號內的內容"
    


