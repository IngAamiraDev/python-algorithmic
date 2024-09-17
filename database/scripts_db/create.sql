
CREATE TABLE trading_tracker (
    id_trade SERIAL PRIMARY KEY,
    date_trade DATE,
    status VARCHAR(10),
	tickers VARCHAR(10),
    shares NUMERIC(10, 2),
	cost_shares NUMERIC(10, 2),
	cost_basis NUMERIC(10, 2),
	count_day_trading INT,
	pdt_alert VARCHAR(10),
	last_buy_price NUMERIC(10, 2),
	profit_Loss NUMERIC(10, 2)
);