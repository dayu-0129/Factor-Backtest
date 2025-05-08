#preprocess includes del_outlier and stanardize
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
#delete outlier( using mad method)
def del_outlier(factor_df, factor_name, method="mad", n=3):
    def mad_clip(x):
        med = x.median()
        mad = np.median(np.abs(x - med))
        upper = med + n * 1.4826 * mad
        lower = med - n * 1.4826 * mad
        return x.clip(lower, upper)
    factor_df = factor_df.copy()
    factor_df[factor_name] = factor_df.groupby("date")[factor_name].transform(mad_clip)
    return factor_df
#zscore standardize
def zscore_standardize(factor_df, factor_name):
    factor_df = factor_df.copy()
    factor_df[factor_name] = factor_df.groupby("date")[factor_name].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    return factor_df

