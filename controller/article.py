import math

from flask import Blueprint, abort, render_template, request, session

from common.utility import parse_image_url, generate_thumb
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
    comment_user = Comment().find_limit_with_user(articleid, 0, 50)

    # 对应新的模板文件——article-base.html
    comment_list = Comment().get_comment_user_list(articleid, 0, 10)

    # 原始评论总页数
    count = Comment().get_count_by_article(articleid)
    total = math.ceil(count/10)

    # return render_template('article-base.html', result=result)
    # 评论有分页，回复已做好，最终模样，点赞、反对、隐藏 功能俱全
    return render_template('article-base.html', article=dict, position=position, payed=payed,
                           is_favorited=is_favorited, prev_next=prev_next, comment_list=comment_list,
                           total=total)

    # 评论无分页，回复与评论并列
    # return render_template('article-base-jinja2.html', article=dict, position=position, payed=payed,
    #                        is_favorited=is_favorited, prev_next=prev_next, comment_user=comment_user)
    # 评论无分页，但回复已做好，在对应评论下，点赞、反对 数量显示功能具备
    # return render_template('article-base-reply.html', article=dict, position=position, payed=payed,
    #                        is_favorited=is_favorited, prev_next=prev_next, comment_list=comment_list)
    # jquery方式未成功实现，存在BUG
    # return render_template('article-base-jquery.html', article=dict, position=position, payed=payed,
    #                        is_favorited=is_favorited, prev_next=prev_next, comment_list=comment_list,
    #                        total=total)
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

@article.route('/prepost')
def pre_post():
    return render_template('publish.html')

@article.route('/article', methods=['POST'])
def add_article():
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))
    credit = int(request.form.get('credit'))
    drafted = int(request.form.get('drafted'))
    checked = int(request.form.get('checked'))
    articleid = int(request.form.get('articleid'))
    print(session)
    print(session.get('userid'))
    if session.get('userid') is None:
        return 'perm-denied'
    else:
        user = User().find_by_userid(session.get('userid'))
        if user.role == 'editor':
            # 权限合格，可以执行发布文章的代码
            # 首先为文章生成缩略图，找不到则随机生成一张
            url_list = parse_image_url(content)
            if len(url_list) > 0:
                thumbname = generate_thumb(url_list)
            else:
                thumbname = '%d.png' % type
            article = Article()
            if articleid == 0:
                try:
                    id = article.insert_article(type=type, headline=headline, content=content, thumbnail=thumbname,
                                                  credit=credit, drafted=drafted, checked=checked)
                    return str(id)
                except Exception as e:
                    return 'post-fail'
            else:
                try:
                    id = article.update_article(articleid=articleid, type=type, headline=headline, content=content, thumbnail=thumbname,
                                                  credit=credit, drafted=drafted, checked=checked)
                    return str(id)
                except Exception as e:
                    return 'post-fail'
        # 如果角色不是作者，则只能投稿，不能正式发布
        elif checked == 1:
            return 'perm-denied'
        else:
            return 'perm-denied'