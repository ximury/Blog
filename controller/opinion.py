from flask import Blueprint, request, session, jsonify

from module.comment import Comment
from module.opinion import Opinion

opinion = Blueprint('opinion', __name__)


@opinion.route('/opinion', methods=['POST'])
def do_opinion():
    commentid = request.form.get('commentid')
    type = int(request.form.get('type'))
    ipaddr = request.remote_addr

    # 判断是否已点赞/反对
    opinion = Opinion()
    is_checked = opinion.check_opinion(commentid, ipaddr)
    if is_checked:
        return 'already-opinion'
    else:
        opinion.insert_opinion(commentid, type, ipaddr)
        Comment().update_agree_oppose(commentid, type)
        return 'opinion-pass'
