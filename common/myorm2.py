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


# 封装成标准的模型类，供子类继承
# 增加field()方法来指定查询哪些列，*代表所有列
class Model:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            print("Model __init__: ", self.__dict__)

    # 通过链式操作指定查询哪些列
    def field(self, columns):
        # 动态增加类实例属性
        self.columns = columns
        return self

    def select(self, **condition):
        table = self.__class__.__getattribute__(self, 'table_name')
        if hasattr(self, 'columns'):
            sql = "select %s from %s" % (self.columns, table)
        else:
            sql = "select * from %s" % table
        if condition is not None:
            sql += " where"
            for k, v in condition.items():
                sql += " %s='%s' and" % (k, v)
            sql += ' 1=1'
        print(sql)
        res = MySQL().query(sql)
        return res

    def insert(self):
        table = self.__class__.__getattribute__(self, 'table_name')
        keys = []
        values = []
        for k, v in self.__dict__.items():
            keys.append(k)
            values.append(str(v))
        sql = "insert into %s(%s) values ('%s')" % (table, ','.join(keys), "','".join(values))
        res = MySQL().execute(sql)
        print(res)
        print("insert sql: ", sql)


# 定义子类User和Article
class User(Model):
    table_name = 'user'

    # 调用父类构造方法
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Article(Model):
    table_name = 'article'

    # 调用父类构造方法
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


user = User()
# res = user.select()
res = user.field('userid, username, nickname').select(userid=1)
print(res)
print(res[0]['username'])

article = Article()
res = article.select(articleid = 1)
print(res)
