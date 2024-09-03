import alpaca_trade_api as tradeapi

def get_account():

    # Reemplaza estos valores con tus credenciales de Alpaca
    API_KEY = ''
    API_SECRET = ''
    BASE_URL = 'https://paper-api.alpaca.markets'  # Usa este URL para el entorno de paper trading; para live trading, usa 'https://api.alpaca.markets'

    # Crear una instancia de la API
    api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

    # Verifica la conexión
    account = api.get_account()
    print(f"Account ID: {account.id}, Cash Balance: {account.cash}")