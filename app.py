from argparse import Namespace
from mailbox import mboxMessage
from socket import socket
# from tkinter.font import names
from flask import Flask
from flask_socketio import SocketIO, emit
from views import test
import config
from modules.post_info import post_info, db
from modules.post_info import add_post_info, search_post_info, delete_post_info, change_post_info


app = Flask(__name__)
# register blueprint
app.register_blueprint(test.test)
app.register_blueprint(post_info)
# load config file
app.config.from_object(config)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def test():
    return "Hello World!"

@socketio.on('Add Post Info', namespace='/post')
def new_post(message):
    print("test")
    flag = add_post_info(message['headline'], message['tags'], message['info'], message['picture'])
    if flag:
        emit('post_info_response', {'result':'Post Success'})
    else:
        emit('post_info_response', {'result':'Post Failure'})



@socketio.on('Search Post Info', namespace='/home') # list应该也有
def show_post(message):
    res = search_post_info(tags=message['tags'])
    ret = []
    flag = True # TODOLIST: 判断是否还有下一个page
    for per in res:
        ret.append((per.id, per.picture))
        if len(ret) == 15:
            break
    emit('post_info_response', {'result': 'Search Success', 'lst': ret, 'page_id': 1, 'first_page': True, 'last_page': flag})


@socketio.on('Open Post Info', namespace='/list')
def open_post(message):
    res = search_post_info(id=message['id'])
    if res == []:
        print('No such id!')
        emit('post_info_response', {'result':'Open Post Failure', 'id':None, 'headline':None, 'tags':None, 'info':None, 'picture':None})
    elif len(res) > 1:
        print('Same id for post info!')
        emit('post_info_response', {'result':'Open Post Failure', 'id':None, 'headline':None, 'tags':None, 'info':None, 'picture':None})
    else:
        res = res[0] # 肯定只有一个
        emit('post_info_response', {'result':'Open Post Success', 'id': res.id, 'headline': res.headline, 'tags': res.tags, 'info': res.info, 'picture': res.picture})


@socketio.on('Search for Next Page', namespace='/list')
def change_page(message):
    ret = []
    emit('post_info_response', {'result': 'Change Page Success', 'lst': ret})
    
#新增用户信息
@socketio.on('Add User Info', namespace='/user_list')
def new_user(message):
    flag = add_user_info(message['id'], message['name'], message['email'], message['info'], message['picture_url'])
    if flag:
        emit('user_info_response', {'result':'Add User Info Success'})
    else:
        emit('user_info_response', {'result':'Add User Info Failure'})

#查询用户信息
@socketio.on('Search User Info', namespace='/user_list')
def show_user_info(message):
    res = search_user_info(id=message['id'])
    res.append()
    emit('user_info_response', {'result': 'Search Success'})

#修改用户信息
@socketio.on('Change User Info', namespace='/user_list')
def change_user_info(message):
    flag = change_user_info(id=message['id'],name=message["name"],email=message["email"],info=message["info"],picture_url=message["picture_url"])
    if flag:
        emit('user_info_response', {'result':'Change User Info Success'})
    else:
        emit('user_info_response', {'result':'Change User Info Failure'})

#删除用户信息
@socketio.on('Delete User Info', namespace='/user_list')
def delete_user(message):
    flag = delete_user_info(id=message["id"])
    if flag:
      emit('user_info_response', {'result': 'Delete User Info Success'})
    else:
      emit('user_info_response', {'result': 'Delete User Info Failure'})

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    socketio.run(app, port=5001, debug=True)
