import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import warnings
import datetime

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

def import_data_yf(symbol, start_date, end_date, interval='5m'):
    """
    Import financial data from Yahoo Finance.
    
    Parameters:
    - symbol: The stock symbol to download.
    - start_date: Start date for the data.
    - end_date: End date for the data.
    - interval: Data interval (e.g., '5m' for 5 minutes).
    
    Returns:
    - DataFrame with the financial data.
    """
    df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    df.index.name = 'time'
    df.rename(columns={'Adj Close': 'close'}, inplace=True)
    return df

def calculate_indicators(df):
    """
    Calculate technical indicators for trading signals.
    
    Parameters:
    - df: DataFrame with financial data.
    
    Returns:
    - DataFrame with calculated indicators.
    """
    df['SMA fast'] = df['close'].rolling(window=5).mean()
    df['SMA slow'] = df['close'].rolling(window=15).mean()
    df['rsi'] = df['close'].diff().apply(lambda x: x if x > 0 else 0).rolling(window=5).mean() / df['close'].diff().apply(lambda x: abs(x)).rolling(window=5).mean() * 100
    df['rsi yesterday'] = df['rsi'].shift(1)
    df.dropna(inplace=True)
    return df

def prepare_data(df):
    """
    Prepare data for machine learning model.
    
    Parameters:
    - df: DataFrame with financial data and indicators.
    
    Returns:
    - Tuple of features and labels arrays.
    """
    if df.empty:
        print("DataFrame is empty after calculations")
        return None, None

    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    features = df[['SMA fast', 'SMA slow', 'rsi']].values
    labels = df['target'].values

    if len(features) == 0 or len(labels) == 0:
        print("Features or labels are empty")
    
    return features, labels

def train_model(features, labels):
    """
    Train a RandomForestClassifier model.
    
    Parameters:
    - features: Features for training.
    - labels: Labels for training.
    
    Returns:
    - Trained model.
    """
    if features is None or labels is None:
        print("No data to train the model")
        return None

    if len(features) == 0 or len(labels) == 0:
        print("No data to train the model")
        return None

    try:
        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=0)
        model = RandomForestClassifier(n_estimators=100, random_state=0)
        model.fit(X_train, y_train)
        return model
    except ValueError as e:
        print(f"Error in training model: {e}")
        return None

def make_predictions(df, model):
    """
    Make predictions using the trained model.
    
    Parameters:
    - df: DataFrame with features for prediction.
    - model: Trained model.
    
    Returns:
    - DataFrame with predictions.
    """
    if model is None:
        print("No model to make predictions")
        return df

    df['predicted'] = model.predict(df[['SMA fast', 'SMA slow', 'rsi']])
    return df

def generate_signals(df):
    """
    Generate trading signals based on predictions.
    
    Parameters:
    - df: DataFrame with predictions.
    
    Returns:
    - Tuple of buy, sell, and stop-loss signals.
    """
    if df.empty:
        print("DataFrame is empty after predictions")
        return None, None, None

    buy_signal = df[df['predicted'] == 1]['close'].min()
    sell_signal = df[df['predicted'] == 0]['close'].max()
    stop_loss = buy_signal * 0.98 if buy_signal is not None else None  # Example: 2% below buy price
    
    return buy_signal, sell_signal, stop_loss

def print_signals(symbol, buy_signal, sell_signal, stop_loss):
    """
    Print the generated trading signals.
    
    Parameters:
    - symbol: Stock symbol.
    - buy_signal: Buy signal value.
    - sell_signal: Sell signal value.
    - stop_loss: Stop-loss value.
    """
    print(f"Symbol: {symbol}")
    if pd.notna(buy_signal):
        print(f"Buy: {buy_signal:.2f}")
    else:
        print("No Buy Signal")
    if pd.notna(sell_signal):
        print(f"Sell: {sell_signal:.2f}")
    else:
        print("No Sell Signal")
    if pd.notna(stop_loss):
        print(f"Stop: {stop_loss:.2f}")
    else:
        print("No Stop-Loss Trigger")

def main():
    symbol = 'AAPL'
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')    
    start_date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')    
    interval = '5m'
    
    df = import_data_yf(symbol, start_date, end_date, interval)
    df = calculate_indicators(df)
    
    if df.empty:
        print("No data available after importing and calculating indicators")
        return
    
    features, labels = prepare_data(df)
    model = train_model(features, labels)
    df = make_predictions(df, model)
    buy_signal, sell_signal, stop_loss = generate_signals(df)
    print_signals(symbol, buy_signal, sell_signal, stop_loss)

if __name__ == "__main__":
    main()