import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def get_stock_data(ticker: str) -> pd.DataFrame:
    """This function takes a ticker as an argument and returns 
    a dataframe containing stock data gathered from stooq.pl
    """

    df = pd.read_csv(f'https://stooq.pl/q/d/l/?s={ticker}' + '&i=d', index_col=0, parse_dates=[0])
    if len(df) == 0:
        raise FileNotFoundError('No data for this ticker')
    
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df.index.name = None
    return df
