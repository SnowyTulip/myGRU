import numpy as np
import torch
from torch import nn
from tqdm import tqdm 
import matplotlib.pyplot as plt
import pandas as pd
from data_phm import DataSet
from torch.autograd import Variable
import torch.utils.data as Data
from collections import OrderedDict
import time
import matplotlib.pyplot as plt



# import torch_directml
# from config import args
import os
# Define GRU Neural Networks
class GRU(nn.Module):
    """
        Parameters:
        - input_size: feature size
        - hidden_size: number of hidden units
        - output_size: number of output
        - num_layers: layers of LSTM to stack
    """

    def __init__(self, input_size, num_layers=1,seq_len = 2560):
        super().__init__()
        self.hidden_size = 256
        self.seq_len = seq_len
        self.feature_size = input_size
        bidirectional  = False # 是否是双向网络
        self.com = 10         # seq 放缩倍数
        if bidirectional:
            self.dim_n = 2
        else:
            self.dim_n = 1
        self.compress_seq = nn.Sequential(
            nn.Linear(self.seq_len * self.feature_size, int(self.seq_len / self.com)),
            nn.ReLU(),
            nn.Linear( int(self.seq_len / self.com) , int(self.seq_len / self.com) * self.feature_size),
        )
        self.net = nn.GRU(input_size, self.hidden_size, batch_first=True,num_layers = num_layers ,bidirectional = bidirectional,dropout = 0.3)  # utilize the GRU model in torch.nn
        self.FC = nn.Sequential(
            nn.Linear(self.hidden_size * self.dim_n,256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256,1),
            nn.ReLU(),                        #此处的问题，为什么添加了ReLU或者其他的激活函数作为输出后，预测的结果之间全是0(tanh为负数)
            #nn.Sigmoid()
        ) 
    def forward(self,x):
        x = x.to(torch.float32)                                           # x: [batch,seq , 2 ] 
        x = x.reshape(-1, self.seq_len * self.feature_size)               # x: [batch,2 * seq ]
        x_com = self.compress_seq(x)                                      # x: [batch,seq/10*2]
        x_com = x_com.reshape(-1,int(self.seq_len / self.com),self.feature_size)# x: [batch,seq/10,2]
        x, h = self.net(x_com)                                            # x: [batch,seq/10,hid]
        h = h.reshape(-1,self.hidden_size*self.dim_n)                     # h: [1*self.dim , batch, hid]
        h = torch.squeeze(h)                                              # h: [batch,hid]
        out = self.FC(h)
        out = torch.squeeze(out)                                          #out:[batch,1]
        return out
    
