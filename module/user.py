import random
import time

from flask import session
from sqlalchemy import Table

from common.database import dbconnect

dbsession, md, DBase = dbconnect()


class User(DBase):
    __table__ = Table('user', md, autoload=True)

    # 查询用户名，可用于注册时判断用户名是否已注册，也可用于登录校验
    def find_by_username(self, username):
        result = dbsession.query(User).filter_by(username=username).all()
        return result

    # 实现注册，首次注册时用户只需要输入用户名以及密码，所以只需要两个参数
    # 注册时，在模型类中为其他字段尽力生成一些可用的值，虽不全面，但可用
    # 通常用户注册时不建议填些太多资料，影响体验，可待用户后续逐步完善
    def do_register(self, username, password):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        nickname = username.split('@')[0]  # 默认将邮箱账号前缀作为昵称
        avatar = str(random.randint(1, 10))  # 从10张头像图片中随机选择一张
        user = User(username=username, password=password, role='user', credit=50,
                    nickname=nickname, avatar=avatar + '.png', createtime=now, updatetime=now)
        dbsession.add(user)
        dbsession.commit()
        return user

    # 修改用户剩余积分
    def update_credit(self, credit):
        user = dbsession.query(User).filter_by(userid=session.get('userid')).one()
        user.credit = int(user.credit)+credit
        dbsession.commit()

    def do_updatepwd(self, username, password):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        user = dbsession.query(User).filter_by(username=username).one()
        user.password=password
        user.updatetime = now
        dbsession.commit()
        return user