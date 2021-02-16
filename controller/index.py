import math

from flask import Blueprint, render_template, abort, jsonify, session, request

from module.article import Article
from module.user import User

index = Blueprint('index', __name__)


@index.route('/')
def home():
    if session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username!=None and password!=None:
            user = User()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role

    article = Article()
    result = article.find_limit_with_user(0, 10)
    # print(result, end='---------------\n')
    total = math.ceil(article.get_total_count() / 10)  # 向上取整

    # 以下是在首页添加侧边栏的内容，side-jinja2.html中使用到，但是这种方式有一个缺陷：
    # 需要在每个HTML页面中引用引用一下代码，重复率高，改良版在：side.html中
    last, most, recommended = article.find_most_recommended()
    return render_template('index-base.html', result=result, page=1, total=total,
                           last=last, most=most, recommended=recommended)


@index.route('/page/<int:page>')
def paginate(page):
    start = (page - 1) * 10
    article = Article()
    result = article.find_limit_with_user(start, 10)
    total = math.ceil(article.get_total_count() / 10)  # 向上取整
    return render_template('index-base.html', result=result, page=page, total=total)


@index.route('/type/<int:type>-<int:page>')
def classify(type, page):
    start = (page - 1) * 5  # 计算某一页需要跳过的文章数目
    article = Article()
    result = article.find_by_type(type, start, 5)  # 某一页的文章详情
    total = math.ceil(article.get_count_by_type(type) / 5)  # 统计页数
    return render_template('type.html', result=result, page=page, total=total, type=type)


@index.route('/search/<int:page>-<keyword>')
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == '' or '%' in keyword or len(keyword)>10:
        abort(404)
    start = (page - 1) * 10
    article = Article()
    result = article.find_by_headline(keyword, start, 10)
    total = math.ceil(article.get_count_by_headline(keyword) / 10)
    return render_template('search.html', result=result, page=page, total=total, keyword=keyword)

# 前后端分离方式：
# 利用JavaScript处理JSON的方式进行原生代码的前端渲染
# 1.通过后台:原生Python输出HTML,使用模板引擎,浏览器直接绘制HTML
# 2.通过前端:使用JavaScript动态填充DOM元素(JSON).对搜索引擎不友好
# 前后端分离(Web App主流开发模式)-->核心思想:字符串拼接
# 3.前后端分离可以有效减少服务器渲染HTML的资源消耗,把渲染的过程交给前端浏览器处理
@index.route('/recommend')
def recommend():
    article = Article()
    last, most, recommended = article.find_most_recommended()
    # return jsonify(last, most, recommended)
    list = []
    list.append(last)
    list.append(most)
    list.append(recommended)
    return jsonify(list)