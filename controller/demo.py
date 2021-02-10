# from main import app
from flask import Blueprint, request

# 定义一个Blueprint的模块名称
demo = Blueprint('this is my name: demo', __name__)

# 定义一个模块拦截器（蓝图拦截器）
@demo.before_request
def demo_before():
    url = request.path
    if url == '/demo':
        return '禁止访问'

@demo.route('/demo')
def my_demo():  # 函数名称不能与全局变量名称一致
    return 'Hello Demo'