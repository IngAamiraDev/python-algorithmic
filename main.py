from datetime import datetime, timedelta

from src.plots_sma import view_plot_sma, verify_plot_signals_sma, plot_profits_sma
from src.charts import setup_plot_styling, save_plot
from src.utils import import_data_yf, clear_directory, create_directory
from src.strategy import get_sma, get_sortino, get_beta, get_alpha

def run():
    """Main function to download data, generate and save plots."""
    year = "2024"
    output_dir = './img/'
    symbol = "AAPL"
    symbol_sp500 = "^GSPC"
    
    # Setup plot styling and manage output directory
    setup_plot_styling()
    clear_directory(output_dir)
    create_directory(output_dir)

    # Download data for both years
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    df = import_data_yf(symbol, start_date, end_date)
    
    if df is not None:
    
        # Generate and save plots
        sma = get_sma(df)
        plot_functions = [
            ("view_plot_sma", view_plot_sma, []),
            ("verify_signals_sma", verify_plot_signals_sma, [year]),
            ("profits_sma", plot_profits_sma, []),
        ]

        for plot_name, plot_func, args in plot_functions:
            plot_func(sma, *args)
            save_plot(plot_name, symbol, output_dir)
        
        # Calculate and print financial metrics
        sortino = get_sortino(df)
        print(f"Sortino: {'%.3f' % sortino}")
        
        df_sp500 = import_data_yf(symbol_sp500, start_date, end_date)
        beta = get_beta(df, df_sp500)
        print(f"Beta: {'%.3f' % beta}")
        
        alpha = get_alpha(df, beta)
        print(f"Alpha: {'%.1f' % alpha} %")

if __name__ == '__main__':
    run()