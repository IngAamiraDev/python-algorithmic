import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cycler import cycler
import yfinance as yf
import ta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
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
        plt.savefig(f'{output_dir}/{name}_{symbol}.png')
        plt.close()
    except Exception as e:
        print(f"An error occurred while saving the plot: {e}")

def download_data(symbol: str) -> pd.DataFrame:
    """Download financial data using yfinance."""
    try:
        df = yf.download(symbol)
        df = df[['Adj Close']]
        df.columns = ['close']
        return df
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame instead of None

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

def evaluate_model(reg: LinearRegression, df: pd.DataFrame, split: int) -> None:
    """Evaluate the regression model and print metrics."""
    X = df[['SMA 15', 'SMA 60', 'MSD 10', 'MSD 30', 'rsi']]
    df["prediction"] = reg.predict(X)
    df["position"] = np.sign(df["prediction"])
    df["strategy"] = df["returns"] * df["position"].shift(1)

    print(f"Test R²: {r2_score(df['returns'].iloc[split:], df['prediction'].iloc[split:])}")
    print(f"Test MSE: {mean_squared_error(df['returns'].iloc[split:], df['prediction'].iloc[split:])}")

def plot_strategy(df: pd.DataFrame, symbol: str, output_dir: str) -> None:
    """Plot the trading strategy performance."""
    plt.figure(figsize=(10, 5))
    plt.plot((df["strategy"].iloc[int(0.80 * len(df)):].cumsum() * 100))
    plt.title(f"Linear Regression Strategy for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns (%)")
    save_plot('lin_reg_strategy', symbol, output_dir)

def lin_reg_trading(symbol: str, output_dir: str) -> None:
    """Main function to perform linear regression trading strategy."""
    setup_plot_styling()

    df = download_data(symbol)
    if df.empty:
        print("No data available for the specified symbol.")
        return

    df = feature_engineering(df)
    reg, split = perform_regression(df)
    evaluate_model(reg, df, split)
    plot_strategy(df, symbol, output_dir)

def main() -> None:
    """Entry point for the script."""
    symbol = "NCL"
    output_dir = './img'
    lin_reg_trading(symbol, output_dir)

if __name__ == '__main__':
    main()