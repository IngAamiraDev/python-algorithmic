import matplotlib.pyplot as plt

def view_plot_sma_30_60(sma):
    """Plot the SMA (30/60) and price."""
    plt.figure(figsize=(15, 6))
    plt.plot(sma['close'], label='Close Price')
    plt.plot(sma['sma_fast'], label='SMA Fast (30)')
    plt.plot(sma['sma_slow'], label='SMA Slow (60)')
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.title("SMA 30/60 Plot")
    plt.grid(True)  # Added grid for better readability

def verify_plot_signals_sma_30_60(sma, year):
    """Plot buy/sell signals on the SMA 30/60 chart."""
    plt.figure(figsize=(15, 6))
    
    try:
        year_data = sma.loc[year]
        idx_open = year_data[year_data["position"] == 1].index
        idx_close = year_data[year_data["position"] == -1].index
        plt.scatter(idx_open, year_data.loc[idx_open]["close"], color="#57CE95", marker="^", label='Buy Signal')
        plt.scatter(idx_close, year_data.loc[idx_close]["close"], color="red", marker="v", label='Sell Signal')
        plt.plot(year_data["close"], alpha=0.35, label='Close Price')
        plt.plot(year_data["sma_fast"], alpha=0.35, label='SMA Fast (30)')
        plt.plot(year_data["sma_slow"], alpha=0.35, label='SMA Slow (60)')
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("SMA 30/60 Signals Verification")
        plt.legend()
        plt.grid(True)  # Added grid for better readability
    except KeyError:
        print(f"No data available for the year {year}")

def view_plot_sma_200_50_20(sma):
    """Plot the SMA (200/50/20) and price."""
    plt.figure(figsize=(15, 6))
    plt.plot(sma['close'], label='Close Price')
    plt.plot(sma['sma_200'], label='SMA 200', color="red")
    plt.plot(sma['sma_50'], label='SMA 50', color="blue")
    plt.plot(sma['sma_20'], label='SMA 20', color="yellow")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.title("SMA 200/50/20 Plot")
    plt.grid(True)  # Added grid for better readability

def verify_plot_signals_sma_200_50_20(sma):
    """Plot buy/sell signals on the SMA 200/50/20 chart."""
    plt.figure(figsize=(15, 6))
    
    try:
        idx_open = sma[sma["position"] == 1].index
        idx_close = sma[sma["position"] == -1].index
        plt.scatter(idx_open, sma.loc[idx_open]["close"], color="#57CE95", marker="^", label='Buy Signal')
        plt.scatter(idx_close, sma.loc[idx_close]["close"], color="red", marker="v", label='Sell Signal')
        plt.plot(sma["close"], alpha=0.35, label='Close Price')
        plt.plot(sma["sma_200"], alpha=0.35, label='SMA 200', color="red")
        plt.plot(sma["sma_50"], alpha=0.35, label='SMA 50', color="blue")
        plt.plot(sma["sma_20"], alpha=0.35, label='SMA 20', color="yellow")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("SMA 200/50/20 Signals Verification")
        plt.legend()
        plt.grid(True)  # Added grid for better readability
    except KeyError:
        print("An error occurred while plotting SMA 200/50/20 signals.")

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