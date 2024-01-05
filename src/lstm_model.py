import numpy as np
import pandas as pd
import random
import os
import sklearn.preprocessing

# count number of processed files to parse
datasets = []
idx = 1
while os.path.exists(f'data/processed{idx}.csv'): 
    datasets.append(pd.read_csv(f'data/processed{idx}.csv', index_col = 'T', parse_dates=True))
    idx += 1
random.shuffle(datasets)

# join on datasets to apply scaling operations
merged_df = pd.concat(datasets)

# apply scaling
ss = sklearn.preprocessing.StandardScaler()
np_df = ss.fit_transform(merged_df)
merged_df.iloc[:,:] = np_df

# revert back to original datasets
for idx, df in enumerate(datasets):
    df.update(merged_df)
    datasets[idx] = df

# split data into input and output (ordered)
input_datasets = []
output_datasets = []

for df in datasets:
    input_datasets.append(df.iloc[:,:30]) # first 30 cols
    output_datasets.append(df.iloc[:,30:]) # after first 30 cols
    
# take 80-20 train-test split with priority to test

input_train_datasets = []
input_test_datasets = []
output_train_datasets = []
output_test_datasets = []

for di, do in zip(input_datasets, output_datasets):
    if (len(input_test_datasets))/len(input_datasets) < 0.2: 
        input_test_datasets.append(di)
        output_test_datasets.append(do)
    else: 
        output_train_datasets.append(di)
        output_train_datasets.append(do)