import os
import matplotlib.pyplot as plt
from matplotlib import cycler

def save_plot(name, symbol, output_dir):
    """Saves the plot to the specified directory."""
    output_path = os.path.join(output_dir, f'{name}_{symbol}.png')
    plt.savefig(output_path)
    print(f'Generated sma chart for {symbol} in path: "{output_path}"')
    plt.close()

def setup_plot_styling():
    """Sets up the styling for the plots."""
    colors = cycler('color', ['#669FEE', '#66EE91', '#9988DD', '#EECC55', '#88BB44', '#FFBBBB'])
    plt.rc('figure', facecolor='#313233')
    plt.rc('axes', facecolor="#313233", edgecolor='none',
           axisbelow=True, grid=True, prop_cycle=colors,
           labelcolor='gray')
    plt.rc('grid', color='474A4A', linestyle='solid')
    plt.rc('xtick', color='gray')
    plt.rc('ytick', direction='out', color='gray')
    plt.rc('legend', facecolor="#313233", edgecolor="#313233")
    plt.rc("text", color="#C9C9C9")

def view_plot_sma(sma):
    """Plot view SMA"""
    sma[["close", "sma_fast", "sma_slow"]].plot(figsize=(15,8))

def verify_plot_signals_sma(sma, year):
    """Plots the buy and sell signals on the stock data."""
    idx_open = sma.loc[sma["position"] == 1].loc[year].index
    idx_close = sma.loc[sma["position"] == -1].loc[year].index

    plt.figure(figsize=(15, 6))
    plt.scatter(idx_open, sma.loc[idx_open]["close"].loc[year], color="#57CE95", marker="^")
    plt.scatter(idx_close, sma.loc[idx_close]["close"].loc[year], color="red", marker="v")
    plt.plot(sma["close"].loc[year].index, sma["close"].loc[year], alpha=0.35)
    plt.plot(sma["close"].loc[year].index, sma["sma_fast"].loc[year], alpha=0.35)
    plt.plot(sma["close"].loc[year].index, sma["sma_slow"].loc[year], alpha=0.35)

def plot_profits_sma(sma):
    """Plot view profits"""
    sma["return"].plot(figsize=(15,8))    