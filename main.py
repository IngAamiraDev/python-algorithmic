from src.charts_sma import setup_plot_styling, plot_signals, save_plot
from src.utils import import_data_yf, clear_directory, create_directory
from src.strategy import get_sma

def run():
    """Main function to download data, generate and save the plot."""
    symbol = "AAPL"
    year = "2024"
    output_dir = './img/'
    
    setup_plot_styling()
    clear_directory(output_dir)
    create_directory(output_dir)
    
    df = import_data_yf(symbol)
    sma = get_sma(df)
    
    if sma is not None:
        plot_signals(sma, year)
        save_plot(symbol, output_dir)

if __name__ == '__main__':
    run()