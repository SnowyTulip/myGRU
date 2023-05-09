import pymysql
host = 'localhost'
user = 'pi'
password = 'admin'
database_name = 'bear_db'



db = pymysql.connect(
        host=host,
        user=user,password=password,
        database= database_name,
        charset="utf8")
        
    
def CreateRecordTable(db,TableName = 'Records'):
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL，如果表存在则删除
    cursor.execute(f"DROP TABLE IF EXISTS {TableName}")
    # 使用预处理语句创建表
    sql = f"""CREATE TABLE {TableName} (
            Device_ID  char(20) PRIMARY KEY,
            province  char(20),
            factory char(20),  
            RUL int,
            risk char(10),
            Date DATETIME)"""
    
    cursor.execute(sql)

def InsertRecord(db,Record:dict):
    '''先查询是否已经存在该条设备ID
        如果存在该设备那么进行更新操作
        否则应该进行插入操作
    '''
    cursor = db.cursor()
    sql_insert = f"""replace into Records(Device_ID,
            province, factory, RUL,risk,Date)
            values ('{Record["Device_ID"]}', 
                '{Record["province"]}', 
                '{Record["factory"]}',
                '{Record["RUL"]}', 
                '{Record["risk"]}',
                    NOW()        )"""
    res = True
    try:
        cursor.execute(sql_insert)
        db.commit()
    except:
        db.rollback()
        res = False
    return res 

def CreateFactoryTable(db,TableName = 'Factory'):
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL，如果表存在则删除
    cursor.execute(f"DROP TABLE IF EXISTS {TableName}")
    # 使用预处理语句创建表
    sql = f"""CREATE TABLE {TableName} (
            factory_ID  char(20) PRIMARY KEY,
            province  char(20),
            factory char(20),  
            alarm_cnt  int,
            risk char(10))"""
    
    cursor.execute(sql)

def CreateModelTable(db,TableName = 'Model'):
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL，如果表存在则删除
    cursor.execute(f"DROP TABLE IF EXISTS {TableName}")
    # 使用预处理语句创建表
    sql = f"""CREATE TABLE {TableName} (
            model_ID  char(20) PRIMARY KEY,
            model_name  char(20),
            model_arch char(20),  
            Dir char(20),
            Date DATETIME)"""
    
    cursor.execute(sql)

def CreateDataSetsTable(db,TableName = 'DataSets'):
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL，如果表存在则删除
    cursor.execute(f"DROP TABLE IF EXISTS {TableName}")
    # 使用预处理语句创建表
    sql = f"""CREATE TABLE {TableName} (
            DataSets_ID  char(20) PRIMARY KEY,
            DataSets_name  char(20),
            pretreat char(20),  
            Dir int,
            Date DATETIME)"""
    
    cursor.execute(sql)


if __name__ == "__main__":
    # CreateModelTable(db)
    # CreateFactoryTable(db)
    # CreateDataSetsTable(db)
    ...
