from sqlalchemy import create_engine, MetaData, Integer, Column, String, DateTime, Table, or_, func, and_

# 建立与MYSQL的连接
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# echo 参数为 True 时，会显示每条执行的 SQL 语句
engine = create_engine('mysql+pymysql://root:123456@localhost/woniunote', echo=True)

# 定义模型类继承的父类及数据连接会话
DBsession = sessionmaker(bind=engine)
dbsession = scoped_session(DBsession)  # 线程安全
# declarative_base() 创建了一个 BaseModel 类，这个类的子类可以自动与一个表关联
Base = declarative_base()
md = MetaData(bind=engine)


# 定义模型类
# class User(Base):
#     __tablename__ = "user"
#
#     # 如果需要在 SQLAlchemy里面直接创建表结构，则详细定义列
#     userid = Column(Integer, primary_key = True)
#     username = Column(String(50))
#     password = Column(String(32))
#     nickname = Column(String(30))
#     qq = Column(String(15))
#     role = Column(String(10))
#     credit = Column(Integer)
#     createtime = Column(DateTime)
#     updatetime = Column(DateTime)
#
# User.metadata.create_all(engine)  # 创建表

# 表已经存在了，就不需要上面的表结构进行创建表了
class User(Base):
    __table__ = Table('user', md, autoload=True)


class Article(Base):
    __table__ = Table('article', md, autoload=True)

class Comment(Base):
    __table__ = Table('comment', md, autoload=True)


if __name__ == '__main__':
    # 通过query和filter进行标准查询，all返回多行数据的列表
    res = dbsession.query(User).filter(User.userid <= 5).all()
    # res = dbsession.query(User).filter_by(userid=2).all()
    print(res, type(res))  # 返回的是列表
    print(res[0].username)
    for row in res:
        print(row.userid, row.username)

    # first() 只返回一条数据，直接返回模型类
    res = dbsession.query(User).filter(User.userid <= 5).first()
    print(res, type(res))  # 返回的是对象
    print(res.username)

    # 直接指定列名，则返回的是元组，不再是模型对象
    # 只查其中一列、两列
    res = dbsession.query(User.userid, User.username).filter(User.userid <= 5).first()
    print(res, type(res))  # 返回的是对象
    print(res.userid)

    # 新增
    # user = User(username='alchemy@163.com', password='jiw929uejao29', nickname='ORM', avatar='2.png', qq='36718371', role='user', credit=50,
    #             createtime='2021-02-09 19:21:52', updatetime='2021-02-09 19:21:52')
    # dbsession.add(user)
    # dbsession.commit()

    # 更新
    # row = dbsession.query(User).filter_by(userid=4).first()
    # row.nickname = '海德堡'
    # dbsession.commit()

    # 删除
    row = dbsession.query(User).filter_by(userid=4).delete()
    dbsession.commit()

    # 基础查询汇总
    # 直接打印一个类的时候，具体打印什么内容，由类的__repr__魔术方法决定，可重写
    # select * from user
    result = dbsession.query(User).all()
    # select userid, username from user
    result = dbsession.query(User.userid, User.username).all()
    # select * from user where userid=1 and qq='12344321'
    result = dbsession.query(User).filter_by(userid=1, qq='12344321').all()
    # select * from user where userid>5 or nickname='测试'
    result = dbsession.query(User).filter(or_(User.userid > 5, User.nickname == '测试')).all()
    # select * from user limit 3
    result = dbsession.query(User).limit(3).all()
    # select * from user limit 1, 2
    result = dbsession.query(User).limit(2).offset(1).all()  # 跳过1条数据，查询两条数据
    # select count(*) from user where ...
    count = dbsession.query(User).filter(User.userid > 2).count()
    print(count)
    # select distinct(qq) from user
    result = dbsession.query(User.qq).distinct(User.qq).all()
    # select * from user order by userid desc
    result = dbsession.query(User).order_by(User.userid.desc()).all()
    # select * from user where username like '%test%'
    result = dbsession.query(User).filter(User.username.like('%test%')).all()
    # select * from user group by role
    result = dbsession.query(User).group_by(User.role).all()
    # select * from user group by role
    result = dbsession.query(User).group_by(User.role).having(User.userid > 2).all()  # 带筛选
    # 聚合函数：min,max,avg,sum
    # select sum(credit) from user
    result = dbsession.query(func.sum(User.credit)).first()
    print(result)
    print(result[0].username)
    # filter: ==  >=  <=  !=  in  not

    # ------------------------------------------------------
    # 多表连接查询
    # 返回的结果不再是单纯的[Model, Model]数据结构，而是每张表的结果有独立的对象来维护
    # select * from article inner join `user` on article.userid=`user`.userid where article.articleid=1
    result = dbsession.query(Article, User).join(User, Article.userid == User.userid).all()
    print(result)
    for article, user in result:
        print(article.articleid, article.headline, user.userid, user.username)

    # select article.*, `user`.nickname from article inner join `user` on article.userid=`user`.userid where article.articleid=1
    result = dbsession.query(Article, User.nickname).join(User, Article.userid == User.userid).all()
    print(result)
    for article, nickname in result:
        print(article.articleid, article.headline, nickname)

    # 外连接，左外连接以左表为基础，查询符合条件的右表的数据，右表查出来的结果可以为空
    # outerjoin 默认为左外连接
    # select `user`.userid,sum(article.readcount) as total from `user` left join article on `user`.userid=article.userid
    result = dbsession.query(User.userid, User.nickname, func.sum(Article.readcount)) \
        .outerjoin(Article, User.userid == Article.userid).group_by(User.userid).all()

    # 复杂查询： and和or混用，username like 'test' or (userid>2 and nickname='小杜')
    result = dbsession.query(User).filter(or_(User.username.like('test'),
                                          and_(User.userid > 2, User.nickname == '小杜'))).all()
    result = dbsession.query(User).filter(and_(User.username.like('test'),
                                              or_(User.userid > 2, User.nickname == '小杜'))).all()
    result = dbsession.query(User).filter(User.username.like('test'),
                                              or_(User.userid > 2, User.nickname == '小杜')).all()

    for row in result:
        print(row.userid, row.username)

    # 三表连接
    result = dbsession.query(Comment, User, Article).join(User, Comment.userid==User.userid)\
        .join(Article, Article.articleid==Comment.articleid).all()
    print(result)

    # 利用SQLAlchemy执行原生SQL
    result = dbsession.execute("select * from user where userid>2").fetchall()
    print(result)
    print(result[0].username)

    dbsession.execute("delete from user where userid=3")
    dbsession.commit()

    # --------------------------------------------

    result = dbsession.query(User).all()
    print(result)
    list = []
    for row in result:
        # print(row.__dict__)
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                # print(k, v)
                dict[k] = v
            print(dict)
        list.append(dict)
    print(list)
