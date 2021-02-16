from flask import Blueprint, abort, render_template, request

from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.favorite import Favorite
from module.user import User

article = Blueprint('article', __name__)


@article.route('/article/<int:articleid>')
def read(articleid):
    try:
        # 数据格式：(Article, 'nickname')
        result = Article().find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)
    dict = {}
    for k, v in result[0].__dict__.items():
        if not k.startswith('_sa_instance_state'):
            dict[k] = v
    dict['nickname'] = result.nickname

    # 如果已经消耗过积分，不再截取文章内容
    payed = Credit().check_payed_article(articleid)
    position = 0
    if dict['credit'] != 0:
        if not payed:
            content = dict['content']
            temp = content[0:int(len(content) / 2)]
            # 找到一个闭合标签
            position = temp.rindex('</p>') + 4
            dict['content'] = temp[0:position]
            # print(dict)
    Article().update_read_count(articleid)  # 阅读次数+1

    # 是否收藏
    is_favorited = Favorite().check_favorite(articleid)

    # 获取当前文章的上一篇和下一篇
    prev_next = Article().find_prev_next_by_id(articleid)

    # 显示当前文章评论信息
    # comment_user = Comment().find_limit_with_user(articleid, 0, 50)

    # 对应新的模板文件——article-base.html
    comment_list = Comment().get_comment_user_list(articleid, 0, 50)
    # print(comment_list)

    # return render_template('article-base.html', result=result)
    return render_template('article-base.html', article=dict, position=position, payed=payed,
                           is_favorited=is_favorited, prev_next=prev_next, comment_list=comment_list)
    # return render_template('article-base-jinja2.html', article=dict, position=position, payed=payed,
    #                        is_favorited=is_favorited, prev_next=prev_next, comment_user=comment_user)

@article.route('/readall', methods=['POST'])
def read_all():
    position = int(request.form.get('position'))
    articleid = request.form.get('articleid')
    article = Article()
    result = article.find_by_id(articleid)
    content = result[0].content[position:]

    payed = Credit().check_payed_article(articleid)
    if not payed:
        # 添加积分明细
        Credit().insert_detail(type='阅读文章', target=articleid, credit=-1 * result[0].credit)
        # 减少用户表的剩余积分
        User().update_credit(credit=-1 * result[0].credit)
    return content
