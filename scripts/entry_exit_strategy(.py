import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import ta

# Constants
SYMBOL = "AAPL"  # Example symbol
STOP_LOSS_PERCENT = 0.02  # 2% stop loss
OUTPUT_DIR = './img/'

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

def save_plot(name, symbol, output_dir):
    """Save the plot to the specified directory."""
    plt.savefig(f'{output_dir}/{name}_{symbol}.png')
    plt.close()

def import_data_yf(symbol):
    """Download data from Yahoo Finance using yfinance."""
    df = yf.download(symbol, interval="1d").dropna()
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df.index.name = "time"
    return df

def calculate_indicators(df):
    """Calculate indicators for the strategy."""
    df['sma_fast'] = df['close'].rolling(window=15).mean()
    df['sma_slow'] = df['close'].rolling(window=50).mean()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    return df.dropna()

def entry_exit_strategy(df):
    """Determine entry, exit, and stop-loss points."""
    df['position'] = 0  # Default to no position

    # Entry signal: Buy when the price crosses above the fast SMA
    df.loc[df["close"] > df["sma_fast"], "position"] = 1

    # Exit signal: Sell when the price crosses below the fast SMA
    df.loc[df["close"] < df["sma_fast"], "position"] = -1

    # Stop-loss: Set stop-loss based on the entry price
    df['stop_loss'] = df['close'] * (1 - STOP_LOSS_PERCENT)

    return df

def verify_plot_signals_sma(df, years=2):
    """Plot buy/sell signals and the stop-loss on the SMA chart, showing only the last two years by month."""
    plt.figure(figsize=(15, 6))

    # Filter to show only the last two years of data
    recent_years = df.index.max().year - years
    df_recent = df[df.index.year >= recent_years]

    buy_signals = df_recent[df_recent['position'] == 1]
    sell_signals = df_recent[df_recent['position'] == -1]
    stop_loss_signals = df_recent[df_recent['close'] <= df_recent['stop_loss']]

    plt.plot(df_recent['close'], label='Close Price', alpha=0.5)
    plt.plot(df_recent['sma_fast'], label='SMA Fast', alpha=0.75)
    plt.plot(df_recent['sma_slow'], label='SMA Slow', alpha=0.75)
    
    plt.scatter(buy_signals.index, buy_signals['close'], marker='^', color='g', label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['close'], marker='v', color='r', label='Sell Signal')
    plt.scatter(stop_loss_signals.index, stop_loss_signals['close'], marker='x', color='k', label='Stop Loss Trigger')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Entry, Exit, and Stop-Loss Strategy (Last 2 Years)')
    plt.legend()
    plt.grid(True)

    # Format the x-axis to show months
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.xticks(rotation=45)
    
    # Save plot
    plt.savefig(f'{OUTPUT_DIR}/entry_exit_stop_loss_{SYMBOL}.png')
    plt.close()

def verify_plot_signals_sma_month(df, months):
    """Plot buy/sell signals and the stop-loss on the SMA chart, showing only the specified number of months."""
    plt.figure(figsize=(15, 6))

    # Filter to show only the last `months` of data
    recent_data = df.loc[df.index >= (df.index.max() - pd.DateOffset(months=months))]

    buy_signals = recent_data[recent_data['position'] == 1]
    sell_signals = recent_data[recent_data['position'] == -1]
    stop_loss_signals = recent_data[recent_data['close'] <= recent_data['stop_loss']]

    plt.plot(recent_data['close'], label='Close Price', alpha=0.5)
    plt.plot(recent_data['sma_fast'], label='SMA Fast', alpha=0.75)
    plt.plot(recent_data['sma_slow'], label='SMA Slow', alpha=0.75)
    
    plt.scatter(buy_signals.index, buy_signals['close'], marker='^', color='g', label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['close'], marker='v', color='r', label='Sell Signal')
    plt.scatter(stop_loss_signals.index, stop_loss_signals['close'], marker='x', color='k', label='Stop Loss Trigger')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'Entry, Exit, and Stop-Loss Strategy (Last {months} Months)')
    plt.legend()
    plt.grid(True)

    # Format the x-axis to show months
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.xticks(rotation=45)
    
    # Save plot
    plt.savefig(f'{OUTPUT_DIR}/entry_exit_stop_loss_{SYMBOL}_{months}_months.png')
    plt.close()

def main():
    # Download data
    df = import_data_yf(SYMBOL)
    
    # Calculate indicators
    df = calculate_indicators(df)
    
    # Apply strategy
    df = entry_exit_strategy(df)
    
    # Plot results
    verify_plot_signals_sma(df)

    # Plot for months
    months = 6
    verify_plot_signals_sma_month(df, months)

if __name__ == '__main__':
    main()