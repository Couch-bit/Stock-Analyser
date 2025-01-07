import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

from global_settings import (
    TRADE_DAYS_IN_YEAR,
    TRADE_DAYS_IN_MONTH,
    TRADE_DAYS_IN_WEEK,
    OSCILLATOR_LONG,
    OSCILLATOR_SHORT,
    OSCILLATOR_SMOOTH,
)
from plotly.subplots import make_subplots


def _preprocess_data(df: pd.DataFrame, filter_string: str) -> pd.DataFrame:
    """Calculates the stochastic oscilator, filters the data,
    adds these columns to the DataFrame
    and makes sure all columns are lower case
    """
    # defines stochastic oscillator
    df = pd.concat(
        [
            df, 
            df.ta.stoch(
                high='high',
                low='low',
                close='close',
                k=OSCILLATOR_LONG,
                d=OSCILLATOR_SHORT,
                smooth_k=OSCILLATOR_SMOOTH,
            )
        ], axis=1
    )

    # defines moving average
    df['close_weekly_average'] = (
        df['close'].rolling(TRADE_DAYS_IN_WEEK).mean()
    )
    df['close_monthly_average'] = (
        df['close'].rolling(TRADE_DAYS_IN_MONTH).mean()
    )

    # filters DataFrame
    df = df.last(filter_string)

    # fixes column naming (stoch method creates weird names)
    df.columns = [col.lower() for col in df.columns]

    return df


def get_stock_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates both simple and log daily returns"""
    df = df.copy()
    df['daily return'] = df['close'].diff() / df['close'].shift(1)
    df['log daily return'] = np.log(df['daily return'] + 1)

    return df


def summarise_stock(
    df: pd.DataFrame,
    var_function: 'function',
    es_function: 'function',
) -> pd.DataFrame:
    """Given display ready DataFrame summarises it.
    VaR and ES are calculated on daily returns using provided functions
    """
    # calculates summary metrics
    return_over_time = (
        (np.prod(df['daily return'] + 1)**(TRADE_DAYS_IN_YEAR / len(df))) - 1
    )
    annualized_volatility = (
        np.std(df['log daily return'], ddof=1) * np.sqrt(TRADE_DAYS_IN_YEAR)
    )
    value_at_risk = var_function(df['daily return'])
    expected_shortfall = es_function(df['daily return'])

    # creates DataFrame from metrics
    result_df = pd.DataFrame(
        data={'': [
            return_over_time,
            annualized_volatility, 
            value_at_risk, 
            expected_shortfall,
        ]},
        index = ['Return', 'Volatility', 'VaR', 'ES']
    )

    return result_df


def prepare_data_for_display(
    df: pd.DataFrame,
    filter_string: str,
) -> pd.DataFrame:
    """Parses datetime as date and filters data for display"""
    df = df.copy()
    df = df.last(filter_string)
    # the index should be date not datetime
    # this is more readable
    df.index = df.index.date

    return df


def visualize_stock_prices(df: pd.DataFrame, filter_string: str) -> go.Figure:
    """Creates a plot of stock price history with volume
    and an oscillator plot from a given pandas DataFrame
    for the previous months based on filter_string
    """
    df = _preprocess_data(df, filter_string)
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=('Price History', 'Oscillator'),
        specs=[[{'secondary_y': True}], [{}]],
    )

    # creates candlestick plot
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # adds lineplot of weekly price average
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['close_weekly_average'],
            line=dict(color='lightblue', width=1),
            name=f'close {TRADE_DAYS_IN_WEEK}D moving average',
        ),
        row=1, 
        col=1,
    )

    # adds lineplot of monthly price average
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['close_monthly_average'],
            line=dict(color='orange', width=1),
            name=f'close {TRADE_DAYS_IN_MONTH}D moving average',
        ), 
        row=1, 
        col=1,
    )

    # adds barplot of volume
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['volume'],
            marker=dict(color='grey'),
            name=f'Volume',
            opacity=0.5,
            showlegend=False,
        ),
        secondary_y=True,
        row=1, 
        col=1,
    )

    # adds fast stochastic oscillator
    oscillator_col_fast = (
        f'stochk_{OSCILLATOR_LONG}_{OSCILLATOR_SHORT}_{OSCILLATOR_SMOOTH}'
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[oscillator_col_fast],
            line=dict(color='lightblue', width=2),
            name='fast',
        ),
        row=2, 
        col=1,
    )

    # adds slow stochastic oscillator
    oscillator_col_slow = (
        f'stochd_{OSCILLATOR_LONG}_{OSCILLATOR_SHORT}_{OSCILLATOR_SMOOTH}'
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[oscillator_col_slow],
            line=dict(color='orange', width=2),
            name='slow',
        ),
        row=2, 
        col=1,
    )

    # updates y-axis fot oscillator plot
    fig.update_yaxes(range=[-10, 110], row=2, col=1)

    # adds helper lines for oscillator plot
    fig.add_hline(y=0, col=1, row=2, line_color='white', line_width=2)
    fig.add_hline(y=100, col=1, row=2, line_color='white', line_width=2)
    fig.add_hline(y=20, col=1, row=2, line_color='red', line_width=1)
    fig.add_hline(y=80, col=1, row=2, line_color='green', line_width=1)

    # adds colored rectangles for critical areas
    fig.add_hrect(y0=0, y1=20, col=1, row=2, line_width=0,
                  fillcolor='red', opacity=0.2)
    fig.add_hrect(y0=80, y1=100, col=1, row=2, line_width=0,
                  fillcolor='green', opacity=0.2)

    # configures layout
    layout = go.Layout(
        plot_bgcolor='#111111',
        font_family='Times New Roman',
        font_color='white',
        font_size=20,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        ),
        yaxis=dict(title='Price'),
        yaxis2=dict(title='Volume'),
    )
    fig.update_layout(layout)

    return fig
