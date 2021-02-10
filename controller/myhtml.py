from flask import Blueprint
myhtml = Blueprint('myhtml', __name__)

# 直接把HTML代码写在函数中，并返回
@myhtml.route('/template1')
def template1():
    resp = """
        <div>
            <a href="#">test</a>
            <ul>
                <li>test 1</li>
                <li>test 2</li>
            </ul>
        </div>
    """
    return resp

# 直接将变量与HTML拼接，再写入程序
@myhtml.route('/template2/<username>')
def template2(username):
    # username = 'uname'
    resp = """
        <div>
            <a href="#">test</a>
            <ul>
                <li>test 1</li>
                <li>test 2</li>
            </ul>
        </div>
        <p>welcome %s here</p>
    """ % username
    return resp

# 把HTML文件内容保存到文件，打开该文件并响应
@myhtml.route('/template3')
def template03():
    with open('template/myhtml.html', encoding='utf-8') as file:
        html = file.read()
    return html

# 在HTML文件中标识模板变量，然后在渲染前对模板变量的值进行替换
# 实现Python代码与HTML模板页面分离
@myhtml.route('/template4')
def template04():
    # 类似于 render_template 功能，模板引擎
    with open('template/myhtml.html', encoding='utf-8') as file:
        html = file.read()
    html = html.replace('{{username}}', '蜗牛笔记')
    return html