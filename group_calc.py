import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr
#seperate group data by factor
def get_stock_group(factor_df, factor_name, n_groups=5):
    factor_df = factor_df.copy()
    def assign_group(x):
        x = x.dropna(subset=[factor_name])
        x[factor_name + '_group'] = pd.qcut(x[factor_name], q=n_groups, labels=False, duplicates='drop')
        return x

    factor_df = factor_df.groupby("date", group_keys=False).apply(assign_group)
    return factor_df

#calculate group return
def get_group_ret(factor_df, ret_df, factor_name, n_groups=5, mktmv_df=None):
    """
    calculate the portfolio return rate by factor grouping 
    """
    # get factor one period in advance
    prev_factor_df = factor_df.copy()
    prev_factor_df['date'] = prev_factor_df['date'].shift(1)
    prev_mktmv_df = prev_factor_df[['date', 'stock_code']].copy()
    prev_mktmv_df['mktmv'] = 1  # equal weights to all stock

    # combine factordf returndf and weights
    df = pd.merge(ret_df, prev_factor_df, on=['date', 'stock_code'], how='inner')
    df = pd.merge(df, prev_mktmv_df, on=['date', 'stock_code'], how='inner')
    #seperate 
    df = get_stock_group(df, factor_name, n_groups)
    # calculate returns of different groups
    group_ret = df.groupby(['date', factor_name + '_group'])['ret'].mean().reset_index()
    group_ret.columns = ['date', 'group', 'ret']

    # convert to wide 
    group_ret_wide = group_ret.pivot(index='date', columns='group', values='ret')
    group_ret_wide.columns = [f'Group{int(c)}' for c in group_ret_wide.columns]

    # calculate H-L
    group_ret_wide['H-L'] = group_ret_wide[f'Group{n_groups - 1}'] - group_ret_wide['Group0']
    group_ret_wide = group_ret_wide.sort_index()
    
    return group_ret_wide


def get_group_ret_backtest(group_ret, rf=0.0, period='DAILY'):
    """
    calculate the performance indicators of different groups
    indicatiors:annual return,annul volatility,sharpe ratio,maxdrawdown
    """
    freq_map = {'DAILY': 252, 'WEEKLY': 52, 'MONTHLY': 12}
    ann_factor = freq_map.get(period.upper(), 252)

    result = {}
    for col in group_ret.columns:
        ret = group_ret[col].dropna()
        if len(ret) == 0:
            continue
        cum = (1 + ret).cumprod()
        peak = cum.cummax()
        dd = (peak - cum) / peak
        maxdd = dd.max()

        ann_ret = ret.mean() * ann_factor
        ann_vol = ret.std() * np.sqrt(ann_factor)
        sharpe = (ann_ret - rf) / ann_vol if ann_vol != 0 else np.nan

        result[col] = {
            "annual return(%)": ann_ret * 100,
            "annual volatility(%)": ann_vol * 100,
            "sharpe ratio": sharpe,
            "max drawdown(%)": maxdd * 100
        }

    return pd.DataFrame(result)
#plot net value graph

def analysis_group_ret(
    factor_df,
    ret_df,
    factor_name,
    n_groups,
    mktmv_df=None,
    rf=0,
    period="DAILY",
):
    group_ret = get_group_ret(factor_df, ret_df, factor_name, n_groups, mktmv_df)
    backtest_df = get_group_ret_backtest(group_ret, rf=rf, period=period)

    time_idx = pd.to_datetime(group_ret.index)
    factor_ret = group_ret["H-L"]
    weight_name = "equal weight" 

    # net value of different groups
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    for col in group_ret.columns:
        if col != 'H-L':
            net_value = (1 + group_ret[col]).cumprod()
            ax1.plot(time_idx, net_value, label=col)
    ax1.set_title(f" {factor_name} net value ({weight_name})")
    ax1.set_xlabel("date")
    ax1.set_ylabel("net value")
    ax1.grid(True)
    ax1.legend()

    # H-L net value
    fig2, ax2 = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax2[0].bar(time_idx, 100 * factor_ret, label='factor long short return rate(%)')
    ax2[0].set_ylabel("factor long short return rate(%)")
    ax2[0].grid(True)

    cum = (1 + factor_ret).cumprod() - 1
    ax2[1].plot(time_idx, 100 * cum, label='factor long short return rate(%)')
    ax2[1].set_xlabel("date")
    ax2[1].set_ylabel("factor long short return rate(%)")
    ax2[1].grid(True)

    fig2.suptitle(f" {factor_name} factor long short return rate ({weight_name})")

    return backtest_df, fig1, fig2

#IC calculation


def prepare_ic_data(factor_df, ret_df, factor_name='momentum'):    
    merged_df = pd.merge(factor_df, ret_df, on=['date', 'stock_code'], how='inner')
    merged_df = merged_df.rename(columns={'ret': 'next_ret'})
    return merged_df[['date', 'stock_code', factor_name, 'next_ret']].dropna()

def calc_ic_series(merged_df, factor_name='momentum'):
    ic_series = merged_df.groupby('date').apply(
        lambda x: spearmanr(x[factor_name], x['next_ret'])[0]
    )
    ic_series.name = 'IC'
    return ic_series

def summarize_ic(ic_series):
    ic_series = ic_series.dropna()
    ic_mean = ic_series.mean()
    ic_std = ic_series.std()
    ic_ir = ic_mean / ic_std
    pos_ratio = (ic_series > 0).mean()

    summary = pd.DataFrame({
        "IC Mean": [ic_mean],
        "IC Std": [ic_std],
        "IC IR": [ic_ir],
        "IC > 0 Ratio": [pos_ratio]
    }).T
    summary.columns = ["Value"]
    return summary

def plot_ic_series(ic_series):
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    ic_series.plot(title='IC Time Series')
    plt.axhline(0, color='gray', linestyle='--')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    ic_series.cumsum().plot(title='Cumulative IC')
    plt.axhline(0, color='gray', linestyle='--')
    plt.grid(True)

    plt.tight_layout()
    plt.show()
