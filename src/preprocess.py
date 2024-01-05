import pandas as pd
import numpy as np
from plot import hand_plot
import os

class data_format():    
    # apply all techniques to get concatated table
    def process(self, df1, df2, interval, roll_over1, roll_over2):
        df1 = self.format_data(df1)
        df2 = self.format_data(df2)
        
        df1 = self.rolling_sum(df1, roll_over1)
        df2 = self.rolling_sum(df2, roll_over2)
        
        df1 = self.extrapolate_interval(df1, interval)
        df2 = self.extrapolate_interval(df2, interval)
        
        df = self.join(df1, df2)
        return df
        
    # applies extrapolation and inner join to tables
    def format_data(self, df):
        # convert T row to date and time
        df['T'] = pd.to_datetime(df['T'], unit='s')
        df['T'] = df['T'].dt.round('10ms') 
        df = df.set_index('T')
        return df
    
    # apply rolling sum average to the output data
    def rolling_sum(self, df, roll_over):
        for column in df: df[column] = df[column].rolling(roll_over).sum()/roll_over
        return df
    
    # function to extrapolate to interval and remove rest
    def extrapolate_interval(self, df, interval):
        # interpolate to interval
        df = df.resample("10ms").interpolate('time') # first interpolate to finer granularity
        df = df.resample(f"{interval}ms").interpolate('time')
        
        # drop None values (usually start and end ones)
        df = df.replace(to_replace='None', value=np.nan).dropna()
        return df
    
    # inner join and rounding
    def join(self, df1, df2):
        df = pd.merge(df1, df2, left_index=True, right_index=True)
        df = df.round(2)
        
        # check for file name and output
        idx = 1
        while os.path.exists(f'data/processed{idx}.csv'): idx += 1
        df.to_csv(f"data/processed{idx}.csv")
        return df
        
data_f = data_format()   
idx = 1        
while os.path.exists(f'data/reciever{idx}.csv'): 
    
    # data reading
    dr = pd.read_csv(f'data/reciever{idx}.csv')
    dc = pd.read_csv(f'data/camera{idx}.csv')    
    
    # do the processing and create files
    dp = data_f.process(dr, dc, 100, 1, 5)
    idx += 1
        
# uncomment below to display processed handplot for certain read
# dc = pd.read_csv(f'data/camera1.csv') 
# dc = data_f.format_data(dc)
# dc = data_f.rolling_sum(dc, 5)
# dc = data_f.extrapolate_interval(dc, 100)
# dc = dc.to_numpy()

# hp = hand_plot(dc, 100)
# hp.create_plot(dc)