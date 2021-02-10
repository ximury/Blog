import os

from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
# 下面两行是解决 ModuleNotFoundError: No module named 'MySQLdb'
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__, static_url_path="/", static_folder="resource", template_folder="template")

app.config['SECRET_KEY'] = os.urandom(24)

# ------------------
# 使用Flask集成方式处理SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/woniunote?charset=utf8'
# FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and
# will be disabled by default in the future.  Set it to True or False to suppress this warning.
#   'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # True表示跟踪数据库的修改，及时发送信号
# 实例化db对象
db = SQLAlchemy(app)
# ------------------

# 第二种方案：按照标准的函数调用
def gettype2():
    type = {'1': 'Php开发', '2': 'Java开发', '3': 'Python开发'}
    return type
app.jinja_env.globals.update(mytype2=gettype2)

# 自定义模板页面过滤器
def mylen(str):
    return len(str)
app.jinja_env.filters.update(mylen=mylen)


# 必须放在main函数前面，否则不起作用
# 模板继承与模板引入
@app.route('/')
def index():
    return render_template('index-base.html')

#定义 404 错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-404.html')

#定义 500 错误页面
@app.errorhandler(500)
def server_error(e):
    return render_template('error-500.html')

# 模拟一个500的错误
@app.route('/error')
def error_500():
    try:
        x= 10/0
        return x
    except:
        return abort(500)

if __name__ == '__main__':
    from controller.myhtml import *
    app.register_blueprint(myhtml)

    from controller.jinja2 import *
    app.register_blueprint(jinja2)

    # module/user引入main中db,controller/user引入module/user中User,
    # main中再次引入controller/user中定义的蓝图进行注册，形成循环引用，所以放在__main__函数里
    from controller.user import *
    app.register_blueprint(user)

    app.run(debug=True)


