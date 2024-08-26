import matplotlib.pyplot as plt

def view_plot_sma(sma):
    """Plot the SMA and price."""
    plt.figure(figsize=(15, 6))
    plt.plot(sma['close'], label='Close Price')
    plt.plot(sma['sma_fast'], label='SMA Fast (30)')
    plt.plot(sma['sma_slow'], label='SMA Slow (60)')
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.title("SMA Plot")
    plt.grid(True)  # Added grid for better readability

def verify_plot_signals_sma(sma, year):
    """Plot buy/sell signals on the SMA chart."""
    plt.figure(figsize=(15, 6))
    
    try:
        year_data = sma.loc[year]
        idx_open = year_data[year_data["position"] == 1].index
        idx_close = year_data[year_data["position"] == -1].index
        plt.scatter(idx_open, year_data.loc[idx_open]["close"], color="#57CE95", marker="^", label='Buy Signal')
        plt.scatter(idx_close, year_data.loc[idx_close]["close"], color="red", marker="v", label='Sell Signal')
        plt.plot(year_data["close"], alpha=0.35, label='Close Price')
        plt.plot(year_data["sma_fast"], alpha=0.35, label='SMA Fast')
        plt.plot(year_data["sma_slow"], alpha=0.35, label='SMA Slow')
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("SMA Signals Verification")
        plt.legend()
        plt.grid(True)  # Added grid for better readability
    except KeyError:
        print(f"No data available for the year {year}")

def plot_profits_sma(sma):
    """Plot the profits of the SMA strategy."""
    plt.figure(figsize=(15, 6))
    sma['cumulative_returns'] = (1 + sma['return']).cumprod().fillna(1)  # Fill NaN with 1 for initial value
    plt.plot(sma['cumulative_returns'], label='Cumulative Returns')
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.title("SMA Strategy Profits")
    plt.legend()
    plt.grid(True)  # Added grid for better readability