import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from charts import setup_plot_styling
from utils import import_data_yf, clear_directory

def compare_years(df, year1, year2, path, symbol):
    """Plot and compare the closing prices of two years."""
    plt.figure(figsize=(15, 6))
    df_year1 = df[df.index.year == year1]
    df_year2 = df[df.index.year == year2]
    plt.plot(df_year1.index, df_year1['close'], label=f'Close Price {year1}', color='blue', alpha=0.7)
    plt.plot(df_year2.index, df_year2['close'], label=f'Close Price {year2}', color='orange', alpha=0.7)
    plt.title(f'Comparison of Close Prices: {year1} vs {year2}')
    plt.legend()
    plt.savefig(f'{path}compare_{year1}_vs_{year2}_{symbol}.png')
    plt.close()

def compare_same_month(df, month, year1, year2, path, symbol):
    """Plot and compare the closing prices of the same month in two different years."""
    plt.figure(figsize=(15, 6))
    df_year1 = df[(df.index.year == year1) & (df.index.month == month)]
    df_year2 = df[(df.index.year == year2) & (df.index.month == month)]
    plt.plot(df_year1.index, df_year1['close'], label=f'Close Price {year1}-{month:02}', color='blue', alpha=0.7)
    plt.plot(df_year2.index, df_year2['close'], label=f'Close Price {year2}-{month:02}', color='orange', alpha=0.7)
    plt.title(f'Comparison of Close Prices: {year1}-{month:02} vs {year2}-{month:02}')
    plt.legend()
    plt.savefig(f'{path}compare_{year1}_{year2}_{month:02}_{symbol}.png')
    plt.close()

def run():
    year1 = 2022
    year2 = 2023
    month = 7
    symbol = "AAPL"
    path = './img/'
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365 * 2)).strftime('%Y-%m-%d')
    df = import_data_yf(symbol, start_date, end_date)
    clear_directory(path)
    setup_plot_styling()
    compare_years(df, year1, year2, path, symbol)
    compare_same_month(df, month, year1, year2, path, symbol)

if __name__ == '__main__':
    run()