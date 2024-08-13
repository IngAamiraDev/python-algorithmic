import os
import glob
import yfinance as yf
from datetime import datetime, timedelta

def import_data_yf(symbol):
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

def clear_directory(path):
    """Deletes all files in the specified directory."""
    files = glob.glob(os.path.join(path, '*'))
    for f in files:
        try:
            os.remove(f)
            print(f"Deleted: {f}")
        except Exception as e:
            print(f"Error deleting file {f}: {e}")

def create_directory(path):
    """Ensures the directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)