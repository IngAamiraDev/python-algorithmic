from collections import deque
from datetime import datetime, timedelta

class DayTradeTracker:
    def __init__(self):
        self.trades = deque(maxlen=5)  # Mantiene las fechas de las últimas 5 operaciones

    def add_trade(self, trade_date):
        # Convierte la fecha de la operación a formato datetime
        trade_date = datetime.strptime(trade_date, '%Y-%m-%d')
        self.trades.append(trade_date)
        self.trades = deque([d for d in self.trades if d >= datetime.now() - timedelta(days=5)])
        
        return len(self.trades)

    def can_trade(self):
        # Si hay menos de 3 operaciones en los últimos 5 días hábiles, se permite el trading
        return len(self.trades) < 3

# Ejemplo de uso
tracker = DayTradeTracker()

# Añadir operaciones (asegúrate de usar fechas válidas)
tracker.add_trade('2024-09-01')
tracker.add_trade('2024-09-02')
tracker.add_trade('2024-09-03')

if tracker.can_trade():
    print("Puedes realizar un day trade sin exceder el límite PDT.")
else:
    print("Has alcanzado el límite de day trades para los últimos 5 días.")