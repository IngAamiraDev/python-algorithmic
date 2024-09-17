import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Descargar los datos históricos
def download_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['RSI'] = compute_rsi(data['Close'], 14)
    return data

# Calcular el RSI
def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Estrategia MA-RSI Day Trading
def ma_rsi_day_trading_strategy(data):
    buy_signals = []
    sell_signals = []
    
    for i in range(len(data)):
        if data['MA5'][i] > data['MA20'][i] and data['RSI'][i] < 30:
            buy_signals.append(data['Close'][i])
            sell_signals.append(np.nan)
        elif data['MA20'][i] > data['MA5'][i] and data['RSI'][i] > 70:
            buy_signals.append(np.nan)
            sell_signals.append(data['Close'][i])
        else:
            buy_signals.append(np.nan)
            sell_signals.append(np.nan)

    data['Buy_Signal'] = buy_signals
    data['Sell_Signal'] = sell_signals

# Gráfica de la estrategia
def plot_trading_signals(data, ticker):
    plt.figure(figsize=(14,8))
    plt.plot(data['Close'], label=f'{ticker} Close Price', alpha=0.5)
    plt.plot(data['MA5'], label='MA 5', alpha=0.75)
    plt.plot(data['MA20'], label='MA 20', alpha=0.75)
    plt.scatter(data.index, data['Buy_Signal'], label='Buy Signal', marker='^', color='green', alpha=1)
    plt.scatter(data.index, data['Sell_Signal'], label='Sell Signal', marker='v', color='red', alpha=1)
    plt.title(f'{ticker} MA-RSI Day Trading Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(loc='best')
    plt.grid()
    plt.show()

# Función principal
def main():
    ticker = 'AAPL'  # Puede cambiar el símbolo
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    
    # Descargar y procesar datos
    data = download_data(ticker, start=start_date, end=end_date)
    
    # Aplicar la estrategia de trading
    ma_rsi_day_trading_strategy(data)
    
    # Graficar señales de compra y venta
    plot_trading_signals(data, ticker)

if __name__ == "__main__":
    main()