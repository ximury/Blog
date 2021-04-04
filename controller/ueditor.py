import os
import time

from flask import Blueprint, abort, render_template, request, jsonify

from common.utility import compress_image

ueditor = Blueprint('ueditor', __name__)


@ueditor.route('/uedit', methods=['GET', 'POST'])
def uedit():
    # 根据ueditor的接口定义规则，如果前端参数为action=config，
    # 则表示试图请求后台的config.json文件，请求成功则说明后台接口正常
    param = request.args.get('action')  # 从url地址从取值 xxx?action=config
    if request.method == 'GET' and param == 'config':
        return render_template('config.json')
    elif request.method == 'POST' and request.args.get('action') == 'uploadimage':
        f = request.files['upfile']  # 获取前端图片文件数据
        filename = f.filename

        # 为上传来的文件生成统一的文件名
        suffix = filename.split('.')[-1]
        newname = time.strftime('%Y%m%d_%H%M%S.'+suffix)
        f.save('./resource/upload/' + newname)  # 保存图片到upload目录
        # 对图片进行压缩，按照1200像素宽度为准，并覆盖原始文件
        source = dest='./resource/upload/'+newname
        compress_image(source, dest, 1200)

        result = {}  # 构造响应数据
        result['state'] = 'SUCCESS'
        result['url'] = f"/upload/{newname}"
        result['title'] = filename
        result['original'] = filename

        return jsonify(result)  # 以JSON格式返回响应，供前端编辑器引用

    elif request.method == 'GET' and param == 'listimage':
        list = []
        filelist = os.listdir('./resource/upload')
        for filename in filelist:
            if filename.lower().endswith('.png') or filename.lower().endswith('.jpg'):
                list.append({'url': '/upload/%s' % filename})

        # 根据listimage接口规则构建响应数据
        result = {}
        result['state'] = 'SUCCESS'
        result['list'] = list
        result['start'] = 0
        result['total'] = 50
        return jsonify(result)
