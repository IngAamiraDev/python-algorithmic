import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from src.charts import setup_plot_styling
from utils import import_data_yf

def compare_years(df, year1, year2):
    """Plot and compare the closing prices of two years."""
    plt.figure(figsize=(15, 6))
    df_year1 = df[df.index.year == year1]
    df_year2 = df[df.index.year == year2]
    plt.plot(df_year1.index, df_year1['close'], label=f'Close Price {year1}', color='blue', alpha=0.7)
    plt.plot(df_year2.index, df_year2['close'], label=f'Close Price {year2}', color='orange', alpha=0.7)
    plt.title(f'Comparison of Close Prices: {year1} vs {year2}')
    plt.legend()
    plt.savefig(f'./img/compare_{year1}_vs_{year2}.png')
    plt.close()

def run():
    year1 = 2023
    year2 = 2024
    symbol = "AAPL"
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365 * 2)).strftime('%Y-%m-%d')
    df = import_data_yf(symbol, start_date, end_date)
    setup_plot_styling()
    compare_years(df, year1, year2)

if __name__ == '__main__':
    run()