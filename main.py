from src.charts_sma import setup_plot_styling, view_plot_sma, verify_plot_signals_sma, save_plot, plot_profits_sma
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
        view_plot_sma(sma)
        save_plot("view_plot_sma",symbol, output_dir)        

        verify_plot_signals_sma(sma, year)
        save_plot("verify_signals_sma",symbol, output_dir)
        
        plot_profits_sma(sma)
        save_plot("profits_sma",symbol, output_dir)
        
        print(sma)

if __name__ == '__main__':
    run()