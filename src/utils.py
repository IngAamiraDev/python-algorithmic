import os
import glob
import yfinance as yf

def import_data_yf(symbol, start_date, end_date):
    """Download financial data using yfinance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        df.columns = ["open", "high", "low", "close", "adj close", "volume"]
        df.index.name = "time"  
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    return df

def clear_directory(path):
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

def create_directory(output_dir):
    """Create the output directory if it does not exist."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory {output_dir} created or already exists.")