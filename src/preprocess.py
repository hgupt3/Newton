import pandas as pd
import numpy as np

class data_process():
    def __init__(self):
        self.dr = pd.read_csv('data/data_reciever.csv')
        self.dc = pd.read_csv('data/data_camera.csv')
    
    def format_data(self, interval):
        self.dr = self.extrapolate_interval(self.dr, interval)
        self.dc = self.extrapolate_interval(self.dc, interval)
        
        self.dp = pd.merge(self.dr, self.dc, left_index=True, right_index=True)
        self.dp = self.dp.round(2)
        self.dp.to_csv("data/data_processed.csv")
        
    # function to extrapolate to interval and remove rest
    def extrapolate_interval(self, df, interval):
        # convert T row to date and time
        df['T'] = pd.to_datetime(df['T'], unit='s')
        df['T'] = df['T'].dt.round('10ms') 
        
        # interpolate to interval
        df = df.set_index('T')
        df = df.resample("10ms").interpolate('time') # first interpolate to finer granularity
        df = df.resample(f"{interval}ms").interpolate('time')
        
        # drop None values (usually start and end ones)
        df = df.replace(to_replace='None', value=np.nan).dropna()
        return df
        
dp = data_process()
dp.format_data(100) # 100ms interval

        