class Model():
    def __init__(self,device = torch.device("cpu")):
        self.epochs       = 200
        self.batch_size   = 128
        self.batches      = 30
        self.lr           = 0.1
        self.feature_size = 2
        self.device = device
        self.network      = GRU(self.feature_size).to(device)
        # self.optimizer    =  torch.optim.Adam(self.network.parameters(),lr=self.lr,weight_decay=1e-4)
        self.optimizer    =  torch.optim.SGD(self.network.parameters(),lr=self.lr,weight_decay=1e-4,momentum=0.78)
        # self.loss         = nn.CrossEntropyLoss()
        self.loss         = nn.MSELoss()
        self.save_log_path = "./log"
        # self.loss         = nn.KLDivLoss(reduction='batchmean') # KL 散度可用于衡量不同的连续分布之间的距离, 在连续的输出分布的空间上(离散采样)上进行直接回归时
        # lambda1 = lambda epoch: 1 / (epoch + 1) #调整学习率
        # self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda=[lambda1])

        self.initLogF()

    def initLogF(self):
        if  not os.path.exists(self.save_log_path):
            os.mkdir(self.save_log_path)
        f1,f2 =  open(os.path.join(self.save_log_path,"train.log"),'w'), open(os.path.join(self.save_log_path,"sample.log"),'w') 
        f1.close()
        f2.close()


    def get_bear_data(self, dataset, select):
        if select == 'train':
            # _select = ['Bearing1_1','Bearing1_2','Bearing2_1','Bearing2_2','Bearing3_1','Bearing3_2']
            # _select =['Bearing1_3','Bearing1_1']
            _select =['Bearing1_1']
        elif select == 'test':
            _select = ['Bearing1_3','Bearing1_4','Bearing1_5','Bearing1_6','Bearing1_7',
                        'Bearing2_3','Bearing2_4','Bearing2_5','Bearing2_6','Bearing2_7',
                        'Bearing3_3']
            # _select = ['Bearing1_2','Bearing2_2','Bearing3_2']
        else:
            raise ValueError('wrong select!')
        data,rul = dataset.get_data(_select,is_percent = True)
        # data :[测试总次数n,acc,2]
        # RUL  :[测试总次数n:RUL]
        data,rul = np.array(data),np.array(rul)
        data,rul = torch.tensor(data),torch.tensor(rul).float()
        data_set = Data.TensorDataset(data,rul)
        output   =   Data.DataLoader(data_set,self.batch_size,shuffle = True)
        return output

    def train(self):
        dataset = DataSet.load_dataset("phm_data")
        train_iter = self.get_bear_data(dataset,'train')
        # train_iter = self.get_bear_data(dataset,'test')
        test_iter =  self.get_bear_data(dataset,'test')
    
        log = OrderedDict()
        log['train_err'] = []
        log['test_err'] = []
        log['train_loss'] = []
        log['test_loss'] = []
        sample = open(os.path.join(self.save_log_path,"sample.log"),"w",encoding="utf-8") 
        # tx,ty = 1,1
        # for x,y in test_iter:
        #     tx,ty = x,y
        with tqdm(total=self.epochs * len(train_iter),colour= "red") as pbar:
            for epoch in range(1,self.epochs+1):
                #训练的过程记录数据
                train_l_sum, train_err_sum,test_err_sum,n, start = 0.0, 0.0,0, 0, time.time()
                batch_count = 0
                test_loss = 0
                test_err = 0
                #这里的无论是loss还是Err 都是一个batch数据的和
                for x,y in train_iter:
                    # x,y = tx,ty
                    self.network.train()
                    x = x.to(device)
                    y = y.to(device)
                    # x: [128, 2560, 2] :[batch,seq,feature]
                    # y: [128]          :[batch:rul]
                    y_hat = self.network(x).to(device)
                    # y_hat:[128]
                    loss_ = self.loss(y_hat,y)
                    self.optimizer.zero_grad()
                    loss_.backward()
                    self.optimizer.step()
                    # 统计部分$$$$$$$$$$
                    y_hat = y_hat.detach().cpu().numpy()
                    loss_ = loss_.detach().cpu().numpy()
                    y     = y.detach().cpu().numpy()
                    train_l_sum += loss_
                    self.sample_write(sample,y_hat,y)
                    train_err = sum([abs(y_hat[index] - y[index]) / (y[index]) for index in range(len(y_hat)) if y[index] != 0])/len(y_hat)
                    train_err_sum += train_err
                    n += y.shape[0]
                    batch_count += 1
                    pbar.set_description("epoch:{},err:{:.2f},loss:{:.4f}".format(epoch,train_err,loss_))
                    pbar.update(1)
                    #end
                # self.scheduler.step() # 调整学习率
                # test_err,test_loss = self.evaluate_accuracy(test_iter)#测试太慢了，暂时不进行测试
                #仍然是统计部分
                epoch_info = f'epoch{epoch + 1}, train err:{train_err_sum/batch_count :.2f}, test err:{test_err:.2f},train_loss:{train_l_sum / batch_count:.2f},test_loss:{test_loss:.2f}\n'
                print(epoch_info)
                log['train_err'].append(train_err_sum/batch_count)
                log['test_err'].append(test_err)
                log['train_loss'].append(train_l_sum/batch_count)
                log['test_loss'].append(test_loss)
                f = open(os.path.join(self.save_log_path,"train.log"), 'a',encoding="utf-8")
                f.write(epoch_info + "\n")
                f.close()

            #训练结束后保存图像
            self.paint(log)
            torch.save(self.network.cpu(), 'model/GRU_net.pkl')
            model = torch.load('model/GRU_net.pkl') 

    def evaluate_accuracy(self,data_iter):
        test_err_sum = 0
        test_loss_sum = 0
        net = self.network
        batch_count = 0
        with torch.no_grad():
            for x, y in data_iter:
                x = x.to(self.device)
                y = y.to(self.device)

                net.eval()  # 评估模式, 这会关闭dropout
                y_hat = net(x).to(device)
                loss = self.loss(y_hat,y)
                net.train()  # 改回训练模式

                test_loss_sum += loss.cpu().item()
                y_hat = y_hat.detach().cpu().numpy()
                y     = y.detach().cpu().numpy()
                test_err = sum([abs(y_hat[index] - y[index]) / (y[index]) for index in range(len(y_hat)) if y[index] != 0])/len(y_hat)
                test_err_sum += test_err
                batch_count += 1
        return test_err_sum/batch_count, test_loss_sum/batch_count
    
    def paint(self,log:OrderedDict):
        fig1 = plt.figure(1)
        fig2 = plt.figure(2)
        ax1 = fig1.subplots() 
        ax2 = fig2.subplots()
        ax1.plot(log['train_err'], label="train_err")
        ax1.plot(log['test_err'],label = "test_err")
        ax2.plot(log['train_loss'], label="train_loss")
        ax2.plot(log['test_loss'],label = "test_loss")
        ax1.set_title("err")
        ax2.set_title("loss")
        ax1.legend()
        ax2.legend()
        # plt.show()
        fig1.savefig(os.path.join(self.save_log_path,"fig1.png"))
        fig2.savefig(os.path.join(self.save_log_path,"fig2.png"))

    
    def sample_write(self,sample,y_hat,y,size = None):
        '''向sample写入日志'''
        size = size  if size and size < self.batch_size  else len(y_hat)
        for i in range(size):
            sample.write("{:.4f} ".format(y[i]))
        sample.write("\n")
        for i in range(size):
            sample.write("{:.4f} ".format(y_hat[i]))
        sample.write("\n\n")
        sample.flush()



if __name__ == '__main__':
    # torch.backends.cudnn.enabled=False
    # device = torch_directml.device()
    device = torch.device("cuda")
    print("use device:{}".format(device))
    process = Model(device= device)
    process.train()
