import pandas as pd
import pymysql



class DBTool(object):


    def __init__(self):
        # 打开数据库连接
        db = pymysql.connect("localhost", "root", "123456", "orange")

        # 使用 cursor() 方法创建一个游标对象 cursor
        self.cursor = db.cursor()


    # def mycursor(db_name=None):
    #     '''连接数据库，创建游标'''
    #     config = dict(zip(['host', 'user', 'port', 'password'],
    #                       ['localhost', 'root', 3306, '123456']))
    #     config.update(database=db_name)
    #     connection = pymysql.connect(**config)
    #     cursor = connection.cursor()
    #     return cursor
    #
    #
    # def mycon(db_name=None):
    #     '''连接数据库，创建游标'''
    #     config = dict(zip(['host', 'user', 'port', 'password'],
    #                       ['localhost', 'root', 3306, '123456']))
    #     config.update(database=db_name)
    #     connection = pymysql.connect(**config)
    #     return connection
    #
    #
    # def use(db_name):
    #     '''切换数据库，返回游标'''
    #     return mycursor(db_name)
    #
    #
    # def insert_many(table, data):
    #     '''向全部字段插入数据'''
    #     val = '%s, ' * (len(data[0]) - 1) + '%s'
    #     sql = f'insert into {table} values ({val})'
    #     cursor.executemany(sql, data)
    #     cursor.connection.commit()


    def query(self,sql):
        '''以数据框形式返回查询据结果'''
        self.cursor.execute(sql)
        data = self.cursor.fetchall()  # 以元组形式返回查询数据
        header = [t[0] for t in self.cursor.description]
        df = pd.DataFrame(list(data), columns=header)  # pd.DataFrem 对列表具有更好的兼容性
        return df


    # def select_database():
    #     '''查看当前数据库'''
    #     sql = 'select database();'
    #     return query(sql)
    #
    #
    # def show_tables():
    #     '''查看当前数据库中所有的表'''
    #     sql = 'show tables;'
    #     return query(sql)
    #
    #
    # def select_all_from(table):
    #     sql = f'select * from {table};'
    #     return query(sql)