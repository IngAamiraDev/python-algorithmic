import matplotlib.pyplot as plt
import yfinance as yf
import warnings
import ta  # Ensure ta is installed for technical analysis

# Setup
plt.style.use('ggplot')
warnings.filterwarnings("ignore")

# Utility Functions
def download_data(symbol):
    """Download and prepare stock data."""
    df = yf.download(symbol)
    df = df[["Adj Close"]]
    df.columns = ["close"]
    return df

def calculate_returns(df):
    """Calculate daily returns."""
    df["returns"] = df["close"].pct_change(1)
    return df

def calculate_sma(df, windows):
    """Calculate Simple Moving Averages (SMA)."""
    for window in windows:
        df[f"SMA {window}"] = df["close"].rolling(window).mean().shift(1)
    return df

def calculate_volatility(df, windows):
    """Calculate rolling standard deviations (volatility)."""
    for window in windows:
        df[f"MSD {window}"] = df["returns"].rolling(window).std().shift(1)
    return df

def calculate_rsi(df, window=14):
    """Calculate the Relative Strength Index (RSI)."""
    RSI = ta.momentum.RSIIndicator(df["close"], window=window, fillna=False)
    df["rsi"] = RSI.rsi()
    return df

def feature_engineering(symbol):
    """Apply feature engineering to the stock data."""
    df = download_data(symbol)
    df = calculate_returns(df)
    df = calculate_sma(df, windows=[15, 60])
    df = calculate_volatility(df, windows=[10, 30])
    df = calculate_rsi(df)
    return df

def main():
    """Main function to run the feature engineering process."""
    symbol = "GOOG"
    df_features = feature_engineering(symbol)
    print(df_features)

if __name__ == "__main__":
    main()