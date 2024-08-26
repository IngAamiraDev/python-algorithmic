import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import ta
import warnings
from cycler import cycler
warnings.filterwarnings("ignore")

# Constants
DURATION = 5
SPREAD = 0.01
SYMBOL = "AAPL"  # Update this symbol as needed
OUTPUT_DIR = './img/'

# Utility Functions
def create_directory(output_dir):
    """Create the output directory if it does not exist."""
    import os
    os.makedirs(output_dir, exist_ok=True)

def save_plot(name: str, symbol: str, output_dir: str) -> None:
    """Save the plot to the specified directory."""
    try:
        plt.savefig(f'{output_dir}/{name}_{symbol}.png')
        plt.close()
    except Exception as e:
        print(f"An error occurred while saving the plot: {e}")

def import_data_yf(symbol):
    """Download data from Yahoo Finance using yfinance."""
    df = yf.download(symbol, interval="1d").dropna()

    # Rename columns
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df.index.name = "time"
    return df

def support_resistance(df, duration=DURATION, spread=SPREAD):
    """Calculate support and resistance levels and generate trading signals."""
    
    # Support and resistance building
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

    # Create Simple moving average 30 days
    df["SMA fast"] = df["close"].rolling(30).mean()

    # Create Simple moving average 60 days
    df["SMA slow"] = df["close"].rolling(60).mean()

    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=10).rsi()

    # RSI yesterday
    df["rsi yesterday"] = df["rsi"].shift(1)

    # Create the signal
    df["signal"] = 0

    df["smooth resistance"] = df["resistance"].fillna(method="ffill")
    df["smooth support"] = df["support"].fillna(method="ffill")

    condition_1_buy = (df["close"].shift(1) < df["smooth resistance"].shift(1)) & \
                      (df["smooth resistance"]*(1+0.5/100) < df["close"])
    condition_2_buy = df["SMA fast"] > df["SMA slow"]
    condition_3_buy = df["rsi"] < df["rsi yesterday"]

    condition_1_sell = (df["close"].shift(1) > df["smooth support"].shift(1)) & \
                       (df["smooth support"]*(1+0.5/100) > df["close"])
    condition_2_sell = df["SMA fast"] < df["SMA slow"]
    condition_3_sell = df["rsi"] > df["rsi yesterday"]

    df.loc[condition_1_buy & condition_2_buy & condition_3_buy, "signal"] = 1
    df.loc[condition_1_sell & condition_2_sell & condition_3_sell, "signal"] = -1

    # Calculate returns
    df["pct"] = df["close"].pct_change(1)
    df["return"] = np.array([df["pct"].shift(i) for i in range(duration)]).sum(axis=0) * (df["signal"].shift(duration))
    df.loc[df["return"] == -1, "return"] = df["return"] - spread
    df.loc[df["return"] == 1, "return"] = df["return"] - spread

    return df["return"]

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

def plot_returns(returns, symbol):
    """Plot cumulative returns and save the plot."""
    plt.figure(figsize=(15, 8))
    plt.plot(returns.cumsum(), label='Cumulative Returns', color='blue')
    plt.title(f'Cumulative Returns for {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)

    # Save plot
    save_plot('cumulative_returns', symbol, OUTPUT_DIR)

def main():
    # Setup
    setup_plot_styling()
    create_directory(OUTPUT_DIR)
    
    # Download data
    df = import_data_yf(SYMBOL)

    # Apply support and resistance analysis
    returns = support_resistance(df)

    # Plot and save results
    plot_returns(returns, SYMBOL)

if __name__ == '__main__':
    main()