import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import ta
from datetime import datetime, timedelta
from matplotlib import cycler

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

def import_data_yf(symbol, start_date, end_date):
    """Download financial data using yfinance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        df.columns = ["open", "high", "low", "close", "adj close", "volume"]
        df.index.name = "time"  
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    return df

def support_resistance(df, duration=5, spread=0):
    """Calculate support and resistance levels and generate trading signals."""
    df["support"] = np.nan
    df["resistance"] = np.nan

    df.loc[
        (df["low"].shift(5) > df["low"].shift(4)) &
        (df["low"].shift(4) > df["low"].shift(3)) &
        (df["low"].shift(3) > df["low"].shift(2)) &
        (df["low"].shift(2) > df["low"].shift(1)) &
        (df["low"].shift(1) > df["low"].shift(0)),
        "support"
    ] = df["low"]

    df.loc[
        (df["high"].shift(5) < df["high"].shift(4)) &
        (df["high"].shift(4) < df["high"].shift(3)) &
        (df["high"].shift(3) < df["high"].shift(2)) &
        (df["high"].shift(2) < df["high"].shift(1)) &
        (df["high"].shift(1) < df["high"].shift(0)),
        "resistance"
    ] = df["high"]

    df["SMA fast"] = df["close"].rolling(30).mean()
    df["SMA slow"] = df["close"].rolling(60).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=10).rsi()
    df["rsi yersteday"] = df["rsi"].shift(1)

    df["signal"] = 0
    df["smooth resistance"] = df["resistance"].ffill()
    df["smooth support"] = df["support"].ffill()

    condition_1_buy = (
        (df["close"].shift(1) < df["smooth resistance"].shift(1)) &
        (df["smooth resistance"] * (1 + 0.5 / 100) < df["close"])
    )
    condition_2_buy = df["SMA fast"] > df["SMA slow"]
    condition_3_buy = df["rsi"] < df["rsi yersteday"]

    condition_1_sell = (
        (df["close"].shift(1) > df["smooth support"].shift(1)) &
        (df["smooth support"] * (1 + 0.5 / 100) > df["close"])
    )
    condition_2_sell = df["SMA fast"] < df["SMA slow"]
    condition_3_sell = df["rsi"] > df["rsi yersteday"]

    df.loc[condition_1_buy & condition_2_buy & condition_3_buy, "signal"] = 1
    df.loc[condition_1_sell & condition_2_sell & condition_3_sell, "signal"] = -1

    df["pct"] = df["close"].pct_change(1)
    df["return"] = np.array([df["pct"].shift(i) for i in range(duration)]).sum(axis=0) * df["signal"].shift(duration)
    df.loc[df["return"] == -1, "return"] -= spread
    df.loc[df["return"] == 1, "return"] -= spread

    return df["return"]

def plot_support_resistance(df, symbol, output_dir):
    """Plot and save support and resistance levels."""
    setup_plot_styling()
    plt.figure(figsize=(15, 8))
    plt.plot(df.index, df['support'], label='Support', color='green')
    plt.plot(df.index, df['resistance'], label='Resistance', color='red')
    plt.plot(df.index, df['close'], label='Close Price', color='blue')
    plt.title('Support and Resistance Levels')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    save_plot('support_resistance', symbol, output_dir)

def main():
    symbol = "NCL"
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    output_dir = './img/'

    df = import_data_yf(symbol, start_date, end_date)
    if df is not None:
        df['return'] = support_resistance(df)
        plot_support_resistance(df, symbol, output_dir)
        print(df.head())

if __name__ == '__main__':
    main()