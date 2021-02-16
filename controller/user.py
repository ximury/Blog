import hashlib
import re

from flask import Blueprint, make_response, session, request, redirect, url_for

from common.utility import ImageCode, gen_email_code, send_email
from module.credit import Credit
from module.user import User

user = Blueprint('user', __name__)


# 获取图片验证码
@user.route('/vcode')
def vcode():
    code, bstring = ImageCode().get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    # 大小写皆可
    session['vcode'] = code.lower()
    return response


# 发送邮件验证码
@user.route('/ecode', methods=['POST'])
def ecode():
    email = request.form.get('email')
    if not re.match('.+@.+\..+', email):
        return 'email-invalid'
    code = gen_email_code()
    try:
        send_email(email, code)
        session['ecode'] = code  # 将邮箱验证码保存在session中
        return 'send-pass'
    except:
        return 'send-fail'


# 注册
@user.route('/user/reg', methods=['POST'])
def register():
    user = User()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    ecode = request.form.get('ecode').strip()

    # 校验邮箱验证码是否正确
    if ecode != session.get('ecode'):
        return 'ecode-error'

    # 验证邮箱地址的正确性和密码的有效性, 数据库中username是邮箱格式
    elif not re.match('.+@.+\..+', username) or len(password) < 5:
        return 'up-invalid'

    # 验证用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        return 'user-repeated'

    else:
        # 实现注册功能
        # 密码加密
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.do_register(username, password)
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role
        # 更新积分详情表
        Credit().insert_detail(type='用户注册', target='0', credit=50)
        return 'reg-pass'


# 登录
@user.route('/user/login', methods=['POST'])
def login():
    user = User()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    vcode = request.form.get('vcode').lower().strip()

    # 校验图像验证码是否正确,0000用来做测试
    if vcode != session.get('vcode') and vcode != '0000':
        return 'vcode-error'

    else:
        # 实现登录功能
        # 密码加密
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        if len(result) == 1 and result[0].password == password:
            session['islogin'] = 'true'
            session['userid'] = result[0].userid
            session['username'] = username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role
            # 更新积分详情表
            Credit().insert_detail(type='正常登录', target='0', credit=1)
            user.update_credit(1)
            # 将Cookie写入浏览器,持久化存储
            response = make_response('login-pass')
            response.set_cookie('username', username, max_age=30 * 24 * 3600)
            response.set_cookie('password', password, max_age=30 * 24 * 3600)
            return response
        else:
            return 'login-fail'


# 注销
@user.route('/logout')
def logout():
    # 清空session，页面跳转
    session.clear()
    # return redirect('/')
    response = make_response('注销并进行重定向', 302)
    response.headers['Location'] = url_for('index.home')
    response.delete_cookie('username')
    response.set_cookie('password', '', max_age=0)  # 与上面效果一样
    return response


# 修改密码
@user.route('/user/updatepwd', methods=['POST'])
def updatepwd():
    user = User()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    ecode = request.form.get('ecode').strip()

    # 校验邮箱验证码是否正确
    if ecode != session.get('ecode'):
        return 'ecode-error'

    # 验证邮箱地址的正确性和密码的有效性, 数据库中username是邮箱格式
    elif not re.match('.+@.+\..+', username) or len(password) < 5:
        return 'up-invalid'

    else:
        # 实现修改密码功能
        # 密码加密
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.do_updatepwd(username, password)
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role
        return 'updatepwd-pass'

# password = '123321'
# print(hashlib.md5(password.encode()).hexdigest())
## c8837b23ff8aaa8a2dde915473ce0991
# password = '123456'
# print(hashlib.md5(password.encode()).hexdigest())
## e10adc3949ba59abbe56e057f20f883e
