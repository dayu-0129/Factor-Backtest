import os
from tqdm import tqdm
import yfinance as yf
import pandas as pd
import time
table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
tickers = table[0]['Symbol'].tolist()
tickers=[t.replace(".", "-") for t in tickers]
os.makedirs("data", exist_ok=True)

for ticker in tqdm(tickers):
    try:
            df = yf.download(ticker, start="2018-01-01", end="2023-12-31", progress=False)
            if df.empty or len(df) < 200:
                continue
            df.to_csv(os.path.join("data", f"{ticker}.csv"))
            time.sleep(0.3)
            if df[['Close', 'Volume']].isna().mean().mean() > 0.3 or len(df) < 200:
                 continue
    except Exception as e:
         print(f"Failed to download {ticker}: {e}")

    

