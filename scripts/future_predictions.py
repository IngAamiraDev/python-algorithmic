import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import ta
import warnings
from cycler import cycler
import os

warnings.filterwarnings("ignore")

# Constants
DURATION = 5
SPREAD = 0.01
SYMBOL = "O"
OUTPUT_DIR = './img/'

# Utility Functions
def create_directory(output_dir):
    """Create the output directory if it does not exist."""
    os.makedirs(output_dir, exist_ok=True)

def save_plot(name: str, symbol: str, output_dir: str) -> None:
    """Save the plot to the specified directory."""
    try:
        plt.savefig(os.path.join(output_dir, f'{name}_{symbol}.png'))
        plt.close()
    except Exception as e:
        print(f"An error occurred while saving the plot: {e}")

def import_data_yf(symbol):
    """Download data from Yahoo Finance using yfinance."""
    df = yf.download(symbol, interval="1d").dropna()
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df.index.name = "time"
    return df

def support_resistance(df, duration=DURATION, spread=SPREAD):
    """Calculate support and resistance levels and generate trading signals."""
    df["support"] = np.nan
    df["resistance"] = np.nan

    df.loc[(df["low"].shift(5) > df["low"].shift(4)) & 
           (df["low"].shift(4) > df["low"].shift(3)) & 
           (df["low"].shift(3) > df["low"].shift(2)) & 
           (df["low"].shift(2) > df["low"].shift(1)) & 
           (df["low"].shift(1) > df["low"].shift(0)), "support"] = df["low"]

    df.loc[(df["high"].shift(5) < df["high"].shift(4)) & 
           (df["high"].shift(4) < df["high"].shift(3)) & 
           (df["high"].shift(3) < df["high"].shift(2)) & 
           (df["high"].shift(2) < df["high"].shift(1)) & 
           (df["high"].shift(1) < df["high"].shift(0)), "resistance"] = df["high"]

    df["SMA fast"] = df["close"].rolling(30).mean()
    df["SMA slow"] = df["close"].rolling(60).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=10).rsi()
    df["rsi yesterday"] = df["rsi"].shift(1)

    df["signal"] = 0
    df["smooth resistance"] = df["resistance"].ffill()
    df["smooth support"] = df["support"].ffill()

    condition_1_buy = (df["close"].shift(1) < df["smooth resistance"].shift(1)) & \
                      (df["smooth resistance"] * (1 + 0.5 / 100) < df["close"])
    condition_2_buy = df["SMA fast"] > df["SMA slow"]
    condition_3_buy = df["rsi"] < df["rsi yesterday"]

    condition_1_sell = (df["close"].shift(1) > df["smooth support"].shift(1)) & \
                       (df["smooth support"] * (1 + 0.5 / 100) > df["close"])
    condition_2_sell = df["SMA fast"] < df["SMA slow"]
    condition_3_sell = df["rsi"] > df["rsi yesterday"]

    df.loc[condition_1_buy & condition_2_buy & condition_3_buy, "signal"] = 1
    df.loc[condition_1_sell & condition_2_sell & condition_3_sell, "signal"] = -1

    df["pct"] = df["close"].pct_change(1)
    df["return"] = np.array([df["pct"].shift(i) for i in range(duration)]).sum(axis=0) * df["signal"].shift(duration)
    df["return"] -= df["signal"].shift(duration) * spread

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

def verify_plot_signals_sma(sma, year):
    """Plot buy/sell signals on the SMA chart."""
    plt.figure(figsize=(15, 6))
    
    try:
        year_data = sma.loc[year]
        idx_open = year_data[year_data["signal"] == 1].index
        idx_close = year_data[year_data["signal"] == -1].index
        plt.scatter(idx_open, year_data.loc[idx_open]["close"], color="#57CE95", marker="^", label='Buy Signal')
        plt.scatter(idx_close, year_data.loc[idx_close]["close"], color="red", marker="v", label='Sell Signal')
        plt.plot(year_data["close"], alpha=0.35, label='Close Price')
        plt.plot(year_data["SMA fast"], alpha=0.35, label='SMA Fast')
        plt.plot(year_data["SMA slow"], alpha=0.35, label='SMA Slow')
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("SMA Signals Verification")
        plt.legend()
        plt.grid(True)
    except KeyError:
        print(f"No data available for the year {year}")

def create_weekly_df(df):
    """Create a DataFrame for the last week of trading days, including future dates if present."""
    # Ensure index is a datetime object for proper date manipulation
    df.index = pd.to_datetime(df.index)
    
    # Get the latest available date in the DataFrame
    end_date = df.index.max()
    
    # Calculate the start date for the week
    start_date = end_date - pd.DateOffset(weeks=1)
    
    # Filter for trading days only, considering future dates
    df_weekly = df.loc[start_date:end_date].copy()
    df_weekly = df_weekly[df_weekly.index.dayofweek < 5]  # Exclude weekends (Saturday=5, Sunday=6)
    
    return df_weekly[['close']]


def plot_weekly_prediction(df_weekly, symbol):
    """Plot the prediction of the price for the last week."""
    plt.figure(figsize=(10, 6))
    plt.plot(df_weekly.index, df_weekly['close'], label='Close Price', marker='o')
    plt.title(f'{symbol} - Price Prediction for Last Week')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid(True)
    save_plot('weekly_price_prediction', symbol, OUTPUT_DIR)

def main():
    # Setup
    setup_plot_styling()
    create_directory(OUTPUT_DIR)
    
    # Download data
    df = import_data_yf(SYMBOL)

    # Apply support and resistance analysis
    sma = support_resistance(df)

    # Verify and plot signals for a specific year
    verify_plot_signals_sma(sma, '2024')

    # Create a weekly DataFrame and plot the price prediction
    df_weekly = create_weekly_df(df)
    plot_weekly_prediction(df_weekly, SYMBOL)

if __name__ == '__main__':
    main()