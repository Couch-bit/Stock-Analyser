import pandas as pd
import streamlit as st

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def format_ticker(ticker: str) -> str:
    """Formats given ticker so it's friendly to stooq.pl"""
    return ticker.strip().replace(' ', '.').lower()


@st.cache_data(show_spinner='Getting stock name', max_entries=10)
def get_stock_name(ticker: str) -> str:
    """Gets the name of the stock given by the ticker"""
    try:
        # configures selenium driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'https://stooq.pl/q/?s={ticker}')

        # accepts cookies
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'fc-cta-consent'))
        ).click()

        # waits until the page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'f18'))
        )

        # gets page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # extracts stock name
        ticker_upper = f'({ticker.upper()})'
        result = ''
        for tag in soup.find_all('font', id='f18'):
            if ticker_upper in tag.text:
                result = tag.text.strip()
    finally:
        driver.quit()
    
    if result == '':
        # something went wrong
        raise Exception('Something went wrong')
      
    return result
        

@st.cache_data(show_spinner='Downloading data', max_entries=10)
def get_stock_data(ticker: str) -> pd.DataFrame:
    """Takes a ticker as an argument and returns 
    a DataFrame containing stock data gathered from stooq.pl
    """
    # tries to get data for ticker
    df = pd.read_csv(
        f'https://stooq.pl/q/d/l/?s={ticker}' + '&i=d',
        index_col=0, 
        parse_dates=[0],
    )
    if len(df) == 0:
        raise FileNotFoundError('No data for this ticker')
    
    # if successful fixes naming for the pandas DataFrame
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df.index.name = None

    return df
