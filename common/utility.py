import random
import string
from io import BytesIO

# 要想导入PIL，首先要下载一个Pillow，网址如下: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
# 要下载本机可支持的版本，查看合适的版本：终端输入 pip debug --verbose，在 Compatible tags字样下可以查看到支持的版本
# 将Pillow下载保存到某位置后，执行 pip install xxx.\xx.whl，比如：pip install D:\Pillow‑8.1.0‑cp37‑cp37m‑win32.whl
from PIL import Image, ImageFont, ImageDraw


class ImageCode:
    # 生成用于绘制字符串的随机颜色
    def rand_color(self):
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    # 生成4位随机字符串
    def gen_text(self):
        # sample用于从一个大的列表或字符串中随机取得n个字符，来构建一个子列表
        list = random.sample(string.ascii_letters + string.digits, 4)
        return ''.join(list)

    # 画一些线，用于干扰，其中draw位PIL中的ImageDraw对象
    def draw_lines(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=2)

    # 绘制验证码图片
    def draw_verify_code(self):
        code = self.gen_text()  # 验证码
        width, height = 120, 50  # 设定图片大小，可根据实际需求调整
        # 创建图片对象，并设定背景色为白色
        im = Image.new('RGB', (width, height), 'white')
        # 选择使用何种字体及字体大小
        font = ImageFont.truetype(font='arial.ttf', size=40)
        draw = ImageDraw.Draw(im)  # 创建ImageDraw对象
        # 绘制字符串
        for i in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)),
                      text=code[i], fill=self.rand_color(), font=font)
        # 绘制干扰线
        self.draw_lines(draw, 2, width, height)
        # im.show()  # 临时调试，显示图片输出
        return im, code

    # 生成图片验证码，并返回给控制器
    def get_code(self):
        image, code = self.draw_verify_code()
        buf = BytesIO()
        image.save(buf, 'jpeg')
        bstring = buf.getvalue()
        return code, bstring


from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header


# 发送QQ邮箱验证码，参数为收件箱地址和随机生成的验证码
def send_email(receiver, ecode):
    sender = 'wyj <2629409421@qq.com>'  # 你的邮箱账号和发件者签名
    # 定义发送邮件的内容，支持HTML标签和CSS样式
    content = f"<br/>欢迎注册NOTE博客系统账号，您的邮箱验证码为：<span style='color:red; font-size:20px;'>" \
              f"{ecode}</span>, 请复制到注册窗口<br/>"
    # 实例化邮件对象，并指定邮件的关键信息
    message = MIMEText(content, 'html', 'utf-8')
    # 指定邮件的标题，同样使用utf-8编码
    message['Subject'] = Header('NOTE博客的注册验证码', 'utf-8')
    message['From'] = sender  # 发件人信息
    message['To'] = receiver  # 收件人邮箱地址

    # 与QQ邮箱服务器连接
    smtpObj = SMTP_SSL('smtp.qq.com')
    # 通过邮箱账号和获取到的授权码登录QQ邮箱
    smtpObj.login(user='2629409421@qq.com', password='awdmrncjktreeche')
    # 指定发件人，收件人和邮件内容
    smtpObj.sendmail(sender, receiver, str(message))
    smtpObj.quit()


# 生成6位随机字符串作为邮箱验证码
def gen_email_code():
    str = random.sample(string.ascii_letters + string.digits, 6)
    return ''.join(str)


# code = gen_email_code()
# print(code)
# send_email('2629409421@qq.com', code)

# 单个模型类转化为标准的Python list数据
def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dict[k] = v
        list.append(dict)
    return list


# SQLAlchemy连接查询两张表的结果集转化为[{},{}]
# Comment, User, [{Comment, User}, {Comment, User}]
def model_join_list(result):
    list = []  # 定义列表用于存放所有行
    for obj1, obj2 in result:
        dict = {}
        for k1, v1 in obj1.__dict__.items():
            if not k1.startswith('_sa_instance_state'):
                if not k1 in dict:  # 如果字典中已经存在相同的key则跳过
                    dict[k1] = v1
        for k2, v2 in obj2.__dict__.items():
            if not k2.startswith('_sa_instance_state'):
                if not k2 in dict:
                    dict[k2] = v2
        list.append(dict)
    return list
