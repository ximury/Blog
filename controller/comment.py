from flask import Blueprint, request, session

from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.user import User

comment = Blueprint('comment', __name__)

@comment.before_request
def before_comment():
    if session.get('islogin') is None or session.get('islogin') != 'true':
        # return '还未登录，不能进行评论'
        return 'not-login'
    else:
        pass

@comment.route('/comment', methods=['POST'])
def add():
    articleid = request.form.get('articleid')
    content = request.form.get('content').strip()
    ipaddr = request.remote_addr

    # 对评论内容进行简单检验
    if len(content) < 5 or len(content) > 1000:
        return 'content-invalid'
    comment = Comment()
    if not comment.check_limit_per_5():
        # try:
        comment.insert_comment(articleid, content, ipaddr)
        # 评论成功后，更新积分明细和剩余积分，以及文章回复数量
        Credit().insert_detail(type='添加评论', target=articleid, credit=2)
        User().update_credit(2)
        Article().update_replycount(articleid)
        return 'add-pass'
    # except:
    #     return 'add-fail'
    else:
        return 'add-limit'


@comment.route('/reply', methods=['POST'])
def reply():
    articleid = request.form.get('articleid')
    commentid = request.form.get('commentid')
    content = request.form.get('content').strip()
    ipaddr = request.remote_addr

    # 如果评论的字数低于5个或多于1000，视为不合法
    if len(content) < 5 or len(content) > 1000:
        return 'content-invalid'

    comment = Comment()
    # 没有超出限制才能发表评论
    if not comment.check_limit_per_5():
        try:
            comment.insert_reply(articleid=articleid, commentid=commentid,
                                 content=content, ipaddr=ipaddr)
            # 评论成功后，同步更新credit表明细，user表积分和article表回复数
            Credit().insert_detail(type='回复评论', target=articleid, credit=2)
            User().update_credit(2)
            Article().update_replycount(articleid)
            return 'reply-pass'
        except:
            return 'reply-fail'
    else:
        return 'reply-limit'
