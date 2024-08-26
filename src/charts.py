import matplotlib.pyplot as plt
from matplotlib import cycler

def setup_plot_styling():
    """Setup custom plot styling."""
    colors = cycler('color', ['#669FEE', '#66EE91', '#9988DD', '#EECC55', '#88BB44', '#FFBBBB'])
    plt.rc('figure', facecolor='#313233')
    plt.rc('axes', facecolor="#313233", edgecolor='none', axisbelow=True, grid=True, prop_cycle=colors, labelcolor='gray')
    plt.rc('grid', color='#474A4A', linestyle='solid')
    plt.rc('xtick', color='gray')
    plt.rc('ytick', direction='out', color='gray')
    plt.rc('legend', facecolor="#313233", edgecolor="#313233")
    plt.rc("text", color="#C9C9C9")

def save_plot(name, symbol, output_dir):
    """Save the plot to the specified directory."""
    plt.savefig(f'{output_dir}/{name}_{symbol}.png')
    plt.close()