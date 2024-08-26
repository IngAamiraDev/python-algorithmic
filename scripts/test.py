import yfinance as yf
from datetime import datetime, timedelta

def import_data_yf(symbol, start_date, end_date):
    """Download financial data using yfinance."""
    try:
        # Downloading the data
        df = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        # Renaming and dropping unnecessary columns
        df.columns = ["open", "high", "low", "close", "adj close", "volume"]
        df = df.drop(columns=["adj close", "volume", "high", "low"])
        df.index.name = "time"

        return df  # Return the DataFrame instead of printing it

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Returning None if an error occurs

# Define symbol, start date, and end date
symbol = "AAPL"
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')

# Import the data and store it in a variable
data = import_data_yf(symbol, start_date, end_date)

# Print the data if it was successfully downloaded
if data is not None:
    print(data)