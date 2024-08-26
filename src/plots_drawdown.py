import matplotlib.pyplot as plt

def view_plot_drawdown(drawdown):
    """The drawdown represents the percentage decline from the highest peak to the subsequent trough over a specific period."""
    plt.figure(figsize=(15, 8))    
    plt.fill_between(drawdown.index, drawdown*100, 0,drawdown, color="#CE5757", alpha=0.65)
    plt.xlabel("Time")
    plt.ylabel("Drawdown (%)")
    plt.title("Drawdown")
    plt.grid(True)