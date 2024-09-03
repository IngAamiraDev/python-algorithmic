import pandas as pd
import yfinance as yf

# Descargar datos históricos de una acción (por ejemplo, AAPL)
data = yf.download('SOXS', start='2024-06-01', end='2024-08-31')

# Calcular la media móvil de 20 días (SMA)
data['SMA_20'] = data['Close'].rolling(window=20).mean()

# Identificar oportunidades de compra cuando el precio cruza por encima de la SMA de 20 días
data['Signal'] = 0
data.loc[data['Close'] > data['SMA_20'], 'Signal'] = 1
data['Position'] = data['Signal'].diff()

# Mostrar los puntos de entrada y salida
buy_signals = data[data['Position'] == 1]
sell_signals = data[data['Position'] == -1]

print("Puntos de compra:")
print(buy_signals[['Close', 'SMA_20']])

print("\nPuntos de venta:")
print(sell_signals[['Close', 'SMA_20']])