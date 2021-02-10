class User:
    table_name = 'user'  # 类属性

    def __init__(self):
        self.username = 'ximu'  # 实例变量
        self.password = '123321'
        self.email = 'abc@163.com'

    def method(self, value):
        print("Hello %s" % value)

    # 链式操作
    def chain(self):
        print("通过返回当前类的实例进行连续的方法调用")
        return self

    def hello(self):
        print("hello in chain")
        return self


if __name__ == '__main__':
    print(User.__dict__)
    # 实例化User类
    user = User()
    print(user.__class__)
    print(user.__class__.__dict__)

    # 通过__来区分哪些是自定义的属性和方法
    for k, v in User.__dict__.items():
        if not k.startswith('__'):
            print(k, v)

    print(User.__name__)  # 输出为 User

    print(user.__dict__)  # 获取实例变量或方法

    user.nickname = '郝'  # 动态为实例设置属性
    print(user.__dict__)

    user.__setattr__('nickname', '冉冉')  # 动态为实例设置属性，面向对象
    print(user.__dict__)

    setattr(user, 'nickname', '分析')  # 面向过程
    print(user.__dict__)
    print("-------------------------------")

    print(user.__getattribute__('username'))
    print(user.__getattribute__('method'))
    user.__getattribute__('method')('北京')
    getattr(user, 'method')('北京')

    # 链式调用
    user.chain().chain().hello().chain().hello()
