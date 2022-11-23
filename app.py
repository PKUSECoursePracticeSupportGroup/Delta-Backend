from argparse import Namespace
from functools import total_ordering
from mailbox import mboxMessage
from socket import socket
from sre_parse import ESCAPES
# from tkinter.font import names
from flask import Flask, session
from flask_socketio import SocketIO, emit

from modules.utils import config, db
from modules.post_info import post_info
from modules.post_info import add_post_info, search_post_info, delete_post_info, change_post_info
from modules.login_regist import AccountInfo
from modules.login_regist import login_blue, regist_blue, getsesinfo_blue, logout_blue
from modules.user_info_function import user_info
from modules.user_info_function import add_user_info, search_user_info, delete_user_info, change_user_info

app = Flask(__name__)
app.secret_key=config.SECRET_KEY
# register blueprint
app.register_blueprint(post_info)
app.register_blueprint(user_info)
app.register_blueprint(login_blue)
app.register_blueprint(regist_blue)
app.register_blueprint(getsesinfo_blue)
app.register_blueprint(logout_blue)
# load config file
app.config.from_object(config)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def test():
    return "Hello World!"

################ Post Info WebSocket Begin ################
@socketio.on('Add Post Info', namespace='/post')
def new_post(message):
    print("test")
    flag = add_post_info(message['headline'], message['tags'], float(message['price_and_number']), message['info'], message['picture'])
    if flag:
        emit('post_info_response', {'result':'Post Success'})
    else:
        emit('post_info_response', {'result':'Post Failure'})


@socketio.on('Search Post Info', namespace='/list') 
def show_post(message):
    limit = 15
    res, total_post = search_post_info(tags=message['tags'], limit=limit, offset=(message['cur_page']-1)*15)
    if total_post == 0:
            emit('post_info_response', {'result': 'Search Failure', 'lst': [], 'cur_page': message['cur_page'], 'total_post': total_post})
    else:
        ret = []
        for per in res:
            ret.append({'post_id': per.id, 'title': per.headline, 'imgUrl': per.picture})
        emit('post_info_response', {'result': 'Search Success', 'lst': ret, 'cur_page': message['cur_page'], 'total_post': total_post})


@socketio.on('Search Post Info by Key Words', namespace='/key-list') 
def search_by_key_words(message):
    limit = 15
    key_words = message['key_words'].split() # 根据空白符分隔
    res, total_post = search_post_info(key_words=key_words, limit=limit, offset=(message['cur_page']-1)*15)
    if total_post == 0:
        emit('key_words_search_response', {'result': 'Search Failure', 'lst': [], 'cur_page': message['cur_page'], 'total_post': total_post})
    else:
        ret = []
        for per in res:
            ret.append({'post_id': per.id, 'title': per.headline, 'imgUrl': per.picture})
        emit('post_info_response', {'result': 'Search Success', 'lst': ret, 'cur_page': message['cur_page'], 'total_post': total_post})


@socketio.on('Open Post Info', namespace='/detail')
def open_post(message):
    res, _ = search_post_info(id=message['id'])
    if res == []:
        print('No such id!')
        emit('post_info_response', {'result':'Open Post Failure', 'id':None, 'headline':None, 'tags':None, 'price_and_number': None, 'info':None, 'picture':None})
    elif len(res) > 1:
        print('Same id for post info!')
        emit('post_info_response', {'result':'Open Post Failure', 'id':None, 'headline':None, 'tags':None, 'price_and_number': None, 'info':None, 'picture':None})
    else:
        res = res[0] # 肯定只有一个
        emit('post_info_response', {'result':'Open Post Success', 'id': res.id, 'headline': res.headline, 'tags': res.tags, 'price_and_number': res.price_and_number, 'info': res.info, 'picture': res.picture})
################ Post Info WebSocket End ################


################ User Info WebSocket Begin ################
@socketio.on('Change user Info', namespace='user-list')
def change_user(message):
    flag = change_user_info(message['id'], message['new_name'], message['new_email'], message['new_info'], message['new_picture'])
    if flag:
        emit('user_info_response', {'result':'Change User Info Success'})
    else:
        emit('user_info_response', {'result':'Change User Info Failure'})


################ User Info WebSocket End ################

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    socketio.run(app, port=5001, debug=True)