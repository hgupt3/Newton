import numpy as np
import pandas as pd
import random
import os
import sklearn.preprocessing
import torch
import torch.nn as nn
from torch.autograd import Variable
from plot import hand_plot

# count number of processed files to parse
datasets = []
row_count = []
idx = 1
while os.path.exists(f'data/processed{idx}.csv'): 
    datasets.append(pd.read_csv(f'data/processed{idx}.csv', index_col = 'T', parse_dates=True))
    row_count.append(datasets[-1].shape[0])
    idx += 1

# randomize datasets
random.shuffle(datasets)

# join on datasets to apply scaling operations
merged_df = pd.concat(datasets)

test_data = pd.read_csv(f'data/testing.csv', index_col='T', parse_dates=True)

# apply scaling
ss_input = sklearn.preprocessing.StandardScaler()
ss_output = sklearn.preprocessing.StandardScaler()

np_df = ss_input.fit_transform(merged_df.iloc[:,:30])
merged_df.iloc[:,:30] = np_df
np_df = ss_output.fit_transform(merged_df.iloc[:,30:])
merged_df.iloc[:,30:] = np_df

test_data_transformed_input = ss_input.transform(test_data.iloc[:,:30])
test_data_transformed_output = ss_output.transform(test_data.iloc[:,30:])

# revert back to original datasets
for idx, df in enumerate(datasets):
    df.update(merged_df)
    datasets[idx] = df

# split data into input and output (ordered)
input_train_datasets = []
output_train_datasets = []

test_data_input_tensor = torch.Tensor(np.array([test_data_transformed_input]))
test_data_label_tensor = torch.Tensor(np.array([test_data_transformed_output]))

for df in datasets:
    input_train_datasets.append(torch.Tensor(df.iloc[:,:30].to_numpy())) # first 30 cols
    output_train_datasets.append(torch.Tensor(df.iloc[:,30:].to_numpy())) # after first 30 cols
      
# pack datasets with zeros        
input_train_tensors = nn.utils.rnn.pad_sequence(input_train_datasets, batch_first=True)
output_train_tensors = nn.utils.rnn.pad_sequence(output_train_datasets, batch_first=True)


class hand_lstm(nn.Module):
    def __init__(self):
        super(hand_lstm, self).__init__()
        self.input_dim = 30
        self.num_layers_lstm = 2
        self.hidden_size_lstm = 128
        self.drop_prob_lstm = 0.2
        self.hidden_size_linear = 84
        self.output_dim = 63
        
        # the hidden state and cell state is stored when the forward live model type is used
        self.h = Variable(torch.zeros(self.num_layers_lstm, 1, self.hidden_size_lstm)) # hidden state
        self.c = Variable(torch.zeros(self.num_layers_lstm, 1, self.hidden_size_lstm)) # cell state
        
        self.lstm = nn.LSTM(input_size=self.input_dim, 
                            hidden_size=self.hidden_size_lstm, 
                            num_layers=self.num_layers_lstm, 
                            dropout=self.drop_prob_lstm,
                            batch_first=True)
        self.linear = nn.Linear(in_features=self.hidden_size_lstm, 
                                out_features=self.hidden_size_linear)
        self.linear_out = nn.Linear(in_features=self.hidden_size_linear, 
                                    out_features=self.output_dim)
        
    # for training
    def forward(self, x):
        # initialize hidden & cell state
        h0 = Variable(torch.zeros(self.num_layers_lstm, x.size(0), self.hidden_size_lstm)) # hidden state
        c0 = Variable(torch.zeros(self.num_layers_lstm, x.size(0), self.hidden_size_lstm)) # cell state
        
        x, (hn, cn) = self.lstm(x, (h0, c0)) # final hidden state and cell state not used
        x = self.linear(x)
        out = self.linear_out(x)
        return out
    
    # for model use with live data where hidden state and live state is plugged in from previous state
    def forward_live(self, x):
        x, (self.h, self.c) = self.lstm(x, (self.h, self.c))
        x = self.linear(x)
        out = self.linear_out(x)
        return out
    
def train(model, num_epoch, learning_rate, hyperparameter_array):        
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # model training
    print("Model training:")
    for epoch in range(num_epoch):
        model.train()
        optimizer.zero_grad()
        output_pred_tensors = model(input_train_tensors)
        loss = criterion(output_pred_tensors, output_train_tensors)
        loss.backward()
        optimizer.step()
        loss_arr[0].append(round(loss.item(),5))
        
        # if not (epoch % (num_epoch//250)): # 100 progress steps
        model.eval()
        output_pred_tensors = model(test_data_input_tensor)
        loss = criterion(output_pred_tensors, test_data_label_tensor)
        print(f"epoch: {epoch}, loss: {round(loss.item(),5)}")
        loss_arr[1].append(round(loss.item(),5))
            
    return model 

def save(model):
    # save model weights
    torch.save(model.state_dict(), 'newton_model/weights.pth')
    print(("Saved weights at 'newton_model/weights.pth'"))
        
# loss_arr = [[],[]] # learning rate format will tell us what each row in the 2D matrix means
# model = hand_lstm()
# model = train(model, 500, 0.005, loss_arr)

# hp = pd.DataFrame(loss_arr, columns=list(range(1,501)))
# hp.to_csv('data/hyperparameter.csv')