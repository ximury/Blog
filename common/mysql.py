import pymysql
from pymysql.cursors import DictCursor

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456',
                       charset='utf8', database='woniunote', autocommit=True)
print(conn.get_server_info())

# 实例化游标对象
# 定义SQL语句
# 通过游标执行SQL语句

cursor = conn.cursor(DictCursor)
sql = "select * from user"
cursor.execute(sql)
res = cursor.fetchall()
print(res)
print(res[1]['username'])

# for row in res:
#     print(row[2])
# print(res[2][6])

# 更新
sql = "update user set qq='1253716' where userid = 1"
cursor.execute(sql)
conn.commit()  # 提交修改，update,insert,delete

cursor.close()
conn.close()