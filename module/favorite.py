import time

from flask import session
from sqlalchemy import Table

from common.database import dbconnect

dbsession, md, DBase = dbconnect()

class Favorite(DBase):
    __table__ = Table('favorite', md, autoload=True)

    # 插入文章收藏数据
    def insert_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get('userid')).first()
        if row is not None:
            row.canceled = 0
            row.updatetime = time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            favorite = Favorite(articleid=articleid, userid=session.get('userid'), canceled=0,
                                createtime=now, updatetime=now)
            dbsession.add(favorite)
        dbsession.commit()

    # 取消收藏
    def cancel_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get('userid')).first()
        row.canceled = 1
        row.updatetime = time.strftime('%Y-%m-%d %H:%M:%S')
        dbsession.commit()

    # 判断是否已经被收藏
    def check_favorite(self, articleid):
        row = dbsession.query(Favorite).filter_by(articleid=articleid, userid=session.get('userid')).first()
        if row is None:
            return False
        elif row.canceled == 1:
            return False
        else:
            return True