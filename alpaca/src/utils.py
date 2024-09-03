import yfinance as yf

def import_data_yf(symbol, start_date, end_date):
    """Download financial data using yfinance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        df.columns = ["open", "high", "low", "close", "adj close", "volume"]
        df.index.name = "time"  
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    return df