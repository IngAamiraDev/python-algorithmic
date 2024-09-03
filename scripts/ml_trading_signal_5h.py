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
    """
    df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    df.index.name = 'time'
    df.rename(columns={'Adj Close': 'close'}, inplace=True)
    return df

def calculate_indicators(df):
    """
    Calculate technical indicators for trading signals.
    """
    df['SMA fast'] = df['close'].rolling(window=5).mean()
    df['SMA slow'] = df['close'].rolling(window=15).mean()
    df['rsi'] = df['close'].diff().apply(lambda x: x if x > 0 else 0).rolling(window=5).mean() / df['close'].diff().apply(lambda x: abs(x)).rolling(window=5).mean() * 100
    df['rsi yesterday'] = df['rsi'].shift(1)
    df.dropna(inplace=True)
    return df

def prepare_data(df, time_limit='5h'):
    """
    Prepare data for machine learning model, ensuring targets are within 5 hours.
    """
    if df.empty:
        print("DataFrame is empty after calculations")
        return None, None

    # Define the time limit for intraday trading (e.g., 5 hours)
    time_limit_td = pd.Timedelta(time_limit)

    # Calculate target based on whether the price reaches a threshold within 5 hours
    df['target'] = 0
    for i in range(len(df)):
        current_time = df.index[i]
        future_time_limit = current_time + time_limit_td

        # Check if within 5 hours, the price exceeds a certain threshold (e.g., 1% gain)
        future_data = df[(df.index > current_time) & (df.index <= future_time_limit)]
        if not future_data.empty:
            if future_data['close'].max() > df['close'].iloc[i] * 1.01:  # Example: 1% gain
                df.at[df.index[i], 'target'] = 1

    features = df[['SMA fast', 'SMA slow', 'rsi']].values
    labels = df['target'].values

    if len(features) == 0 or len(labels) == 0:
        print("Features or labels are empty")
    
    return features, labels

def train_model(features, labels):
    """
    Train a RandomForestClassifier model.
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
    """
    if model is None:
        print("No model to make predictions")
        return df

    df['predicted'] = model.predict(df[['SMA fast', 'SMA slow', 'rsi']])
    return df

def generate_signals(df):
    """
    Generate trading signals based on predictions.
    """
    if df.empty:
        print("DataFrame is empty after predictions")
        return None, None, None, None

    buy_signal = df[df['predicted'] == 1]['close'].min()
    sell_signal = df[df['predicted'] == 0]['close'].max()
    stop_loss = buy_signal * 0.98 if buy_signal is not None else None  # Example: 2% below buy price

    # Calculate percentage change between buy and sell signals
    percent_change = ((sell_signal - buy_signal) / buy_signal * 100) if buy_signal and sell_signal else None
    
    return buy_signal, sell_signal, stop_loss, percent_change

def print_signals(symbol, buy_signal, sell_signal, stop_loss, percent_change):
    """
    Print the generated trading signals without the date.
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
    if pd.notna(percent_change):
        print(f"Percentage Change: {percent_change:.2f}%")
    else:
        print("No Percentage Change")

def process_symbol(symbol, start_date, end_date, interval):
    """
    Process a single symbol through the full pipeline.
    """
    df = import_data_yf(symbol, start_date, end_date, interval)
    df = calculate_indicators(df)
    
    if df.empty:
        print(f"No data available for {symbol} after importing and calculating indicators")
        return

    features, labels = prepare_data(df)
    model = train_model(features, labels)
    df = make_predictions(df, model)
    buy_signal, sell_signal, stop_loss, percent_change = generate_signals(df)
    print_signals(symbol, buy_signal, sell_signal, stop_loss, percent_change)

def main():
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'SOXS', 'MRVL', 'KO']  # List of symbols to process
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    interval = '5m'
    
    for symbol in symbols:
        process_symbol(symbol, start_date, end_date, interval)

if __name__ == "__main__":
    main()