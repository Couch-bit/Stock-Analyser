import numpy as np
import stock_calculations
import stock_scraping
import streamlit as st


# configures general page layout
st.set_page_config(layout='wide', page_title="Stock Analyser")
st.title('_:blue[Stock] Dashboard_')
settings, result = st.columns([0.2, 0.8])

# makes sure 'data_ready' is defined is session_state
if 'data_ready' not in st.session_state:
    st.session_state['data_ready'] = False

with settings:
    # allows for control of data filtering
    month_num = st.slider(
        'Number of months',
        min_value=1,
        max_value=36,
        value=6
    )
    st.session_state['months_filter'] = f'{month_num}M'

    # allows for control of data shown in preview
    row_num = st.slider(
        'Number of rows',
        min_value=5,
        max_value=20
    )

    # allows for control of significance level
    alpha = st.slider(
        'Significance level',
        min_value=0.01, 
        max_value=0.1,
        step=0.01,
        value=0.05
    )   

    # data is gathered from stooq.pl
    ticker_str = (
        st.text_input('Enter your ticker:')
    )

    if st.button('Run Analysis'):
        # don't show anything if last data load failed
        st.session_state['data_ready'] = False

        # formats sticker according to stooq.pl standards
        formatted_ticker = stock_scraping.format_ticker(ticker_str)
        
        try:
            # tries to get data, if successful updates session state
            st.session_state['df'] = stock_calculations.get_stock_returns(
                stock_scraping.get_stock_data(formatted_ticker)
            )

            # gets the name of the stock, if successful updates session state
            st.session_state['name'] = (
                stock_scraping.get_stock_name(formatted_ticker)
            )

            # data loaded successfully
            st.session_state['data_ready'] = True
        except FileNotFoundError as e:
            st.write(str(e))

            # cleasr caches for the current ticker since an error occurred
            stock_scraping.get_stock_data.clear(formatted_ticker)
            stock_scraping.get_stock_name.clear(formatted_ticker)
        except Exception:
            st.write('Unexpected error occurred')

            # clears caches for the current ticker since an error occurred
            stock_scraping.get_stock_data.clear(formatted_ticker)
            stock_scraping.get_stock_name.clear(formatted_ticker)  

with result:
    if st.session_state['data_ready']:
        # sets header as the name of the stock
        st.header(st.session_state['name'])
        
        data_tab, chart_tab = st.tabs(['🗂️ Data', '📈 Plots'])
        with data_tab:
            # gets DataFrame to be displayed
            df_display = stock_calculations.prepare_data_for_display(
                st.session_state['df'],
                st.session_state['months_filter']
            )

            # displays a preview of the data
            st.subheader('Raw Data')
            st.write(df_display.tail(row_num))

            # displays data summary
            st.subheader('Summary')
            st.write(
                stock_calculations.summarise_stock(
                    df_display,
                    lambda x: -np.quantile(x, alpha),
                    lambda x: -np.mean(x[x <= np.quantile(x, alpha)])
                )
            )

        with chart_tab:
            # displays a candlestick plot along with an oscillator plot
            fig = stock_calculations.visualize_stock_prices(
                st.session_state['df'],
                st.session_state['months_filter']
            )
            st.plotly_chart(fig)
