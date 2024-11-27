import pandas as pd
import streamlit as st

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@st.cache_data(show_spinner='Getting stock name')
def get_stock_name(ticker: str) -> str:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'https://stooq.pl/q/?s={ticker}')

        # accept cookies
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'fc-cta-consent'))
        ).click()

        # wait until the page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'f18'))
        )

        # get page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # extract stock name
        ticker_upper = f'({ticker.upper()})'
        result = ''
        for tag in soup.find_all('font', id='f18'):
            if ticker_upper in tag.text:
                result = tag.text.strip()
    finally:
        driver.quit()
    
    if result != '':
        return result
    else:
        # something went wrong
        raise Exception()


@st.cache_data(show_spinner='Downloading data')
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
