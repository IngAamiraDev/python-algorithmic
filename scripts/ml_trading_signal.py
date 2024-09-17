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

def prepare_data(df):
    """
    Prepare data for machine learning model.
    """
    if df.empty:
        print("DataFrame is empty after calculations")
        return None, None

    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    features = df[['SMA fast', 'SMA slow', 'rsi']].values
    labels = df['target'].values

    if len(features) == 0 or len(labels) == 0:
        print("Features or labels are empty")
        return None, None
    
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

def accumulate_signals(signals_list, symbol, buy_signal, sell_signal, stop_loss, percent_change):
    """
    Accumulate the generated trading signals into a list.
    """
    signals_list.append({
        'Symbol': symbol,
        'Buy': f"{buy_signal:.2f}" if pd.notna(buy_signal) else 'No Buy Signal',
        'Sell': f"{sell_signal:.2f}" if pd.notna(sell_signal) else 'No Sell Signal',
        'Stop-Loss': f"{stop_loss:.2f}" if pd.notna(stop_loss) else 'No Stop-Loss Trigger',
        'Percentage-Change': f"{percent_change:.2f}%" if pd.notna(percent_change) else 'No Percentage Change'
    })

def process_symbol(symbol, start_date, end_date, interval, signals_list):
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
    accumulate_signals(signals_list, symbol, buy_signal, sell_signal, stop_loss, percent_change)

def main():
    symbols = [
        'TM', 'INTC', 'NXT', 'AFRM', 'DELL', 'PFE', 'RDDT', 'ABT', 'CAVA', 'BBY',
        'MRVL', 'KMB', 'DDOG', 'LEVI', 'UBER', 'CPB', 'DD', 'MAT', 'V', 'PAYX',
        'RACE', 'MKC', 'SWK', 'TGT', 'HSY', 'AVGO', 'MCD', 'TJX', 'SOFI', 'SCHW', 'BAC',
        'BROS', 'BOWL', 'NFLX', 'SHOP', 'GM', 'WM', 'EMR', 'GS', 'LIN', 'MP',
        'BRK-B', 'WMT', 'NUE', 'PINS', 'SLB', 'DHR', 'JNJ', 'HD', 'ADBE', 'CAT',
        'ULTA', 'HON', 'AMAT', 'LULU', 'SBUX', 'HUM', 'JPM', 'MS', 'CMG', 'PG',
        'AEP', 'MSFT', 'GOOG', 'CSCO', 'VZ', 'WFC', 'SNOW', 'ABNB', 'MA', 'AXP',
        'CRM', 'PYPL', 'HPE', 'DRI', 'GIS', 'BABA', 'TSM', 'CEG', 'BIIB', 'GOLD',
        'O', 'AMD', 'NVDA', 'META', 'GOOGL', 'KO', 'RCL', 'PLTR', 'ARM', 'STZ',
        'COST', 'ETN', 'TTWO', 'INTU', 'WING', 'BA', 'MELI', 'DKNG', 'NKE', 'GAP',
        'PANW', 'PEP', 'DIS', 'OTIS', 'GTLB', 'MDB', 'TSLA', 'SARK', 'SOXS', 'TMF', 'VST',
        'SMMT'
    ]
    #end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    #start_date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    start_date = '2024-09-11'
    end_date = '2024-09-13'
    interval = '5m'
    
    signals_list = []
    
    for symbol in symbols:
        process_symbol(symbol, start_date, end_date, interval, signals_list)
    
    # Convert the list of signals into a DataFrame
    signals_df = pd.DataFrame(signals_list)

    # Convert 'Percentage-Change' to numeric for sorting
    signals_df['Percentage-Change'] = signals_df['Percentage-Change'].str.replace('%', '').astype(float, errors='ignore')

    # Sort by 'Percentage-Change' in descending order
    signals_df = signals_df.sort_values(by='Percentage-Change', ascending=False)
    
    # Print the sorted DataFrame without index
    print(signals_df.to_string(index=False))

if __name__ == "__main__":
    main()