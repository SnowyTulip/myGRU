from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
import pymysql
import stylesheet
import sys
import databaseFunc
class RecordBox(QWidget):
    def __init__(self):
        super().__init__()
        self.record = {"Device_ID":"","province":"","factory":"",
                        "RUL":"","risk":""}
        
        self.db = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("上传日志到数据库")
        Lay_v = QVBoxLayout()
        qfl = QFormLayout()
        
        self.Device_ID = QLineEdit()
        self.province = QLineEdit()
        self.factory = QLineEdit()
        self.RUL = QLineEdit()
        self.Device_ID.setStyleSheet(stylesheet.QlineEdit)
        self.province.setStyleSheet(stylesheet.QlineEdit)
        self.factory.setStyleSheet(stylesheet.QlineEdit)
        self.RUL.setStyleSheet(stylesheet.QlineEdit)
        self.label1 = QLabel("Device ID:")
        self.label2 = QLabel("province :")
        self.label3 = QLabel("factory  :")
        self.label4 = QLabel("RUL      :")

        self.RUL.setValidator(QIntValidator())
        self.label1.setStyleSheet(stylesheet.Font)
        self.label2.setStyleSheet(stylesheet.Font)
        self.label3.setStyleSheet(stylesheet.Font)
        self.label4.setStyleSheet(stylesheet.Font)
        qfl.addRow(self.label1, self.Device_ID)
        qfl.addRow(self.label2, self.province)
        qfl.addRow(self.label3, self.factory)
        qfl.addRow(self.label4, self.RUL)
        
        

        Lay_h = QHBoxLayout()
        self.yes = QPushButton("yes")
        self.yes.setStyleSheet(stylesheet.otherBtns)
        self.cancel = QPushButton("cancel")
        self.cancel.setStyleSheet(stylesheet.otherBtns)
        self.yes.clicked.connect(self.yes_func)
        self.cancel.clicked.connect(self.cancel_func)
        Lay_h.addWidget(self.yes)
        Lay_h.addWidget(self.cancel)

        Lay_v.addLayout(qfl)
        Lay_v.addLayout(Lay_h)

        self.setLayout(Lay_v)

    def cancel_func(self):
        self.close()
    
    def yes_func(self):
        self.getRecord()
        self.update_record()
        self.close()

    def update_record(self):
        if self.db == None:
            dig = QMessageBox.critical(self,"错误", "数据库还未连接",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        else:
            ...
            #做一些上传数据库的操作
            databaseFunc.InsertRecord(self.db,self.record)
            dig = QMessageBox.information(self,"", "日志上传成功",QMessageBox.Yes,QMessageBox.Yes)
            print((self.record))

    def getRecord(self):
        self.record["Device_ID"] = self.Device_ID.text()
        self.record["province"]  = self.province.text()
        self.record["factory"]   = self.factory.text()
        self.record["RUL"]       = self.RUL.text()
        # 风险等级根据RUL来判定0-5 高危 ;5-50良好; 50+ 安全
        self.risks = ["danger","good","safe"]
        RUL  = int(self.RUL.text())
        index = 2 if RUL > 50 else \
                                0 if RUL < 5 else 1  
        self.record["risk"] = self.risks[index]
        return self.record


class db_dig(QWidget):
    def __init__(self):
        super().__init__()
        self.db = None
        self.db_status = False
        self.host = "localhost"
        self.user = "pi"
        self.password = "admin"
        self.database_name = "bear_db"
        self.province = "AnHui"
        self.factory  =  "HFUT"
        self.rbox = RecordBox()
        self.initUI()

    def initUI(self):
        #创建一个表单布局
        qfl = QFormLayout()
        #设置标签右对齐，不设置是默认左对齐
        # qfl.setLabelAlignment(Qt.AlignRight)
        
        self.host_edit = QLineEdit()
        self.user_edit = QLineEdit()
        self.psw_edit = QLineEdit()
        self.dbname_edit = QLineEdit()
        self.host_edit.setStyleSheet(stylesheet.QlineEdit)
        self.user_edit.setStyleSheet(stylesheet.QlineEdit)
        self.psw_edit.setStyleSheet(stylesheet.QlineEdit)
        self.dbname_edit.setStyleSheet(stylesheet.QlineEdit)

        self.host_edit.setText(self.host)
        self.user_edit.setText(self.user)
        self.psw_edit.setText(self.password)
        self.dbname_edit.setText(self.database_name)
        
        #把文本框添加到布局，第一个参数为左侧的说明标签
        self.label1 = QLabel("host  address:")
        self.label2 = QLabel("user     name:")
        self.label3 = QLabel("Password     :")
        self.label4 = QLabel("database name:")

        self.label1.setStyleSheet(stylesheet.Font)
        self.label2.setStyleSheet(stylesheet.Font)
        self.label3.setStyleSheet(stylesheet.Font)
        self.label4.setStyleSheet(stylesheet.Font)
        qfl.addRow(self.label1, self.host_edit)
        qfl.addRow(self.label2, self.user_edit)
        qfl.addRow(self.label3, self.psw_edit)
        qfl.addRow(self.label4, self.dbname_edit)

        self.connect_btn = QPushButton(QIcon("myGRU/IconsBase/in.png"),"")
        self.label5 = QLabel("confirm settings")
        self.label5.setStyleSheet(stylesheet.Font)
        self.connect_btn.clicked.connect(self.btn_confirm)
        self.connect_btn.setStyleSheet(stylesheet.otherBtns)
        
        qfl.addRow(self.label5,self.connect_btn)


        self.splitbox = QLineEdit()
        self.splitbox.setStyleSheet(stylesheet.Font_back)
        self.splitbox.setText("No Connection!")
        self.splitbox.setEnabled(False)
        self.InFo = QLabel("Currently database")
        self.InFo.setStyleSheet(stylesheet.Font)
        qfl.addRow("",QWidget())
        qfl.addRow(self.InFo,self.splitbox)
        qfl.addRow("",QWidget())

        self.label6 = QLabel("province     :")
        self.label7 = QLabel("factory      :")
        self.label6.setStyleSheet(stylesheet.Font)
        self.label7.setStyleSheet(stylesheet.Font)
        self.province_edit = QLineEdit()
        self.factory_edit = QLineEdit()
        self.province_edit.setText(self.province)
        self.factory_edit.setText(self.factory)
        self.province_edit.setStyleSheet(stylesheet.QlineEdit)
        self.factory_edit.setStyleSheet(stylesheet.QlineEdit)

        # self.factory_edit.setDisabled(True)
        # self.province_edit.setDisabled(True)
        qfl.addRow(self.label6,self.province_edit)
        qfl.addRow(self.label7,self.factory_edit)
        

        
        #设置提示输入文本
        self.host_edit.setPlaceholderText("数据库主机名称或IP")
        self.user_edit.setPlaceholderText("登录数据库用户名")
        self.psw_edit.setPlaceholderText("登录密码")
        self.dbname_edit.setPlaceholderText("数据库名称")
        
        #设置显示效果
        self.host_edit.setEchoMode(QLineEdit.Normal)
        self.user_edit.setEchoMode(QLineEdit.Normal)
        self.psw_edit.setEchoMode(QLineEdit.Password)
        self.dbname_edit.setEchoMode(QLineEdit.Normal)


        #把设置的布局加载到窗口
        self.setLayout(qfl)
        
        
    def update_record(self):
        '''上传日志'''
        self.rbox.show()
        self.rbox.db = self.db

    def btn_confirm(self):
        self.host = self.host_edit.text()
        self.user = self.user_edit.text()
        self.password = self.psw_edit.text()
        self.database_name = self.dbname_edit.text()
        dig = QMessageBox.information(self,"", f"参数已更新:{self.database_name}",QMessageBox.Yes,QMessageBox.Yes)

    def connect_db(self):
        try:
            self.db = pymysql.connect(
                host=self.host,
                user=self.user,password=self.password,
                database=self.database_name,
                charset="utf8")
        except:
            print("failed connected to database!")
            dig = QMessageBox.critical(self,"错误", "参数错误，无法连接数据库",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        else:
            print("连接数据库成功")
            dig = QMessageBox.information(self,"成功", f"连接数据库:{self.database_name}",QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
            self.splitbox.setText(f"Connected to {self.database_name}")

    def disconnect(self):
        try:
            self.db.close()
        except:
            pass
        dig = QMessageBox.information(self,"", f"断开数据库:{self.database_name}",QMessageBox.Yes,QMessageBox.Yes)
        self.db = None
        self.splitbox.setText("No Connection!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = db_dig()
    win.show()
    sys.exit(app.exec_())