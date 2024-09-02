from datetime import datetime, timedelta
import numpy as np

from src.plots_sma import (
    view_plot_sma_30_60, verify_plot_signals_sma_30_60, 
    view_plot_sma_200_50_20, verify_plot_signals_sma_200_50_20, 
    plot_profits_sma
)
from src.plots_drawdown import view_plot_drawdown
from src.charts import setup_plot_styling, save_plot
from src.strategy import (
    get_sma_30_60, get_sma_200_50_20, 
    get_sortino, get_beta, get_alpha, get_drawdown
)
from src.utils import import_data_yf, clear_directory, create_directory

def run():
    """Main function to download data, generate and save plots for each symbol."""
    year = "2024"
    output_dir = './img/'
    symbols = ["AAPL", "MSFT", "AMZN", "META", "GOLD", "O"]
    symbol_sp500 = "^GSPC"
    
    # Setup plot styling and manage output directory
    setup_plot_styling()
    clear_directory(output_dir)
    create_directory(output_dir)

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    for symbol in symbols:
        print(f"Processing {symbol}...")

        # Download data for the symbol
        df = import_data_yf(symbol, start_date, end_date)
        
        if df is not None:
            # Strategy 1: SMA 30/60
            sma_30_60 = get_sma_30_60(df)
            plot_functions_30_60 = [
                ("view_plot_sma_30_60", view_plot_sma_30_60, []),
                ("verify_signals_sma_30_60", verify_plot_signals_sma_30_60, [year]),
                ("profits_sma_30_60", plot_profits_sma, []),
            ]

            for plot_name, plot_func, args in plot_functions_30_60:
                plot_func(sma_30_60, *args)
                save_plot(plot_name, symbol, output_dir)
            
            # Strategy 2: SMA 200/50/20
            sma_200_50_20 = get_sma_200_50_20(df)
            plot_functions_200_50_20 = [
                ("view_plot_sma_200_50_20", view_plot_sma_200_50_20, []),
                ("verify_signals_sma_200_50_20", verify_plot_signals_sma_200_50_20, []),
                ("profits_sma_200_50_20", plot_profits_sma, []),
            ]

            for plot_name, plot_func, args in plot_functions_200_50_20:
                plot_func(sma_200_50_20, *args)
                save_plot(plot_name, symbol, output_dir)
            
            # Calculate and print financial metrics
            sortino = get_sortino(df)
            print(f"Sortino: {'%.3f' % sortino}")
            
            df_sp500 = import_data_yf(symbol_sp500, start_date, end_date)
            beta = get_beta(df, df_sp500)
            print(f"Beta: {'%.3f' % beta}")
            
            alpha = get_alpha(df, beta)
            print(f"Alpha: {'%.1f' % alpha} %")

            drawdown = get_drawdown(df)
            max_drawdown = -np.min(drawdown)*100
            view_plot_drawdown(drawdown)
            save_plot("view_plot_drawdown", symbol, output_dir)
            print(f"Max drawdown: {'%.1f' % max_drawdown} %")

if __name__ == '__main__':
    run()