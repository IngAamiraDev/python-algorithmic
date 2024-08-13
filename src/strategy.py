import numpy as np

def get_sma(df):        
    try:
        #Simple Mobile Average per 30 and 60 days  
        df["SMA_fast"] = df["Close"].rolling(30).mean()
        df["SMA_slow"] = df["Close"].rolling(60).mean()        
        
        # Create the condition
        df["Position"]=np.nan
        df.loc[(df["SMA_fast"] > df["SMA_slow"]), "Position"] = 1  #Buy
        df.loc[(df["SMA_fast"] < df["SMA_slow"]), "Position"] = -1 #Sell
    except Exception as e: 
        print(f"An error occurred: {e}")
        return None
    
    return df