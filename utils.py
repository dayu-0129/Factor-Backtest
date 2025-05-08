#build cross section
import os
import pandas as pd
import numpy as np
#generate return data
def generate_ret_df(data_dir):
    all_ret = []
    for filename in os.listdir("data"):
            if filename.endswith(".csv"):
                filepath = os.path.join("data", filename)
                try:
                    df = pd.read_csv(filepath, parse_dates=['date'])
                    df = df.sort_values(by='date')
                    df['ret'] = np.log(df['Close'] / df['Close'].shift(1))
                    df['stock_code'] = filename.replace(".csv", "")
                    df = df[['date', 'stock_code', 'ret']].dropna()
                    all_ret.append(df)
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")

                #combine all the return data
    ret_df = pd.concat(all_ret)
    ret_df = ret_df.sort_values(by=['date', 'stock_code'])
    ret_df.to_csv('./data2/ret_df.csv', index=False)
    return ret_df
#generate volumn volatility df
def generate_volume_volatility_df(data_dir):
    all_factors = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(data_dir, filename)
            try:
                df = pd.read_csv(filepath, parse_dates=['date'])
                df = df.sort_values(by='date')
                df['stock_code'] = filename.replace(".csv", "")
                df['volume_volatility'] = df['Volume'].pct_change().rolling(20).std()
                df = df[['date', 'stock_code', 'volume_volatility']].dropna()
                all_factors.append(df)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
    
    factor_df = pd.concat(all_factors)
    factor_df = factor_df.sort_values(by=['date', 'stock_code'])
    factor_df.to_csv('./data2/volume_volatility_df.csv', index=False)
    return factor_df
#generate momentum df
def generate_momentum_df(data_dir):
    all_factors = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(data_dir, filename)
            try:
                df = pd.read_csv(filepath, parse_dates=['date'])
                df = df.sort_values(by='date')
                df['stock_code'] = filename.replace(".csv", "")
                df['momentum'] = np.log(df['Close'] / df['Close'].shift(20))
                df = df[['date', 'stock_code', 'momentum']].dropna()
                all_factors.append(df)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
    
    factor_df = pd.concat(all_factors)
    factor_df = factor_df.sort_values(by=['date', 'stock_code'])
    factor_df.to_csv('./data2/momentum_df.csv', index=False)
    return factor_df
