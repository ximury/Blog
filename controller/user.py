from module.user import User
from flask import Blueprint, jsonify

user = Blueprint('user', __name__)

@user.route('/user')
def user_demo():
    users = User()
    # row = users.find_user_id(1)
    # return row.username
    result = users.find_all_user()
    list = model_list(result)
    # jsonify 把标准的Python列表或字典或组合转化为JSON
    # 且响应的content-type也会自动设置为application/json
    return jsonify(list)


def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dict[k] = v
        list.append(dict)
    return list
