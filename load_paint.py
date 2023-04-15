import numpy as np
import torch
import matplotlib.pyplot as plt
from utilis.data_phm import DataSet
import os

def get_bear_data(dataset, select,step = 50):
    select_name = ['Bearing1_1','Bearing1_2','Bearing2_1','Bearing2_2','Bearing3_1','Bearing3_2',
               'Bearing1_3','Bearing1_4','Bearing1_5','Bearing1_6','Bearing1_7',
                'Bearing2_3','Bearing2_4','Bearing2_5','Bearing2_6','Bearing2_7',
                'Bearing3_3']
    data,rul = dataset.get_data(select,is_percent = True)
    data,rul = np.array(data),np.array(rul)
    data = data[::step]
    rul  = rul [::step]
    return data,rul

def paint(model,dataset,bear_name = "Bearing2_5"):
    data,rul = get_bear_data(dataset,bear_name)
    model.eval()
    y_hat,_  = model(torch.tensor(data))
    y_hat = y_hat.detach().numpy()
    fig1 = plt.figure(1)
    ax1 = fig1.subplots() 
    ax1.plot(rul, label="Real RUL")
    ax1.plot(y_hat,label ="Pre RUL")
    ax1.set_title("RUL")
    ax1.legend()
    ax1.grid()
    fig1.savefig(os.path.join("rul_predict","rul.png"))

if __name__ == "__main__":
    data_set_name = 'phm_data_Z5'
    model = torch.load('model/LSTM_with_table_5.pkl') 
    dataset = DataSet.load_dataset(data_set_name)
    
    paint(model,dataset)