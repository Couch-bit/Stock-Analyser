import stock_calculations
import stock_scraping
import streamlit as st

st.set_page_config(layout='wide')
st.title('_:blue[Stock] Dashboard_')

settings, result= st.columns([0.2, 0.8])
if 'data_ready' not in st.session_state:
    st.session_state['data_ready'] = False
with settings:
    # data is gathered from stooq.pl
    ticker_str = (
        st.text_input('Enter your ticker:')
    )
    # number of months must be a positive integer
    months_str = (
        st.text_input('Enter how many months of history you want to display:')
    )
    if st.button('Run Analysis'):
        # don't show anything if last data load failed
        st.session_state['data_ready'] = False
        try:
            months = int(months_str)
            if months > 0:
                # don't try webscraping if provided 
                # number of months is correct
                st.session_state['name'] = (
                    stock_scraping.get_stock_name(ticker_str)
                )
                # try to get data, if successful update session state
                st.session_state['df'] = stock_calculations.get_stock_returns(
                    stock_scraping.get_stock_data(ticker_str)
                )
                st.session_state['months_filter'] = f'{months_str}M'
                st.session_state['data_ready'] = True
            else:
                st.write('The number of months must be positive')
        except ValueError:
            st.write('Number of months must be an integer')
        except FileNotFoundError as e:
            st.write(str(e))
        except Exception:
            st.write('Unexpected Error occurred')
    
    if st.session_state['data_ready']:
        # allows for control of data shown in preview
        hslide = st.slider('Number of rows', min_value=5, max_value=20)

with result:
    if st.session_state['data_ready']:
        # get dataframe to be displayed
        df_display = stock_calculations.prepare_data_for_display(
            st.session_state['df'],
            st.session_state['months_filter'] ,
        )
 
        # set header as the name of the stock
        st.header(st.session_state['name'])

        # display a preview of the data
        st.subheader('Raw Data')
        st.write(df_display.tail(hslide))
        st.subheader('Plots')

        # display a candlestick plot along with an oscillator plot
        fig = stock_calculations.visualize_stock_prices(
            st.session_state['df'],
            st.session_state['months_filter'],
        )
        st.plotly_chart(fig)
