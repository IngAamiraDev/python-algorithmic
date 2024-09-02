import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cycler import cycler
import yfinance as yf
import ta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import glob

sns.set_style('darkgrid')

def setup_plot_styling() -> None:
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(f'{output_dir}/{name}_{symbol}.png')
        plt.close()
    except Exception as e:
        print(f"An error occurred while saving the plot: {e}")

def download_data(symbol: str, start_date: str, end_date: str, interval: str = '1h') -> pd.DataFrame:
    """Download intraday financial data using yfinance."""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        if interval == '1m' and (end_dt - start_dt).days > 60:
            print("1m data is only available for the last 60 days. Adjusting date range.")
            end_dt = datetime.now() - timedelta(days=1)
            start_dt = end_dt - timedelta(days=60)
            interval = '1h'
        elif interval == '1h' and (end_dt - start_dt).days > 730:
            print("1h data is only available for the last 730 days. Adjusting date range.")
            end_dt = datetime.now() - timedelta(days=1)
            start_dt = end_dt - timedelta(days=730)
            interval = '1d'

        start_date = start_dt.strftime('%Y-%m-%d')
        end_date = end_dt.strftime('%Y-%m-%d')

        print(f"Downloading data for {symbol} from {start_date} to {end_date} with interval {interval}.")
        
        df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        if df.empty:
            print(f"No data found for {symbol} with interval {interval} from {start_date} to {end_date}")
        else:
            df = df[['Adj Close', 'Open', 'High', 'Low', 'Volume']]
            df.columns = ['close', 'open', 'high', 'low', 'volume']
        
        return df

    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame()

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Perform feature engineering on the data."""
    df_copy = df.dropna().copy()
    df_copy["returns"] = df_copy["close"].pct_change(1)
    df_copy["SMA 15"] = df_copy["close"].rolling(15).mean().shift(1)
    df_copy["SMA 60"] = df_copy["close"].rolling(60).mean().shift(1)
    df_copy["MSD 10"] = df_copy["returns"].rolling(10).std().shift(1)
    df_copy["MSD 30"] = df_copy["returns"].rolling(30).std().shift(1)
    RSI = ta.momentum.RSIIndicator(df_copy["close"], window=14, fillna=False)
    df_copy["rsi"] = RSI.rsi()
    return df_copy.dropna()

def perform_regression(df: pd.DataFrame) -> tuple[LinearRegression, int]:
    """Train a linear regression model and return it."""
    split = int(0.80 * len(df))
    X_train = df[['SMA 15', 'SMA 60', 'MSD 10', 'MSD 30', 'rsi']].iloc[:split]
    y_train = df["returns"].iloc[:split]

    reg = LinearRegression()
    reg.fit(X_train, y_train)

    return reg, split

def plot_strategy(df: pd.DataFrame, symbol: str, output_dir: str) -> None:
    """Plot the trading strategy performance."""
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["strategy"].cumsum() * 100, label='Strategy Cumulative Returns')
    plt.title(f"Linear Regression Strategy for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns (%)")
    plt.legend()

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gcf().autofmt_xdate()
    save_plot('lin_reg_strategy', symbol, output_dir)

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["returns"] - df["prediction"], label='Residuals')
    plt.title(f"Residuals for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Residuals")
    plt.legend()
    save_plot('residuals', symbol, output_dir)

def evaluate_model(reg: LinearRegression, df: pd.DataFrame, split: int) -> None:
    """Evaluate the regression model and print metrics."""
    X = df[['SMA 15', 'SMA 60', 'MSD 10', 'MSD 30', 'rsi']]
    df["prediction"] = reg.predict(X)
    df["position"] = np.sign(df["prediction"])
    df["strategy"] = df["returns"] * df["position"].shift(1)

    print(f"Test R²: {r2_score(df['returns'].iloc[split:], df['prediction'].iloc[split:])}")
    print(f"Test MSE: {mean_squared_error(df['returns'].iloc[split:], df['prediction'].iloc[split:])}")
    print(f"Mean Absolute Error: {np.mean(np.abs(df['returns'].iloc[split:] - df['prediction'].iloc[split:]))}")
    print(f"Mean Absolute Percentage Error: {np.mean(np.abs((df['returns'].iloc[split:] - df['prediction'].iloc[split:]) / df['returns'].iloc[split:])) * 100:.2f}%")

def drawdown_function(serie: pd.Series) -> pd.Series:
    """Calculate the drawdown of a series."""
    cum = serie.dropna().cumsum() + 1
    running_max = np.maximum.accumulate(cum)
    drawdown = cum / running_max - 1
    return drawdown

def lin_reg_trading(symbol: str, start_date: str, end_date: str, interval: str, output_dir: str) -> pd.Series:
    """Main function to perform linear regression trading strategy."""
    setup_plot_styling()

    df = download_data(symbol, start_date, end_date, interval)
    if df.empty:
        print(f"No data available for {symbol} with interval {interval}.")
        return pd.Series()

    df = feature_engineering(df)
    if df.empty:
        print(f"No features available for {symbol}.")
        return pd.Series()

    try:
        reg, split = perform_regression(df)
    except ValueError as e:
        print(f"Regression error for {symbol}: {e}")
        return pd.Series()

    evaluate_model(reg, df, split)
    plot_strategy(df, symbol, output_dir)
    return df["strategy"][df["strategy"] < 0.50]

def clear_directory(path: str) -> None:
    """Clear all contents of the output directory."""
    if os.path.exists(path):
        files = glob.glob(os.path.join(path, '*'))
        for f in files:
            try:
                os.remove(f)
                print(f"Deleted: {f}")
            except Exception as e:
                print(f"Error deleting file {f}: {e}")
    else:
        print(f"Directory {path} does not exist. No files to delete.")

def create_directory(output_dir: str) -> None:
    """Create the output directory if it does not exist."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory {output_dir} created or already exists.")


def main() -> None:
    """Entry point for the script."""
    symbols = ["AAPL", "^GSPC"]
    output_dir = './img'

    # Ensure the output directory exists and clear old files
    create_directory(output_dir)
    clear_directory(output_dir)

    returns = pd.DataFrame()

    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    for symbol in symbols:
        dfc = lin_reg_trading(symbol, start_date, end_date, '5m', output_dir)
        if dfc.empty:
            dfc = lin_reg_trading(symbol, start_date, end_date, '1h', output_dir)
        if dfc.empty:
            dfc = lin_reg_trading(symbol, start_date, end_date, '1d', output_dir)
        if not dfc.empty:
            returns[symbol] = dfc

    if not returns.empty:
        plt.figure(figsize=(20, 8))
        (returns.dropna().sum(axis=1) / returns.shape[1]).cumsum().plot()
        plt.title(f"Cumulative Returns of All Strategies by {symbols}")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Returns")
        save_plot('cumulative_returns', symbols, output_dir)

    if not returns.empty:
        pf = returns.dropna().sum(axis=1) / returns.shape[1]
        drawdowns = drawdown_function(pf.dropna())
        final_performance = pf.dropna().cumsum().iloc[-1] / -np.min(drawdowns)
        print(f"Final performance: {final_performance}")

if __name__ == '__main__':
    main()