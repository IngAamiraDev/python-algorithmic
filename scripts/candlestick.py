import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.dates import date2num
import datetime
from datetime import datetime, timedelta

def download_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Download historical data for a given symbol using yfinance.

    :param symbol: Asset symbol (e.g., "NVDA").
    :param start_date: Start date (format 'YYYY-MM-DD').
    :param end_date: End date (format 'YYYY-MM-DD').
    :param interval: Data interval (e.g., '1d' for daily data).
    :return: DataFrame with downloaded data.
    """
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        df.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        df.index.name = "Date"
        return df
    except Exception as e:
        print(f"An error occurred while downloading data: {e}")
        return pd.DataFrame()

def signal_generator(df: pd.DataFrame) -> int:
    """
    Generate buy/sell signals based on a candlestick pattern.

    :param df: DataFrame with data for the last two candles.
    :return: 1 for bearish pattern, 2 for bullish pattern, 0 for no clear pattern.
    """
    open_current = df.Open.iloc[-1]
    close_current = df.Close.iloc[-1]
    open_previous = df.Open.iloc[-2]
    close_previous = df.Close.iloc[-2]
    
    if (open_current > close_current and 
        open_previous < close_previous and 
        close_current < open_previous and
        open_current >= close_previous):
        return 1  # Bearish pattern

    elif (open_current < close_current and 
          open_previous > close_previous and 
          close_current > open_previous and
          open_current <= close_previous):
        return 2  # Bullish pattern
    
    return 0  # No clear pattern

def add_signals_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add buy/sell signals to the DataFrame.

    :param df: DataFrame with historical data.
    :return: DataFrame with an additional signal column.
    """
    signals = [0]  # Initialize the signals list with a default value
    for i in range(1, len(df)):
        temp_df = df.iloc[i-1:i+1]
        signals.append(signal_generator(temp_df))
    df['signal'] = signals
    return df

def setup_plot_styling():
    """Setup custom plot styling."""
    colors = cycler('color', ['#669FEE', '#66EE91', '#9988DD', '#EECC55', '#88BB44', '#FFBBBB'])
    plt.rc('figure', facecolor='#313233')
    plt.rc('axes', facecolor="#313233", edgecolor='none', axisbelow=True, grid=True, prop_cycle=colors, labelcolor='gray')
    plt.rc('grid', color='#474A4A', linestyle='solid')
    plt.rc('xtick', color='gray')
    plt.rc('ytick', direction='out', color='gray')
    plt.rc('legend', facecolor="#313233", edgecolor="#313233")
    plt.rc("text", color="#C9C9C9")

def save_plot(name: str, symbol: str, output_dir: str) -> None:
    """Save the plot to the specified directory."""
    try:
        plt.savefig(f'{output_dir}/{name}_{symbol}.png')
        plt.close()
    except Exception as e:
        print(f"An error occurred while saving the plot: {e}")

def plot_candlestick_chart(df: pd.DataFrame, symbol: str, output_dir: str) -> None:
    """
    Generate and save a candlestick chart.

    :param df: DataFrame with data to plot.
    :param title: Title of the chart.
    :param output_dir: Directory to save the chart.
    """
    setup_plot_styling()  # Apply custom styling
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot candlesticks
    for i in range(len(df)):
        color = 'green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red'
        ax.plot([df.index[i], df.index[i]], [df['Low'].iloc[i], df['High'].iloc[i]], color=color, lw=1.5)
        ax.add_patch(plt.Rectangle((df.index[i] - pd.Timedelta(hours=12), df['Open'].iloc[i]), width=pd.Timedelta(hours=24), height=df['Close'].iloc[i] - df['Open'].iloc[i], color=color))
    
    ax.set_title(f'Candlestick Chart for {symbol}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.tick_params(axis='x', rotation=45)
    
    # Save the plot with a dynamic filename
    save_plot('candlestick_chart', symbol, output_dir)


def main():
    # Input parameters
    symbol = "AAPL"
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    output_dir = './img/'  # Output directory for the charts
    
    # Download data
    dataF = download_data(symbol, start_date, end_date)
    
    if not dataF.empty:
        # Add signals to the DataFrame
        dataF_with_signals = add_signals_to_dataframe(dataF)
        
        # Display signal counts
        print(dataF_with_signals.signal.value_counts())
        
        # Plot and save
        plot_candlestick_chart(dataF_with_signals, symbol, output_dir)
    else:
        print("Failed to retrieve data or data is empty.")

if __name__ == "__main__":
    main()