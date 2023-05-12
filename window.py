import sys
import os
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
import torch
from utilis.data_phm import DataSet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
import stylesheet
import database
from threading import Thread
class MainUI(QMainWindow):
    _paintOver = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self._paintOver.connect(self.paintOver)
        self.runpaint = True
        self.icon_dir = "myGRU/IconsBase/"
        self.image_dir = "myGRU/images/"
        self.data_set_name = 'phm_data_Z5'
        self.model_name    = 'LSTM_with_table_5.pkl'
        self.database = database.db_dig()
        self.initModelD()
        self.initPaint()
        self.initUI_Tool()
        self.initUI()
        #获取数据
        # self.get_bear_data()
        #进行一次预测
        self.runPredict()
        #绘制
        self.runPaint_Data_t()
        self.runPaint_RUL()

    def initModelD(self):
        self.model = torch.load('model/'+self.model_name) 
        self.dataset = DataSet.load_dataset(self.data_set_name)
        self.step = 15         # 数据的步长
        self.data       = np.array([]) # 数据
        self.fulldata   = np.array([])
        self.Real_RUL   = np.array([]) # 剩余寿命 np.array
        self.Pre_RUL    = np.array([]) # 预测寿命
        self.bear_name = 'Bearing1_1' # 当前预测的轴承名称
        self.bear_names = [ 'Bearing1_1','Bearing1_2','Bearing2_1','Bearing2_2','Bearing3_1','Bearing3_2',
                            'Bearing1_3','Bearing1_4','Bearing1_5','Bearing1_6','Bearing1_7',
                            'Bearing2_3','Bearing2_4','Bearing2_5','Bearing2_6','Bearing2_7',
                            'Bearing3_3']

    def initPaint(self):
        self.fig_data = plt.Figure()
        self.ax_data = self.fig_data.add_subplot(111)
        self.ax_data.grid()
        self.ax_data.set_title("Data")
        # self.ax_data.legend()
        self.ax_data.grid()

        self.fig_RUL  = plt.Figure()
        self.ax_RUL = self.fig_RUL.add_subplot(111)
        self.ax_RUL.grid()
        self.ax_RUL.set_title("RUL")
        # self.ax_RUL.legend()
        self.ax_RUL.grid()

        self.canvas_data = FC(self.fig_data)
        self.canvas_RUL  = FC(self.fig_RUL)


    def initUI(self):
        self.setGeometry(400,300,1500,850)
        self.setWindowTitle("基于稳定学习的轴承寿命预测系统")
        self.setWindowIcon(QIcon(self.icon_dir  + "fire.png"))
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        lay = QHBoxLayout()
        self.spliter = QSplitter(Qt.Horizontal,self)
        self.Container1 = QWidget()#QLabel("Container1")
        self.Container2 = QWidget()#QLabel("Container2")
        self.Container3 = QWidget()#QLabel("Container3")
        self.spliter.addWidget(self.Container1)
        self.spliter.addWidget(self.Container2)
        self.spliter.addWidget(self.Container3)
        # self.Icon = QLabel()
        # self.Icon.setFixedSize(45,45)
        # self.Icon.setScaledContents(True)
        #container1
        Lay1 = QVBoxLayout()
        self.Container1.setLayout(Lay1)

        self.Name_Lable = QLabel("基于稳定学习的\n轴承寿命\n预测系统")
        # self.Name_Lable.setPixmap(QPixmap(self.image_dir+ "Name.png"))
        self.Name_Lable.setScaledContents(True)
        self.Name_Lable.setStyleSheet(stylesheet.Name)
        self.database = database.db_dig()

        self.LOGO_Lable = QLabel()
        self.LOGO_Lable.setPixmap(QPixmap(self.image_dir+ "Gear.png"))
        # self.LOGO_Lable.setScaledContents(True)
        Lay1.addWidget(self.database)
        Lay1.addWidget(self.LOGO_Lable)
        
        #containner2 中间部分设计
        Lay2 = QVBoxLayout()
        self.Container2.setLayout(Lay2)
        # self.test1 = QLabel("按钮")
        # self.test2 = QLabel("选择数据集的下滑commbox")
        self.dataset_Label = QLabel("选择数据集")
        self.dataset_Label.setStyleSheet(stylesheet.Font_zh)
        # 数据集选择
        self.dataset_cob = QComboBox()
        self.dataset_cob.addItems(["phm_data_Z5"])
        self.dataset_cob.setStyleSheet(stylesheet.Font_cob)
        #添加槽函数
        #步长设置

        #轴承名称设置
        self.bear_name_Label = QLabel("轴承名称选择")
        self.bear_name_Label.setStyleSheet(stylesheet.Font_zh)
        self.bear_name_cob = QComboBox()
        self.bear_name_cob.addItems(self.bear_names)
        #这里添加槽函数，当cob变化的时候self.bear_name也要变化
        self.bear_name_cob.currentIndexChanged.connect(self.bear_name_change)
        self.bear_name_cob.setStyleSheet(stylesheet.Font_cob)

        #模型名称选择设置
        self.model_Label = QLabel("模型选择")
        self.model_Label.setStyleSheet(stylesheet.Font_zh)
        self.model_cob = QComboBox()
        self.model_cob.addItems(["LSTM_with_table_5.pkl","LSTM_with_table_10.pkl"])
        #这里是需要绑定槽函数的，但是要考虑绑定之后，会不会引起卡顿，因此要选择
        self.model_cob.currentIndexChanged.connect(self.model_change)
        self.model_cob.setStyleSheet(stylesheet.Font_cob)
        #数据归一化
        self.Normlize_Lable = QLabel("数据归一化")
        self.Normlize_Lable.setStyleSheet(stylesheet.Font_zh)
        self.Normlize_cob = QComboBox()
        self.Normlize_cob.addItems(["Z-Scores","Min-Max Methoh"])
        self.Normlize_cob.setStyleSheet(stylesheet.Font_cob)
        #绘图步长选择 默认为20
        self.step_Lable = QLabel("绘制步长")
        self.step_Lable.setStyleSheet(stylesheet.Font_zh)
        self.step_cob = QComboBox()
        self.step_cob.addItems([f"{i}" for i in range(1,40,2)] )
        self.step_cob.setStyleSheet(stylesheet.Font_cob)
        self.step_cob.currentIndexChanged.connect(self.step_change)
        #日志文本框
        self.Log_Text = QTextEdit()
        self.Log_Text.setCurrentFont(QFont('Monaco'))
        self.Log_Text.setText(f"模型名:{self.model_name}\n数据集:{self.data_set_name}")
        self.Log_Text.setReadOnly(True)

        Lay2.addWidget(self.dataset_Label)
        Lay2.addWidget(self.dataset_cob)

        Lay2.addWidget(self.bear_name_Label)
        Lay2.addWidget(self.bear_name_cob)

        Lay2.addWidget(self.model_Label)
        Lay2.addWidget(self.model_cob)

        Lay2.addWidget(self.Normlize_Lable)
        Lay2.addWidget(self.Normlize_cob)

        Lay2.addWidget(self.step_Lable)
        Lay2.addWidget(self.step_cob)
        
        Lay2.addWidget(self.Log_Text)
        

        #containner3 绘图部分设计
        Lay3 = QVBoxLayout()
        self.Container3.setLayout(Lay3)
                                            #matplotlib + pyqt
        # self.Name_Lable = QLabel("绘图-轴承振动数据-z")
        # self.LOGO_Lable = QLabel("绘图-预测结果数据-mat")
        Lay3.addWidget(self.canvas_data)
        Lay3.addWidget(self.canvas_RUL)

        lay.addWidget(self.spliter)
        self.main_widget.setLayout(lay)
    

    def initUI_Tool(self):
        #获取菜单栏
        bar = self.menuBar()
        file = bar.addMenu("文件(&F)")
        save = file.addAction("保存")
        save.setShortcut("Ctrl+S")
        setup = bar.addMenu("设置(&S)")
        helps = bar.addMenu("帮助(&H)")
        open = file.addAction("打开")
        open.setShortcut("Ctrl+O")
        view = bar.addMenu("查看(&V)")
        color = QMenu("颜色",view)
        view.addMenu(color)
        font = QAction("字体",view)
        font.setShortcut("Ctrl+F")
        view.addAction(font)
        #获取工具栏
        toolbar = self.addToolBar("Run")
        run = QAction(QIcon(self.icon_dir + "dispaly.png"),"启动预测",self)################
        toolbar.addAction(run)
        run.triggered.connect(self.runModel)
        refresh = QAction(QIcon(self.icon_dir + "flush.png"),"重新绘制",self)###############
        toolbar.addAction(refresh)
        refresh.triggered.connect(self.runPaint_Data_step_t)
        setup  = QAction(QIcon(self.icon_dir + "setup1.png"),"设置模型",self)
        toolbar.addAction(setup)
        #连接数据库
        database = QAction(QIcon(self.icon_dir + "database.png"),"连接数据库",self)
        toolbar.addAction(database)
        database.triggered.connect(self.connect_database)

        output = QAction(QIcon(self.icon_dir + "output.png"),"上传日志",self)
        toolbar.addAction(output)
        output.triggered.connect(self.update_Record) # 上传日志需要多个类进行配合
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        datasets = QAction(QIcon(self.icon_dir + "download.png"),"获取数据集",self)
        toolbar.addAction(datasets)
        datasets.triggered.connect(self.download)

        disconnect = QAction(QIcon(self.icon_dir + "no.png"),"断开连接",self)
        toolbar.addAction(disconnect)
        disconnect.triggered.connect(self.disconnect_db)

    def update_Record(self):
        self.database.update_record()
    
    def step_change(self):
        self.step = int(self.step_cob.currentText())
    
    def disconnect_db(self):
        self.database.disconnect()

    def download(self):
        '''下载数据库中的数据文件'''
        dig = QMessageBox.information(self,"数据集", f"下载数据集:{self.data_set_name}",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
            
    def connect_database(self):
        ''''''
        self.database.connect_db()
        print("database")

    def bear_name_change(self):
        self.bear_name = self.bear_names[self.bear_name_cob.currentIndex()]
        self.get_bear_data()
        self.runPaint_Data_t()
    
    def model_change(self):
        self.model_name = self.model_cob.currentText()
        self.model = torch.load('model/'+self.model_name) 

    def get_bear_data(self):
        '''获得轴承数据
        可以选择的参数为:step(绘制步长)

        '''
        self.bear_names = ['Bearing1_1','Bearing1_2','Bearing2_1','Bearing2_2','Bearing3_1','Bearing3_2',
                'Bearing1_3','Bearing1_4','Bearing1_5','Bearing1_6','Bearing1_7',
                'Bearing2_3','Bearing2_4','Bearing2_5','Bearing2_6','Bearing2_7',
                'Bearing3_3']
        data,rul = self.dataset.get_data(self.bear_name,is_percent = True)
        data,rul = np.array(data),np.array(rul)
        self.fulldata = data
        self.data = data[::self.step]
        self.Real_RUL  = rul [::self.step]
        # return data,rul

    def runPaint_Data_t(self):
        self.runpaint = False
        self.Log_Text.setTextColor(QColor("red"))
        self.Log_Text.setText(f"Painting {self.bear_name},please wait...")
        t1 = Thread(target=self.runPaint_Data)
        t1.setDaemon(True)
        t1.start()

    def runPaint_Data_step_t(self):
        if self.runpaint:
            self.Log_Text.setTextColor(QColor("red"))
            self.Log_Text.setText(f"Painting {self.bear_name},please wait...")
            t1 = Thread(target=self.runPaint_Data_step)
            t1.setDaemon(True)
            t1.start()
        

    def runPaint_Data(self):
        '''根据数据绘制振动数据图像,'''
        self.runpaint = False
        if self.data.shape[0] == 0:
            self.get_bear_data()
        self.ax_data.cla()
        self.ax_data.plot(self.fulldata)
        print(self.fulldata.shape)
        self.ax_data.set_title("Vibration Signal")
        # self.ax_data.legend()
        self.ax_data.grid()
        self.canvas_data.draw()
        self._paintOver.emit("")
    
    def runPaint_Data_step(self):
        self.get_bear_data()
        self.ax_data.cla()
        paintdata = self.data.flatten()
        self.ax_data.plot(paintdata)
        print(paintdata.shape)
        self.ax_data.set_title("Vibration Signal")
        # self.ax_data.legend()
        self.ax_data.grid()
        self.canvas_data.draw()
        self._paintOver.emit("")
    
    def paintOver(self):
        self.Log_Text.setTextColor(QColor("black"))
        self.Log_Text.setText(f"model:{self.model_name}\ndataset:{self.data_set_name}\n" + f"painted:{self.bear_name}!")
        self.runpaint = True
        

    def runPaint_RUL(self):
        '''根据数据绘制振动数据图像,'''
        if self.data.shape[0] == 0 or self.Real_RUL.shape[0] == 0:
            self.get_bear_data()
        if self.Pre_RUL.shape[0] == 0:
            self.runPredict()
        self.ax_RUL.cla()
        self.ax_RUL.plot(self.Real_RUL, label="Real_RUL")
        self.ax_RUL.plot(self.Pre_RUL , label="Pred_RUL")
        self.ax_RUL.set_title("RUL")
        self.ax_RUL.legend()
        self.ax_RUL.grid()
        self.canvas_RUL.draw()
    
    def runPredict(self):
        '''进行一次预测'''
        if self.data.shape[0] == 0:
            self.get_bear_data()
        self.model.eval()
        y_hat,_  = self.model(torch.tensor(self.data))
        y_hat = y_hat.detach().numpy()
        self.Pre_RUL = y_hat

    def runModel(self):
        ''''''
        self.get_bear_data()
        self.runPredict()
        self.runPaint_RUL()
        # self.runPaint_Data()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainUI()
    win.show()
    sys.exit(app.exec_())