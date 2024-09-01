strategy = MLTrader(
    name='mlstrat', 
    broker=broker, 
    parameters={"symbol": "SPY","cash_at_risk":".5"})