import stock_calculations
import stock_scraping
import streamlit as st

st.set_page_config(layout='wide')
st.title('_:blue[Stock] Dashboard_')
col1, col2 = st.columns([0.2, 0.8])
months_filter = '6M'
if 'data_ready' not in st.session_state:
    st.session_state['data_ready'] = False
with col1:
    ticker_str = (
        st.text_input('Enter your ticker:')
    )
    months_str = (
        st.text_input('Enter how many months of history you want to display:')
    )
    if st.button('Run Analysis'):
        st.session_state['data_ready'] = False
        try:
            months = int(months_str)
            if months > 0:
                st.session_state['df'] = stock_calculations.get_stock_returns(
                    stock_scraping.get_stock_data(ticker_str)
                )
                months_filter = f'{months_str}M'
                st.session_state['data_ready'] = True
            else:
                st.write('The number of months must be positive')
        except ValueError:
            st.write('Number of months must be an integer')
        except FileNotFoundError as e:
            st.write(str(e))
    
    if st.session_state['data_ready']:
        hslide = st.slider('Number of rows', min_value=5, max_value=20)
with col2:
    if st.session_state['data_ready']:
        df_display = stock_calculations.prepare_data_for_display(
            st.session_state['df'],
            months_filter,
        )
 
        st.subheader('Raw Data')
        st.write(df_display.tail(hslide))
        st.subheader('Plots')
        fig = stock_calculations.visualize_stock_prices(
            st.session_state['df'],
            months_filter,
        )
        st.plotly_chart(fig)

