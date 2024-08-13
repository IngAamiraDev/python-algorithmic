import numpy as np
import pandas as pd
import yfinance as yf

#NVDA
#AAPL

def preprocessing_yf(symbol):
    df = yf.download(symbol).dropna()

    df.columns = ["open", "high", "low", "close", "adj close", "volume"]
    df.index.name = "time"

    del df["adj close"]

    return df


df = preprocessing_yf("AAPL")
# print(df)

# Simple Mobile Average per 30 days
df["SMA fast"] = df["close"].rolling(30).mean()

# Simple Mobile Average per 60 days
df["SMA slow"] = df["close"].rolling(60).mean()

# Plot the results
#df[["close", "SMA fast", "SMA slow"]].plot(figsize=(15,8))

# Plot the results
#df[["close", "SMA fast", "SMA slow"]].loc["2020"].plot(figsize=(15,8))

df["position"]=np.nan

# Create the condition
df.loc[(df["SMA fast"] > df["SMA slow"]), "position"] = 1
df.loc[(df["SMA fast"] < df["SMA slow"]), "position"] = -1

print(df)