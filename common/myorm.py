import pymysql
from pymysql.cursors import DictCursor


class MySQL:
    def __init__(self):
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456',
                               charset='utf8', database='woniunote', autocommit=True)
        self.cursor = conn.cursor(DictCursor)

    # 封装基础查询语句
    def query(self, sql):
        ret = self.cursor.execute(sql)
        print(ret)
        res = self.cursor.fetchall()
        return res

    # 执行修改操作
    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            return 'OK'
        except:
            return 'Fail'


class User:
    table_name = 'user'  # 定义表名

    # 构造方法，传递字典参数作为Insert的key与value
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            print(self.__dict__)
        return

    # 封装查询操作
    def select1(self, condition):
        sql = "select * from %s where %s" % (self.table_name, condition)
        print(sql)
        res = MySQL().query(sql)
        return res

    def select2(self, **condition):
        sql = "select * from %s" % self.table_name
        if condition is not None:
            sql += " where"
            for k, v in condition.items():
                sql += " %s='%s' and" % (k, v)
            sql += ' 1=1'
        print(sql)
        res = MySQL().query(sql)
        return res

    # 封装新增
    def insert(self):
        keys = []
        values = []
        for k, v in self.__dict__.items():
            keys.append(k)
            values.append(str(v))
        print("-------------------")
        print("keys: ", keys)
        print("-------------------")
        print("values:", values)
        print("','".join(keys))
        sql = "insert into %s(%s) values ('%s')" % (self.table_name, ','.join(keys), "','".join(values))
        res = MySQL().execute(sql)
        print(res)
        print("insert sql: ", sql)


if __name__ == '__main__':
    # db = MySQL()
    # res = db.query('select * from user')
    # print(res)

    user = User()
    # # res = user.select1("userid=2 and password='123321'")
    # res = user.select2(userid=2, password='123321')
    # print(res)

    # user = User(username='note@163.com',password='hjwj8382xiia', nickname='小子', avatar='1.png', qq='36718371',
    #             role='user', createtime='2021-02-09 17:21:52', updatetime='2021-02-09 17:21:52')
    # user.insert()

    res = user.select2(username='note@163.com')
    print(res)
