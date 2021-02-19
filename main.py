import datetime
import os

from flask import Flask, abort, render_template
from flask_sqlalchemy import SQLAlchemy
# 下面两行是解决 ModuleNotFoundError: No module named 'MySQLdb'
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__, static_url_path="/", static_folder="resource", template_folder="template")

app.config['SECRET_KEY'] = os.urandom(24)

# -----------------------------------
# 使用Flask集成方式处理SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/woniunote?charset=utf8'
# FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and
# will be disabled by default in the future.  Set it to True or False to suppress this warning.
#   'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # True表示跟踪数据库的修改，及时发送信号
# 有时数据库连接将会失去状态，db.session太多未关闭，导致池大小在一定的时间间隔后耗尽
# sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 10 reached
app.config['SQLALCHEMY_POOL_SIZE'] = 20
# 实例化db对象
db = SQLAlchemy(app)

# -----------------------------------

# 定义 404 错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-404.html')


# 定义 500 错误页面
@app.errorhandler(500)
def server_error(e):
    return render_template('error-500.html')


# 定义全局拦截器，实现自动登录
@app.before_request
def before():
    url = request.path
    pass_list = ['/user', '/login', '/logout']
    if url in pass_list or url.endswith('.js') or url.endswith('.jpg'):
        pass
    if session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username != None and password != None:
            user = User()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role


@app.after_request
def after(response):
    try:
        # commit transaction
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# 通过自定义过滤器来重构truncate原生过滤器
def mytruncate(s, length, end='...'):
    # 中文定义为1个字符，英文定义为0.5个字符
    # 遍历整个字符串，获取每个字符的ASCII码，如果是在128以内（0-127）或256，则认为是英文，否则是中文
    count = 0
    new = ''
    if len(s) < 16:
        end = ''
    for c in s:
        new += c
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
        if count > length:
            break
    return new + end


# 自定义jinja2过滤器：截取日期字符串为 年-月-日 格式
def subdate(date: datetime.time):
    newdate = re.search("(\d{4}-\d{1,2}-\d{1,2})", str(date)).group(1)
    return newdate


# 注册mytruncate过滤器，在侧边栏side.html中使用
app.jinja_env.filters.update(mytruncate=mytruncate)
app.jinja_env.filters.update(subdate=subdate)


# 定义文章类型函数，供模板页面直接调用
@app.context_processor
def gettype():
    type = {
        '1': '招聘',
        '2': 'Python开发',
        '3': 'Java开发',
        '4': 'Golang开发'
    }
    # 在index-base.html中会使用到article_type
    return dict(article_type=type)


if __name__ == '__main__':
    # a = '2020-05-08 10:55:00'
    # m = re.search("(\d{4}-\d{1,2}-\d{1,2})", a)
    # print(m, type(m), m.group(1), type(m.group(1)))
    from controller.index import *

    app.register_blueprint(index)

    from controller.user import *

    app.register_blueprint(user)

    from controller.article import *

    app.register_blueprint(article)

    from controller.favorite import *

    app.register_blueprint(favorite)

    from controller.comment import *

    app.register_blueprint(comment)

    from controller.opinion import *

    app.register_blueprint(opinion)

    from controller.ueditor import *
    app.register_blueprint(ueditor)

    app.run(debug=True)
