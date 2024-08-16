import os
import glob
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import cycler
from datetime import datetime, timedelta


# Utility Functions
def clear_directory(path):
    """Clear all contents of the output directory."""
    files = glob.glob(os.path.join(path, '*'))
    for f in files:
        try:
            os.remove(f)
            print(f"Deleted: {f}")
        except Exception as e:
            print(f"Error deleting file {f}: {e}")


def create_directory(output_dir):
    """Create the output directory if it does not exist."""
    os.makedirs(output_dir, exist_ok=True)


def import_data_yf(symbol, start_date, end_date):
    """Download historical data using yfinance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        df.columns = ["open", "high", "low", "close", "adj close", "volume"]
        df.index.name = "time"
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return df


# Plot Styling
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


# Financial Calculations
def drawdown_function(serie):
    """Calculate the drawdown of a time series."""
    cum = serie.dropna().cumsum() + 1
    running_max = np.maximum.accumulate(cum)
    drawdown = cum / running_max - 1
    return drawdown


def BackTest(serie, annualized_scalar, output_dir):
    """Backtest the portfolio and benchmark against the S&P 500."""
    # Import the benchmark (S&P 500)
    sp500 = yf.download("^GSPC")["Adj Close"].pct_change(1)
    sp500.name = "SP500"

    # Ensure the serie has a name for reference
    serie.name = "Portfolio"

    # Concatenate the portfolio returns and the S&P 500 returns
    val = pd.concat((serie, sp500), axis=1).dropna()

    # Calculate the drawdown
    drawdown = drawdown_function(serie) * 100

    # Calculate the max drawdown
    max_drawdown = -np.min(drawdown)

    # Create subplots
    fig, (cum, dra) = plt.subplots(1, 2, figsize=(20, 6))
    fig.suptitle("Backtesting", size=20)

    # Cumulative returns chart for portfolio and S&P 500
    cum.plot(val["Portfolio"].cumsum() * 100, color="#39B3C7")
    cum.plot(val["SP500"].cumsum() * 100, color="#B85A0F")
    cum.legend(["Portfolio", "SP500"])
    cum.set_title("Cumulative Return", size=13)
    cum.set_ylabel("Cumulative Return %", size=11)

    # Drawdown chart
    dra.fill_between(drawdown.index, 0, drawdown, color="#C73954", alpha=0.65)
    dra.set_title("Drawdown", size=13)
    dra.set_ylabel("Drawdown %", size=11)

    # Save the plot
    plt.savefig(os.path.join(output_dir, 'backtesting_plot.png'))
    plt.close()

    # Calculate the Sortino ratio
    sortino = np.sqrt(annualized_scalar) * serie.mean() / serie[serie < 0].std()

    # Calculate beta
    beta = np.cov(val["Portfolio"], val["SP500"], rowvar=False)[0][1] / np.var(val["SP500"])

    # Calculate alpha
    alpha = annualized_scalar * (serie.mean() - beta * sp500.mean())

    # Print statistics
    print(f"Sortino: {np.round(sortino, 3)}")
    print(f"Beta: {np.round(beta, 3)}")
    print(f"Alpha: {np.round(alpha * 100, 3)} %")
    print(f"MaxDrawdown: {np.round(max_drawdown, 3)} %")


def SMA_strategy(input_data, mt5=False, yf=False):
    """Apply a Simple Moving Average (SMA) strategy on the data."""
    if mt5:
        df = preprocessing(input_data)
    elif yf:
        df = preprocessing_yf(input_data)
    else:
        return None

    # Calculate SMAs
    df["SMA fast"] = df["close"].rolling(30).mean()
    df["SMA slow"] = df["close"].rolling(60).mean()

    # Initialize position column
    df["position"] = np.nan

    # Define positions based on SMA crossovers
    df.loc[(df["SMA fast"] > df["SMA slow"]), "position"] = 1
    df.loc[(df["SMA fast"] < df["SMA slow"]), "position"] = -1

    # Calculate daily returns
    df["pct"] = df["close"].pct_change(1)

    # Calculate strategy returns
    df["return"] = df["pct"] * df["position"].shift(1)

    return df["return"]


def preprocessing_yf(symbol):
    """Preprocess data from yfinance for SMA strategy."""
    df = yf.download(symbol).dropna()

    # Rename columns
    df.columns = ["open", "high", "low", "close", "adj close", "volume"]
    df.index.name = "time"

    # Remove adjusted close
    df.drop(columns=["adj close"], inplace=True)

    return df


def preprocessing(file_name):
    """Preprocess data from a file for SMA strategy."""
    df = pd.read_csv(file_name, delimiter="\t", index_col=0, parse_dates=True)

    # Remove unnecessary columns
    df = df.iloc[:, :-2]

    # Rename columns
    df.columns = ["open", "high", "low", "close", "volume"]
    df.index.name = "time"

    return df


# Main Execution
def main():
    # Parameters
    symbol = "AAPL"
    output_dir = './img/'
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    annualized_scalar = 252

    # Setup
    setup_plot_styling()
    clear_directory(output_dir)
    create_directory(output_dir)

    # Download and process data
    df = import_data_yf(symbol, start_date, end_date)
    dfc = df["close"].pct_change(1).dropna()

    # Apply SMA strategy    
    dfc = SMA_strategy(symbol, yf=True).loc["2024":] - 0.00001

    # Run backtest
    BackTest(dfc, annualized_scalar, output_dir)


if __name__ == '__main__':
    main()