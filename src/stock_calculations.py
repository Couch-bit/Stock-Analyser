import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly.subplots import make_subplots


def _preprocess_data(df: pd.DataFrame, filter_string: str) -> pd.DataFrame:
    """Calculates the stochastic oscilator, filters the data,
    adds these columns to the dataframe
    and makes sure all columns are lower case"""

    # define stochastic oscillator
    df = pd.concat(
        [df, df.ta.stoch(high='high', low='low', k=14, d=3)], axis=1
    )
    # define moving average
    df['close_weekly_average'] = df['close'].rolling(5).mean()
    df = df.last(filter_string)
    df.columns = [x.lower() for x in df.columns]
    return df


@st.cache_data(show_spinner=False)
def get_stock_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates both simple and log daily returns"""

    df = df.copy()
    df['daily return'] = df['close'].diff() / df['close'].shift(1)
    df['log daily return'] = np.log(df['daily return'] + 1)

    return df


@st.cache_data(show_spinner=False)
def prepare_data_for_display(df: pd.DataFrame,
                             filter_string: str) -> pd.DataFrame:
    """Parses datetime as data and filters data for display"""

    df = df.copy()
    df = df.last(filter_string)
    df.index = df.index.date

    return df


@st.cache_data(show_spinner=False)
def visualize_stock_prices(df: pd.DataFrame, filter_string: str) -> go.Figure:
    """Creates a plot stock price history and an oscillator plot from
    a given pandas dataframe for the previous months"""

    df = _preprocess_data(df, filter_string)
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Prices', 'Oscillator'))

    # create candlestick plot
    fig.append_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            showlegend=False
        ), row=1, col=1
    )
    # add lineplot of daily prices
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['close_weekly_average'],
            line=dict(color='orange', width=1),
            name='close 5D moving average',
        ), row=1, col=1
    )

    # add fast stochastic oscillator
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['stochk_14_3_3'],
            line=dict(color='lightblue', width=2),
            name='fast',
        ), row=2, col=1
    )
    # add slow stochastic oscillator
    fig.append_trace(
        go.Scatter(
            x=df.index,
            y=df['stochd_14_3_3'],
            line=dict(color='orange', width=2),
            name='slow'
        ), row=2, col=1
    )

    fig.update_yaxes(range=[-10, 110], row=2, col=1)
    fig.add_hline(y=0, col=1, row=2, line_color="white", line_width=2)
    fig.add_hline(y=100, col=1, row=2, line_color="white", line_width=2)
    fig.add_hline(y=20, col=1, row=2, line_color="red", line_width=1)
    fig.add_hline(y=80, col=1, row=2, line_color="green", line_width=1)
    fig.add_hrect(y0=0, y1=20, col=1, row=2, line_width=0,
                  fillcolor="red", opacity=0.2)
    fig.add_hrect(y0=80, y1=100, col=1, row=2, line_width=0,
                  fillcolor="green", opacity=0.2)

    layout = go.Layout(
        plot_bgcolor='#111111',
        # Font Families
        font_family='Times New Roman',
        font_color='white',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    fig.update_layout(layout)

    return fig
