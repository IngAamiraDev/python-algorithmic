import numpy as np
import pandas as pd

def get_sma(df):
    """Calculate Simple Moving Averages and generate trading signals."""        
    try:
        df["sma_fast"] = df["close"].rolling(30).mean()
        df["sma_slow"] = df["close"].rolling(60).mean()
        df["position"] = np.where(df["sma_fast"] > df["sma_slow"], 1, -1)
        df["pct"] = df["close"].pct_change(1)
        df["return"] = df["pct"] * df["position"].shift(1)
    except Exception as e: 
        print(f"An error occurred in get_sma: {e}")
        return None
    
    return df

def get_sortino(df):
    """Calculate the Sortino ratio."""
    try:
        return_serie = df["close"].pct_change(1).dropna()
        mean = np.mean(return_serie)
        negative_volatility = np.std(return_serie[return_serie < 0]) if len(return_serie[return_serie < 0]) > 0 else np.nan
        if negative_volatility == 0:
            print("Negative volatility is zero, Sortino ratio cannot be calculated.")
            return None
        sortino = np.sqrt(252) * mean / negative_volatility
    except Exception as e: 
        print(f"An error occurred in get_sortino: {e}")
        return None
    
    return sortino

def get_beta(df_symbol, df_sp500):
    """Calculate the Beta of the symbol against the S&P 500."""
    try:
        return_serie = df_symbol["close"].pct_change(1).dropna()
        sp500 = df_sp500["close"].pct_change(1).dropna()
        val = pd.concat([return_serie, sp500], axis=1).dropna()
        cov_var_mat = np.cov(val, rowvar=False)
        beta = cov_var_mat[0][1] / cov_var_mat[1][1] if cov_var_mat[1][1] != 0 else np.nan
    except Exception as e: 
        print(f"An error occurred in get_beta: {e}")
        return None
    
    return beta

def get_alpha(df_symbol, beta):    
    """Calculate the Alpha of the symbol against the S&P 500."""
    try:
        if beta is None:
            print("Beta value is None, Alpha cannot be calculated.")
            return None
        mean = np.mean(df_symbol["close"].pct_change(1).dropna())
        alpha = (252 * mean * (1 - beta)) * 100
    except Exception as e: 
        print(f"An error occurred in get_alpha: {e}")
        return None

    return alpha