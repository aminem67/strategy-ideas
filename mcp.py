
import numpy as np
import pandas as pd

import backtester
import viz

def perform_mcp(idea_name, asset_name='BTCUSDT', csv_filename='BTCUSDT_1d', pd_timeframe='1D'):

    fullname = 'data\\{}.csv'.format(csv_filename)
    df_data = get_data_frame(fullname)    
    
    runner_method = get_runner_method(idea_name)
    trades, df_rets = runner_method('BTCUSDT',
                                    csvFilePath=fullname, 
                                    pandasTimeFrame=pd_timeframe, 
                                    ema1_period=10, 
                                    ema2_period=20, 
                                    ema3_period=30)
    
    df_data = df_data.tail(df_rets.shape[0]+1)  
    
    df_rets = df_rets.dropna()
    df_signals = df_rets.where(df_rets == 0, 1)
    df_signals.columns = ['Signal']
    df_signals['MarketReturn'] = df_data['Close'].pct_change().dropna()
    df_signals['Return'] = df_signals['MarketReturn'] * df_signals['Signal']
    
    test_mean = round(df_signals['Return'].mean() * 100, 2)        
    
    sample_means = []
    for i in range(1, 10000):
        df_sample = df_signals.copy()        
        df_sample['Signal'] = np.random.permutation(df_signals['Signal'].values)
        df_sample['Return'] = df_sample['MarketReturn'] * df_sample['Signal']
        
        sample_mean = round(df_sample['Return'].mean() * 100, 2) 
        sample_means.append(sample_mean)
    
    viz.plot_histogram(sample_means, 
                           nBins=50, 
                           title='MCP Sample Means', 
                           test_mean=test_mean)

# %% Helper methods

def get_data_frame(filePath = "data\\BTCUSDT_1d.csv"):
    
    df = pd.read_csv(filePath,
                    parse_dates=['Date Time'],
                    usecols=['Date Time', 'Open', 'High', 'Low', 'Close'],
                    index_col='Date Time',
                    sep=',',
                    na_values=['NaN'])

    return df

def get_runner_method(idea_name):

    runner_methods = {
        'AS001':backtester.run_AS001
    }

    return runner_methods[idea_name]
