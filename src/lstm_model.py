import numpy as np
import pandas as pd
import random
import os
import sklearn.preprocessing
import torch
import torch.nn as nn
from torch.autograd import Variable

# count number of processed files to parse
datasets = []
row_count = []
idx = 1
while os.path.exists(f'data/processed{idx}.csv'): 
    datasets.append(pd.read_csv(f'data/processed{idx}.csv', index_col = 'T', parse_dates=True))
    row_count.append(datasets[-1].shape[0])
    idx += 1
    
# make all datasets of same size
for dataset in datasets:
    extra_rows = dataset.shape[0]-min(row_count)
    if extra_rows: dataset.drop(dataset.tail(extra_rows).index, inplace = True)

# randomize datasets
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
        input_test_datasets.append(di.to_numpy())
        output_test_datasets.append(do.to_numpy())
    else: 
        input_train_datasets.append(di.to_numpy())
        output_train_datasets.append(do.to_numpy())
        
input_train_tensors = Variable(torch.Tensor(np.array(input_train_datasets)))
input_test_tensors = Variable(torch.Tensor(np.array(input_test_datasets)))
output_train_tensors = Variable(torch.Tensor(np.array(output_train_datasets)))
output_test_tensors = Variable(torch.Tensor(np.array(output_test_datasets)))

class hand_lstm(nn.Module):
    def __init__(self):
        super(hand_lstm, self).__init__()
        self.input_dim = 30
        self.num_layers_lstm = 2
        self.hidden_size_lstm = 128
        self.drop_prob_lstm = 0.2
        self.hidden_size_linear = 84
        self.output_dim = 63
        
        self.lstm = nn.LSTM(input_size=self.input_dim, 
                            hidden_size=self.hidden_size_lstm, 
                            num_layers=self.num_layers_lstm, 
                            dropout=self.drop_prob_lstm,
                            batch_first=True)
        self.linear = nn.Linear(in_features=self.hidden_size_lstm, 
                                out_features=self.hidden_size_linear)
        self.linear_out = nn.Linear(in_features=self.hidden_size_linear, 
                                out_features=self.output_dim)
        
    def forward(self, x):
        # initialize hidden & cell state
        h0 = Variable(torch.zeros(self.num_layers_lstm, x.size(0), self.hidden_size_lstm)) # hidden state
        c0 = Variable(torch.zeros(self.num_layers_lstm, x.size(0), self.hidden_size_lstm)) # cell state
        
        x, (hn, cn) = self.lstm(x, (h0, c0)) # final hidden state and cell state not used
        x = self.linear(x)
        out = self.linear_out(x)
        return out
        
model = hand_lstm()

# model evaluation parameters
learning_rate = 0.001
num_epoch = 2000
        
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# model training
for epoch in range(num_epoch+1):
    model.train()
    optimizer.zero_grad()
    output_pred = model(input_train_tensors)
    loss = criterion(output_pred, output_train_tensors)
    loss.backward()
    optimizer.step()
    
    if not (epoch % (num_epoch//10)): 
        model.eval()
        output_pred = model(input_train_tensors)
        loss = criterion(output_pred, output_train_tensors)
        print(f"epoch: {epoch}, loss: {round(loss.item(),5)}")