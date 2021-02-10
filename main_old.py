import os

from flask import Flask, render_template, request, url_for, redirect, session, make_response

app = Flask(__name__, static_url_path="/", static_folder="resource", template_folder="template")

# 在启用Session的时候,一定要有SECRET_KEY
app.config['SECRET_KEY'] = os.urandom(24)  # 生成随机数种子，用于产生SessionID


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/article')
def read():
    return render_template('article.html')


@app.route('/publish')
def publish():
    return render_template('publish.html')


@app.route('/user/reg', methods=['POST'])
def register():
    return 'Hello'


# 获取查询参数
# http://127.0.0.1:5000/testroute?username=ur&password=123
@app.route('/testroute')
def testroute():
    username = request.args.get('username')
    password = request.args.get('password')
    return '用户名为：%s，密码为：%s' % (username, password)


# 获取路由地址参数，定义限制articleid值为int类型
# http://127.0.0.1:5000/article/3-2
@app.route('/article/<int:articleid>-<page>')
def article(articleid, page):
    return f"正在访问的文章编号为：{articleid}，页面为：{page}"


# 直接读取POST请求正文参数
@app.route('/user/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'nice' and password == '123':
        return 'SUCCESS'
    else:
        return 'FAILED'


# RESTFUL风格定义登陆注册接口路由
# 注册：POST--/user
# 登录：POST--/session
# 注销：DELETE--/session

# URL重定向，HTTP协议本身功能，302状态码，在响应头里通过指定Location字段告诉浏览器跳转地址
@app.route('/redir')
def redir():
    # return redirect(url_for('read'))  #使用项目中的函数名进行重定向，通过url_for构建重定向地址
    return redirect('/article')  # 直接指定重定向地址


@app.route('/redirjs')
def redirjs():
    # html = "<script>location.href='/'</script>"
    # 延时跳转
    html = '感谢访问，2秒以后进行跳转到首页'
    html += "<script>"
    html += "setTimeout(function() {location.href='/';}, 2000);"
    html += "</script>"
    return html


# Session和Cookie
# 要处理Session，必须为app实例设置SECREAT_KEY配置参数，配置随机数生成器（SessionID），再使用Session函数进程操作（add/delete）
# 要处理Cookie，需要使用response对象来往HTTP的响应中写入满足HTTP协议的Cookie要求的信息（Key，Value，OutTime）
@app.route('/session')
def sess():
    session['islogin'] = 'true'
    session['username'] = 'uname'
    session['nickname'] = 'nname'
    session['role'] = 'editor'
    # return session.get('username')
    return 'Done'


# 利用自定义响应的方式往浏览器设置Cookie
@app.route('/cookie')
def cookie():
    response = make_response("这是设置cookie的操作")
    # set_cookie方法在base_response.py中寻找原型，同时也会找到max_age参数，秒为单位
    response.set_cookie('username', 'nice', max_age=30)
    response.set_cookie('password', '123', max_age=30)
    # request.cookies.get('username') # 无法在同一个接口中既设置cookie又获取cookie，而session可以
    return response


@app.route('/sc/read')
def scread():
    # return '当前的用户名为：%s' % session.get('username')  # 获取session信息
    return '当前的用户名为：%s' % request.cookies.get('username')  # 获取cookie信息


# 引用demo.py
from controller.demo import *

app.register_blueprint(demo)  # 使用Blueprint时，必须将其注册到app中


# 针对app实例定义 全局拦截器
# @app.before_request
def before():
    # 如果用户已登录session['islogin] = 'true'，则不拦截
    url = request.path  # 读取到当前接口的地址
    if url == '/session':
        pass
    elif session.get('islogin') != 'true':
        return '还未登录，无法访问接口'
    else:
        pass

    # 白名单：所有静态资源（JS，Image，CSS）必须设置为白名单
    # 登录或者跟用户操作有权限要求的接口前要做的操作，必须放行
    pass_list = ['/', 'reg', 'login', '/vcode', '/session']
    suffix = url.endswith('.png') or url.endswith('.jpg') or url.endswith('.css') or url.endswith('.js')
    if url in pass_list or suffix:
        pass


if __name__ == '__main__':
    app.run(debug=True)
