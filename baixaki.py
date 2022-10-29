import pandas as pd
import numpy as np
import yfinance as yf
import threading
import pickle


file_df = pd.read_csv("etf_funds/historical_data2.csv")
fund_names = list(file_df.columns[1:].values)
fund_returns = []
fund_vol  = []
fund_sharpe = []


for fund in fund_names:
    fund_list = file_df[fund].values
    fund_return = (fund_list[-1] - fund_list[0]) / fund_list[0]
    fund_volatility = file_df[fund].pct_change().std() * np.sqrt(252)
    
    fund_returns.append(fund_return)
    fund_vol.append(fund_volatility)
    fund_sharpe.append(fund_return / fund_volatility)

df_final = pd.DataFrame(data={ 
    "Symbol": fund_names, 
    "1Y Return": fund_returns, 
    "1Y Volatility": fund_vol, 
    "1Y Sharpe": fund_sharpe 
})

df_final = df_final.dropna()

fund_holdings = {}
unique_assets = []
error_list = []
thread_list = []

sem = threading.Semaphore(30)

def baixaki(fund_name):
    global fund_holdings
    global unique_assets
    global error_list
    global sem
    sem.acquire()

    try:
        asset = yf.Ticker(fund_name)
        holdings_info = asset.get_info()['holdings']
        holdings = {}
        
        for holding in holdings_info:
            holdings[holding["holdingName"]] = holding["holdingPercent"]
            unique_assets.append(holding["holdingName"])
        
        fund_holdings[fund_name] = holdings
        print(fund_name)
    except:
        error_list.append(fund)

    sem.release()

for fund in list(df_final["Symbol"].values):
    x = threading.Thread(target=baixaki, args=(fund,))
    thread_list.append(x)
    x.start()

for thread in thread_list:
    thread.join()

f = open('fund_holdings2.pckl', 'wb')
pickle.dump(fund_holdings, f)
f.close()

f = open('unique_assets2.pckl', 'wb')
pickle.dump(list(set(unique_assets)), f)
f.close()


f = open('error_list2.pckl', 'wb')
pickle.dump(error_list, f)
f.close()
