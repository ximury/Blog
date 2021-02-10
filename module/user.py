from sqlalchemy import Table, MetaData

from main import db  # 直接引入main中的全局变量db


class User(db.Model):
    __table__ = Table('user', MetaData(bind=db.engine), autoload=True)

    def find_user_id(self, userid):
        row = db.session.query(User).filter(User.userid == userid).first()
        return row

    def find_all_user(self):
        row = db.session.query(User).filter().all()
        return row