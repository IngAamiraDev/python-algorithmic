import yfinance as yf
from datetime import datetime, timedelta

def download_and_clean_yf_data(symbol):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        df = df.drop(columns=["Adj Close", "Volume"])
        df.index.name = "time"
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    return df

df = download_and_clean_yf_data("AAPL")
if df is not None:
    print(df)
