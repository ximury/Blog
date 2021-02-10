from flask import Blueprint, render_template, session

jinja2 = Blueprint('jinjia2', __name__)


@jinja2.route('/jinja2')
def jinja2_demo():
    session['username'] = 'user'
    article = {'title': 'this is title', 'count': 100}
    count = 100
    content = '<font color="red">这是一段红色的文字</font>'
    #
    # type = gettype()
    # return render_template('jinja2-demo.html', article=article, count=count, content=content, type=type)
    return render_template('jinja2-demo.html', article=article, count=count, content=content)


# 如何在html模板文件里调用py文件中的函数
# 第一种方案：使用上下文处理器来注册自定义函数到Jinja2模板引擎中，
# 并且返回一个字典类型的数据
@jinja2.context_processor
def gettype1():
    # type = "{'1': 'Php开发', '2': 'Java开发', '3': 'Python开发'}"
    type = {'1': 'Php开发', '2': 'Java开发', '3': 'Python开发'}
    return dict(mytype1=type)


# 第二种方案：按照标准的函数调用
# 在main函数里


# 如果要为自定义函数传参，则需要使用二层闭包进行包裹
# @jinja2.context_processor
# def myfun():
#     def mytype(arg):
#         type = {'1': 'Php开发', '2': 'Java开发', '3': 'Python开发'}
#         return type
#     return dict(mytype=mytype)
# 模板引擎里调用方式：{{mytype(100)}}

# 演示前端如何渲染从服务端获取的数据
@jinja2.route('/book')
def book():
    books = [
        {'id': 1, 'title': 'PHP教程', 'author': '张三', 'price': 52},
        {'id': 1, 'title': 'Python', 'author': '李四', 'price': 20},
        {'id': 1, 'title': 'JAVA教程', 'author': '泥鳅', 'price': 48},
        {'id': 1, 'title': 'GoLang教程', 'author': '象保', 'price': 37}
    ]
    return render_template('books.html', books=books)
