import datetime
import re
import time

from flask import session
from sqlalchemy import Table

from common.database import dbconnect
from common.utility import model_join_list
from module.user import User

dbsession, md, DBase = dbconnect()


class Comment(DBase):
    __table__ = Table('comment', md, autoload=True)

    # 新增一条评论
    def insert_comment(self, articleid, content, ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(userid=session.get('userid'), articleid=articleid,
                          content=content, ipaddr=ipaddr, createtime=now, updatetime=now)
        dbsession.add(comment)
        dbsession.commit()

    # 根据文章编号查询所有评论
    def find_by_articleid(self, articleid):
        result = dbsession.query(Comment).filter_by(articleid=articleid, hidden=0, replyid=0).all()
        return result

    # 修改意见：超过5条评论后再评论不加积分
    # 根据用户编号和日期进行查询评论是否已经超过每天5条限制
    def check_limit_per_5(self):
        start = time.strftime('%Y-%m-%d 00:00:00')  # 当天起始时间
        end = time.strftime("%Y-%m-%d 23:59:59")  # 当天结束时间
        result = dbsession.query(Comment).filter(Comment.userid == session.get('userid'),
                                                 Comment.createtime.between(start, end)).all()
        if len(result) > 5:
            return True
        else:
            return False

    # 查询评论与用户信息，注意评论也需要分页
    def find_limit_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, User).join(User, User.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hidden == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # 查询原始评论与对应的用户信息，带分页参数
    def find_comment_with_user(self, articleid, start, count):
        result = dbsession.query(Comment, User).join(User, User.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hidden == 0, Comment.replyid == 0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    # 查询回复评论，回复评论不需要分页
    def find_reply_with_user(self, replyid):
        result = dbsession.query(Comment, User).join(User, User.userid == Comment.userid) \
            .filter(Comment.replyid == replyid, Comment.hidden == 0) \
            .all()
        # if result:
        #     for res in result:
        #         # 截取时间为 年-月-日 形式
        #         res[0].createtime = re.search("(\d{4}-\d{1,2}-\d{1,2})", str(res[0].createtime)).group(1)
        return result

    # 新增一条回复，将原始评论的ID作为新评论的replyid字段来进行关联
    def insert_reply(self, articleid, commentid, content, ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(userid=session.get('userid'), articleid=articleid, content=content,
                          ipaddr=ipaddr, replyid=commentid, createtime=now, updatetime=now)
        dbsession.add(comment)
        dbsession.commit()

    # # 查询原始评论与对应的用户信息，带分页参数
    # def find_comment_with_user(self, articleid, start, count):
    #     result = dbsession.query(Comment, User).join(User, User.userid==Comment.userid)\
    #         .filter(Comment.articleid==articleid, Comment.hidden==0, Comment.replyid==0)\
    #         .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
    #     return result
    #
    # # 查询回复评论，回复评论不需要分页
    # def find_reply_with_user(self, replyid):
    #     result = dbsession.query(Comment,User)\
    #         .join(User, User.userid==Comment.userid)\
    #         .filter(Comment.replyid==replyid, Comment.hidden==0).all()
    #     return result

    # 根据原始评论和回复评论生成一个关联列表
    def get_comment_user_list(self, articleid, start, count):
        result = self.find_comment_with_user(articleid, start, count)
        comment_list = model_join_list(result)  # 原始评论的连接结果
        for comment in comment_list:
            # 根据commentid查询原始评论对应的回复评论，并转化为列表保存在comment_list中
            result = self.find_reply_with_user(comment['commentid'])
            # 为comment_list列表中的原始评论字典对象添加一个新的key叫reply_list
            # 用于存储当前这条原始评论的所有回复评论，如果无回复评论则列表值为空
            comment['reply_list'] = model_join_list(result)
        # 将新的数据结构返回给控制器接口
        return comment_list

    # 查询某篇文章原始评论的总数量
    def get_count_by_article(self, articleid):
        count = dbsession.query(Comment).filter_by(articleid=articleid, hidden=0, replyid=0).count()
        return count

    # 更新评论表的点赞/反对数量
    def update_agree_oppose(self, commentid, type):
        row = dbsession.query(Comment).filter_by(commentid=commentid).first()
        if type == 1:  # 表示赞成
            row.agreecount += 1
        elif type == 0:
            row.opposecount += 1
        dbsession.commit()

    # 隐藏评论
    def hide_comment(self, commentid):
        # 如果评论已经有回复，且回复未全部隐藏，则不接受隐藏操作
        # 返回 Fail 表示不满足隐藏条件，成功返回Done
        result = dbsession.query(Comment).filter_by(replyid=commentid, hidden=0).all()
        if len(result) > 0:
            return 'Fail'
        else:
            row = dbsession.query(Comment).filter_by(commentid=commentid).first()
            row.hidden = 1
            dbsession.commit()
            return 'Done'
