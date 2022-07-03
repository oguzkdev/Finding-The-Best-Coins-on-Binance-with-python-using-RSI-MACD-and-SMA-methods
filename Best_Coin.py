import pandas as pd
from binance.client import Client
from binance import ThreadedWebsocketManager
import ta
import numpy as np
import time
from datetime import datetime, timedelta

import sqlalchemy

import asyncio
from binance import AsyncClient,BinanceSocketManager

import nest_asyncio
nest_asyncio.apply()

class Signals:
    
    def __init__(self,symbol,interval,lookback,lags):
        self.symbol = symbol
        self.interval = interval
        self.lookback = lookback
        self.lags = lags
    
    def getminutedata(self):     
        frame = pd.DataFrame(client.get_historical_klines(self.symbol, self.interval, self.lookback + ' hour ago UTC')) #'min ago UTC' 'day' ya da 'hour' olarakta giriliyor
        frame = frame.iloc[:,:6]
        frame.columns = ['Time','Open','High','Low','Close','Volume']
        frame = frame.set_index('Time')
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype(float)
        return frame
    
    def applytechnicals(self):
        df = self.getminutedata()
        df['%K'] = ta.momentum.stoch(df.High, df.Low,df.Close, window=14, smooth_window=3)
        df['%D'] = df['%K'].rolling(3).mean()
        df['rsi'] = ta.momentum.rsi(df.Close, window=14)
        df['macd'] = ta.trend.macd_diff(df.Close)
        df['sma_s'] = ta.trend.sma_indicator(df.Close, window=50) #MA(50) for long position 
        df['sma_l'] = ta.trend.sma_indicator(df.Close, window=200) #MA(200) for long position
        df.dropna(inplace=True)
        return df
        
    def gettrigger(self):
        df = self.applytechnicals()
        dfx = pd.DataFrame()
        for i in range(self.lags + 1):
            mask = (df['%K'].shift(i) < 20) & (df['%D'].shift(i < 20))
            dfx = pd.concat([dfx,mask], axis=1, ignore_index=True)
        return dfx.sum(axis=1)
    
    def decide(self):
        df = self.applytechnicals()
        df['trigger'] = np.where(self.gettrigger(), 1, 0)
        df['Buy'] = np.where((df.trigger) & (df['%K'].between(20,80)) & (df['%D'].between(20,80)) & (df.rsi > 50) & (df.macd > 0) & (df.sma_s > df.sma_l) & (df.Close > df.sma_s) & (df.Close > df.sma_l) , 1, 0)
        df['Coin'] = self.symbol
        return df[df['Buy'] == 1]

class all_coins:
    
    def __init__(self,client): 
        self.client = client
        
    def get_top_symbol_sql(self):
        engine = sqlalchemy.create_engine('sqlite:///CryptoDB.db')
        all_pairs = pd.DataFrame(self.client.get_ticker())
        relev = all_pairs[all_pairs.symbol.str.contains('USDT')]
        non_lev = relev[~((relev.symbol.str.contains('UP')) | (relev.symbol.str.contains('DOWN')))]
        top_symbol = non_lev.sort_values(by='priceChangePercent', ascending=False)
        top_symbol.to_sql('crypto',engine, if_exists='replace',index=False)
        get_top_symbol_sql = pd.read_sql('crypto',engine)
        return get_top_symbol_sql
    
    def find_coins(self):
        coins=all_coins(client=client)
        symbols = coins.get_top_symbol_sql().symbol
        i=0
        liste_end = []
        
        for symbol in symbols:
            buy_signal = Signals(symbol = symbol, interval = interval, lookback = lookback, lags = lags)
            buysignal_df=pd.DataFrame(buy_signal.decide().tail(1))
            liste = np.array(buysignal_df)
            liste_1 = pd.DataFrame(liste)
            liste_df = liste_1.iloc[0,-1] 
            liste_end.append(liste_df)

            if i <= 4:
                liste_coin = liste_df
                i += 1
            else:
                i=0
                break
        return liste_end
    
    def best_coins(self):
        list_top = self.find_coins()
        list_top_coin=[]
        
        #************* Search Top Coins For Futures Trade *************
        
        for j in range(0,len(list_top)):     
            coin_base = list_top[j]
            info = client.get_symbol_info(coin_base)
            try:
                info['permissions'][1]
            except:
                j+=1
            if j==5:
                j=0
            
         #**************************************************************
            
           #******************** define strategy************************  
            
            coin_base_signal = Signals(symbol = coin_base, interval = interval, lookback = lookback, lags = lags)
            coin_base_df = coin_base_signal.getminutedata()
            coin_base_df['sma_5'] = ta.trend.sma_indicator(coin_base_df.Close, window=5) #MA(5) for long position
            coin_base_df['sma_8'] = ta.trend.sma_indicator(coin_base_df.Close, window=8) #MA(8) for long position
            coin_base_df['sma_13'] = ta.trend.sma_indicator(coin_base_df.Close, window=13) #MA(13) for long position

            coin_base_df.dropna(inplace = True)
            
            #cond1 -> coin_base_df['sma_5'] > coin_base_df['sma_8'] > coin_base_df['sma_13']
            cond1 = (coin_base_df['sma_5'][-1] > coin_base_df['sma_8'][-1]) & (coin_base_df['sma_5'][-1] > coin_base_df['sma_13'][-1]) & (coin_base_df['sma_8'][-1] > coin_base_df['sma_13'][-1])
            
            #cond2 -> coin_base_df['sma_5'] < coin_base_df['sma_8'] < coin_base_df['sma_13']
            
            cond2 = (coin_base_df['sma_5'][-1] < coin_base_df['sma_8'][-1]) & (coin_base_df['sma_5'][-1] < coin_base_df['sma_13'][-1]) & (coin_base_df['sma_8'][-1] < coin_base_df['sma_13'][-1])

            #**************************************************************
            
            position = 0 #Short, Long, Stable Position 
             
            if cond1 == 1: #Long Position
                position = 1
                list_top_coin += [coin_base]
            
            elif cond2 == 1: #Short Position
                position = -1
                j+=1
            else:           #Stable Position
                position = 0
                
        return list_top_coin

if __name__ == "__main__": 

    api_key = "api_key" # you can write your own binance api_key
    secret_key = "secret_key" # you can write your own binance secret_key

    client = Client(api_key = api_key, api_secret = secret_key)

    interval = '1m'
    lookback = '25'
    lags = 25
    
    try:
        top_coins=all_coins(client=client).best_coins()
        print(top_coins)
    except:
        print("Please Try Again!")
