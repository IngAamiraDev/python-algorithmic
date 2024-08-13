import numpy as np

def get_sma(df):        
    try:
        #Simple Mobile Average per 30 and 60 days  
        df["sma_fast"] = df["close"].rolling(30).mean()
        df["sma_slow"] = df["close"].rolling(60).mean()        
        
        # Create the condition
        df["position"]=np.nan
        df.loc[(df["sma_fast"] > df["sma_slow"]), "position"] = 1  #Buy
        df.loc[(df["sma_fast"] < df["sma_slow"]), "position"] = -1 #Sell

        # Calcular el porcentaje de variación del activo
        df["pct"] = df["close"].pct_change(1)

        # Calcular la rentabilidad (retorno) de la estrategia
        df["return"] = df["pct"] * df["position"].shift(1)
    except Exception as e: 
        print(f"An error occurred: {e}")
        return None
    
    return df