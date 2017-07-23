# -*- coding: utf-8 -*-

'''このモジュールでは、予約サーバを実装している。'''

import flask
from flask import request
import configparser
import json
import sqlite3
from contextlib import closing
import logging.config

# コンフィグファイルのロード
inifile = configparser.ConfigParser()
inifile.read('./config.ini')

# ログ設定ファイルのロード
logging.config.fileConfig("./logging.conf")
logger = logging.getLogger()

DATABASE = inifile.get('database', 'db_path')

# Flaskクラスのインスタンス生成
app = flask.Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    '''
    この関数は、データベースに接続する。
    :return:
    '''
    return sqlite3.connect(DATABASE)

def init_db():
    '''
    この関数は、データベースの初期化を行う。
    :return:
    '''
    with closing(connect_db()) as db:
        with app.open_resource(inifile.get('database', 'ddl_file')) as file:
            db.cursor().executescript(file.read().decode('utf-8'))
            db.commit()
        with app.open_resource(inifile.get('database', 'dml_file')) as file:
            db.cursor().executescript(file.read().decode('utf-8'))
            db.commit()

@app.route('/userRegistration/<user_id>', methods=['POST'])
def regist_userid(user_id):
    '''
    この関数は、/userRegistration/<user_id>リクエストに対する処理を行う。
    user_idをuser_id_infoテーブルに登録し、successメッセージを返す。
    :param user_id:
    :return:
    '''
    user_id_info_table = inifile.get('database', 'user_id_info_table')
    sql = 'insert into '+ user_id_info_table + '(user_id) values("' + user_id + '");'
    flask.g.db.execute(sql)
    flask.g.db.commit()
    response_body = json.dumps({"message": "success"})
    logger.info("Reserve Server Regist UserId Success " + "userId:" + user_id)
    return flask.Response(response_body, mimetype='application/json')

@app.route('/beaconInformationSend/<string:user_id>', methods=['POST'])
def beacon_information_send(user_id, visit_date, visit_time):
    '''
    この関数は、/beaconInformationSend/<user_id>リクエストに対する処理を行う。
    現在は、適当な文字列をprintし、successメッセージを返す。
    :param user_id:
    :return:
    '''
    print('beacon catch! userID:' + user_id)
    response_body = json.dumps({"message": "success"})
    logger.info("Reserve Server Beacon Information Send Success")

    # メール送信用にDB情報を取得
    user_id_info_table = inifile.get('database', 'user_id_info_table')
    reserve_info = inifile.get('database', 'reserve_info')

    # ビーコン検知日時と来訪日時を比較
    request_select_maile_send = flask.g.db.execute
    ('SELECT * ,' +
     reserve_info.start_time -  visit_time <= 2 +
     'FROM ' + user_id_info_table +
     'INNER JOIN' + reserve_info +
     'ON' + user_id_info_table.visitor_info_login_id + '=' + reserve_info.visitor_info_login_id +
     'WHERE' + user_id_info_table.visitor_info_login_id + '=' + user_id +
     'AND' + reserve_info.visit_date + '=' + visit_date
     )

    #合致するのがあった場合は、人名と予定日時を入れたメールをDBから取得してメール送信



    return flask.Response(response_body, mimetype='application/json')

@app.route('/v1/user/login', methods=['POST'])
def login_userid():
    '''
    user_idがlogin_idと紐づいていない場合、user_id_infoテーブルにlogin_idを更新する
    その後、login_idとpasswordから、来訪者のログイン処理を行う
    :param
    :return: code 0:success  1:failure
    '''

    # リクエストのBodyを取得
    request_params = json.loads(request.data.decode('utf-8'))
    user_id = request_params['userId']
    login_id = request_params['loginId']
    password = request_params['password']
    user_id_info_table = inifile.get('database', 'user_id_info_table')
    visitor_info_table = inifile.get('database', 'visitor_info_table')

    result_select_user_id = flask.g.db.execute('select * from ' + user_id_info_table + ' where visitor_info_login_id = "' + login_id + '";')

    # 初回ログインのときはユーザIDとログインIDを紐つける
    if (len(result_select_user_id.fetchall()) == 0) :
        sql2 = 'update '+ user_id_info_table + ' set visitor_info_login_id ="' + login_id + '" where user_id = "' + user_id + '";'
        flask.g.db.execute(sql2)
        flask.g.db.commit()

    # ログイン処理を実施
    result_select_login_check = flask.g.db.execute('select * from ' + visitor_info_table + ' where login_id = "' + login_id + '" and password = "' + password + '";')

    # 失敗
    if (len(result_select_login_check.fetchall()) != 1) :
        response_body = json.dumps({"code": "1"})
        logger.debug("User login failed " + "userId:" + user_id)
        return flask.Response(response_body, mimetype='application/json')

    # 成功
    response_body = json.dumps({"code": "0"})
    logger.info("User login succeess " + "userId:" + user_id)
    return flask.Response(response_body, mimetype='application/json')

@app.before_request
def before_request():
    '''
    この関数は、app.routeデコレ－タがついた関数が実行される前に自動で実行される。
    データベースへの接続を行う。
    :return:
    '''
    flask.g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    '''
    この関数は、app.routeデコレ－タがついた関数が実行された後に自動で実行される。
    データベースへの接続断を行う。
    :param exception:
    :return:
    '''
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)