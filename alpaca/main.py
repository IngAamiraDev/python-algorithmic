from src.utils import import_data_yf
from src.cnx_alpaca import get_account

def run():
    symbol = 'AAPL'
    start_date = '2024-08-05'
    end_date = '2024-08-10'
    df = import_data_yf(symbol, start_date, end_date)
    cnx = get_account()
    print(df.head())
    print(cnx)

if __name__ == '__main__':
    run()