import pymysql
from flask import Flask, request, render_template, redirect, url_for, make_response
from flask_cors import CORS
import os
import function
from flask import Flask
from flask import jsonify, request
import uuid
import re
import functools
from datetime import datetime
import json
from analysis import analysis

app = Flask(__name__)
# 限制域名访问
cors = CORS(app, resources={r"/.*": {"origins": ["http://8.141.50.171:9090", "http://172.16.2.190:9090", "http://127.0.0.1:5000"]}})

<<<<<<< HEAD
# 系统库连接
host = "8.141.50.171"
port = 3306
user = "root"
pwd = "zb19980329"
db = "fly_fish"

# 迁移项目请更改目录
# UPLOAD_FOLDER = '/untitled/upload'
UPLOAD_FOLDER = 'C:/Users/赵波/PycharmProjects/untitled/upload'


# 用户页面权限装饰器
def login_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        # 从cookie获取用户信息，如果有，则用户已登录，否则没有登录
        user_id = request.cookies.get('userid')
        print("cookie user_id:", user_id)
        if not user_id:
            return render_template('login.html')
        else:
            return func(*args, **kwargs)
    return inner
=======
#系统库连接
host = "127.0.0.1"
port = 3306
user = "root"
pwd = "*******"
db = "sqlup"
>>>>>>> 3be6d407a129368bf466271dc5e32ab5c3fce10d


# 过滤特殊字符
def filter_str(desstr):
    # 过滤除中英文及数字以外的其他字符
    sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", desstr)
    return sub_str

# 连接用户库函数
def con_sql_user(user_id, t_host):
    t_host = t_host.strip()
    host_con = t_host.split(' ')[0]
    db_con = t_host.split(' ')[1]
    # 连接测试函数
    sql = "select `host`,`db`,`port`,`user`,`pwd`,`encod` from sql_connect where userid = '%s' and `host`='%s' and `db`='%s'" % (
        user_id, host_con, db_con)
    sqls = sql.strip()
    print(sql, sqls)
    con_da = conn_mysql(sqls)
    print(con_da)
    # 连接用户库
    host_u = con_da[0]['host']
    port_u = con_da[0]['port']
    user_u = con_da[0]['user']
    pwd_u = con_da[0]['pwd']
    db_u = con_da[0]['db']
    conn_user = pymysql.connect(host=host_u, port=int(port_u), user=user_u, password=pwd_u, db=db_u)
    cursor_user = conn_user.cursor()
    return cursor_user


# 初始链接
def cons(conn):
    while True:
       try:
           conn.ping()
           break
       except Exception as f:
           print('连接错误',f)
           conn.ping(True)

# conn = pymysql.connect(host=host, port=port, user=user, password=pwd, db=db)
# cursor = conn.cursor()


# 函数
def list_fetchall(sql):
    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, db=db)
    cursor = conn.cursor()
    cons(conn)
    cursor.execute(sql)
    rows = cursor.fetchall()
    row = [item[0] for item in rows]
    cursor.close()
    conn.close()
    return row


def conn_mysql(sql):
    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, db=db)
    cursor = conn.cursor()
    cons(conn)
    cursor.execute(sql)
    row = cursor.description
    ob_rows = [dict(zip([col[0] for col in row],ds)) for ds in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ob_rows


def conn_exec(sql):
    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, db=db)
    cursor = conn.cursor()
    cons(conn)
    num = cursor.execute(sql)
    cursor.connection.commit()
    cursor.close()
    conn.close()
    return num


def mk_dir(path):
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False


# 页面渲染
@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/')
def hello_world():
    return render_template('login.html')


@app.route('/index')
@login_required
def index():
    # 权限
    compent = getcookie('userid')
    print(compent)
    con_list = []
    if compent is not None:
        sql = "select concat(`host`,' ',`db`) from sql_connect where userid ='%s'" % (compent)
        print(sql)
        # cons(conn)
        con_list = conn_mysql(sql)
    print(con_list)
    try:
        if len(compent) != 36:
            return render_template("login.html")
        else:
            return render_template("index.html", con_list=con_list)
    except Exception:
        if compent == 'None':
            return render_template("login.html")
        else:
            return render_template("index.html", con_list=con_list)


@app.route('/colection')
@login_required
def colection():
    return render_template('colection.html')


@app.route('/data_view')
def data_view():
    return render_template('data_view.html')


@app.route('/import_sql')
@login_required
def import_sql():
    # 权限
    compent = getcookie('userid')
    print(compent)
    con_list1 = []
    if compent is not None:
        sql = "select concat(`host`,' ',`db`) from sql_connect where userid ='%s'" % (compent)
        print(sql)
        # cons(conn)
        con_list1 = conn_mysql(sql)
    print(con_list1)
    try:
        if len(compent) != 36:
            return render_template("login.html")
        else:
            return render_template("import_sql.html", con_list1=con_list1)
    except Exception:
        if compent == 'None':
            return render_template("login.html")
        else:
            return render_template("import_sql.html", con_list1=con_list1)


@app.route('/operation')
@login_required
def operation():
    # 权限
    compent = getcookie('userid')
    # compent = compent.strip()
    print(compent)
    con_list1 = []
    if compent is not None:
        sql = "select concat(`host`,' ',`db`) as `con`,concat('x',`id`) as `ID` from sql_connect where userid ='%s'" % (compent)
        print(sql)
        con_list1 = conn_mysql(sql)
    con_list = [item['con'] for item in con_list1]
    print(con_list1, con_list)
    try:
        if len(compent) != 36:
            return render_template("login.html")
        else:
            return render_template("operation.html", con_list1=con_list1, con_list=con_list)
    except Exception:
        if compent == 'None':
            return render_template("login.html")
        else:
            return render_template("operation.html", con_list1=con_list1, con_list=con_list)


@app.route('/usercenter')
@login_required
def usercenter():
    userid = str(getcookie('userid'))
    last_ip = request.remote_addr
    print(userid)
    if userid == 'None':
        return render_template('login.html')
    sql = "select `username`,`addr`,`birthday`,`constellation`,`age` from `user` where `userid` = '%s'"%(userid)
    user_data = conn_mysql(sql)
    user_data[0]['last_ip'] = last_ip
    user_data[0]['date_time'] = str(datetime.now()).split('.')[0]
    print(user_data)
    return render_template('usercenter.html', user_data=user_data)


@app.route('/super_table')
@login_required
def super_table():
    # return render_template('super_table.html')
    t_name = request.cookies.get('t_name')
    t_host = request.cookies.get('t_host')
    print(t_name, t_host)
    resp = make_response()
    if t_name is not None:
        # 取出cookie
        user_id = str(getcookie('userid'))

        cursor_user = con_sql_user(user_id, t_host)

        sql_table_data = "select * from `%s`" % t_name
        table_data = function.conn_fetchall(sql_table_data, cursor_user)

        cursor_user.close()

        print(table_data)
        temp = render_template('super_table.html', table_data=table_data)
    else:
        temp = render_template('super_table.html', table_data=[{"": ""}])
    resp = make_response(temp, 200)
    return resp


# super_table 服务端模式
@app.route('/table_serve', methods=['GET','POST'])
def table_serve():
    t_name = request.cookies.get('t_name')
    t_host = request.cookies.get('t_host')
    print(t_name, t_host)
    # 取出cookie
    user_id = str(getcookie('userid'))

    cursor_user = con_sql_user(user_id, t_host)

    table_request = request.values.to_dict()
    print(table_request)

    search_dict = {}
    for key_s in table_request.keys():
        if "search_" in key_s:
            if key_s.split('_')[1] == '':
                continue
            else:
                search_dict[key_s.split('_')[1]] = table_request[key_s]
    print(search_dict)

    s_str = ""
    if search_dict != {}:
        for s_key in search_dict.keys():
            if search_dict[s_key] == "":
                continue
            s_str = s_str + "`"+s_key+"` " + "like" + " '%"+search_dict[s_key]+"%'" + " and "
        s_str = s_str[0:-5]
        print(s_str)
        # test = input('test:')
        sql_table_recor = "select count(*) from `%s` where %s" % (t_name, s_str)
        sql_table_data = "select * from `%s` where %s limit %s,%s"\
                         % (t_name, s_str, int(table_request['start']), int(table_request['length']))
    else:
        sql_table_recor = "select count(*) from `%s`" % t_name
        sql_table_data = "select * from `%s` limit %s,%s" %\
                         (t_name, int(table_request['start']), int(table_request['length']))
    print(sql_table_recor)
    print(sql_table_data)
    table_recor = function.list_fetchall(sql_table_recor, cursor_user)
    table_data = function.conn_fetchall(sql_table_data, cursor_user)

    cursor_user.close()

    response_table = {"draw": int(table_request['draw']), "recordsTotal": table_recor[0], "recordsFiltered": table_recor[0],
                      "data": table_data}
    print(response_table)
    resp = make_response(jsonify(response_table))
    return resp


# 测试
@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    last_ip = request.remote_addr
    return last_ip


# 功能模块
# 登录验证
@app.route('/login_match', methods=['POST'])
def login_match():
    mes = request.form
    username = mes['username']
    password = mes['password']
    username = filter_str(username)
    password = filter_str(password)
    print(username, password)
    # db.session.query
    # cons(conn)
    sql = "select * from `user` where username = '%s' and password = '%s'limit 1" %(username,password)
    print(sql)
    res = conn_mysql(sql)
    if res:
        userid = str(res[0]['userid'])
        isvip = str(res[0]['isvip'])
        print(userid, isvip)
        login_sql = "update `user` set `login_time` = '%s' where `userid` = '%s'" % (datetime.now(), userid)
        conn_exec(login_sql)
        return redirect(url_for('set_cookie', userid=userid))
    else:
        return render_template('login.html', htm='err')


# 注册
@app.route('/register', methods=['POST'])
def register():
    mes = request.form
    username = mes['username']
    password = mes['password']
    username = filter_str(username)
    password = filter_str(password)
    print(username, password)
    last_ip = request.remote_addr
    date = datetime.now()
    # 连接测试函数
    # cons(conn)
    sql = "select * from user where username = '%s' limit 1" %(username)
    print(sql)
    res = conn_mysql(sql)
    if res:
        return render_template('login.html', htm=2)
    else:
        #创建用户文件夹
        dirname = UPLOAD_FOLDER+'/'+username
        mk_dir(dirname)
        r_sql = "insert into `user`(`username`,`password`,`userid`,`userdir`,`last_ip`,`reg_datetime`)values('%s','%s','%s','%s','%s','%s')" %(username, password, uuid.uuid1(), dirname, last_ip, date)
        conn_exec(r_sql)
        return render_template('login.html', htm=1)


# 退出
@app.route("/signout", methods=['GET'])
def signout():
     temp = render_template('login.html')
     resp = make_response(temp, 200)
     resp.delete_cookie('userid')
     resp.delete_cookie('condb')
     return resp


# 新建userid的COOKIE
@app.route("/set_cookie/<userid>")
def set_cookie(userid):
    print(userid)
    temp = render_template('data_view.html')
    resp = make_response(temp, 200)
    '''
        设置cookie,默认有效期是临时cookie,浏览器关闭就失效
        可以通过 max_age 设置有效期， 单位是秒
    '''''
    resp.set_cookie("userid", userid)
    # return render_template('index.html')
    return resp


# 指定连接
@app.route("/con_db", methods=['POST'])
def con_db():
    condb = request.form.to_dict()
    condb = str(condb['con'])
    #
    return redirect(url_for('con_dbs', condb=condb))


# 新建condb的COOKIE
@app.route("/con_dbs/<condb>")
def con_dbs(condb):
    print(condb)
    temp = render_template('index.html')
    resp1 = make_response(temp, 200)
    '''
        设置cookie,默认有效期是临时cookie,浏览器关闭就失效
        可以通过 max_age 设置有效期， 单位是秒
    '''''
    resp1.set_cookie("condb", condb)
    return resp1


# 获取COOKIE
def getcookie(cookie_name):
    cookie_1 = request.cookies.get(cookie_name)
    print(cookie_1)
    return cookie_1

# 输入用户库
@app.route('/con_sql',methods=['POST'])
def con_sql():
    data = request.form.to_dict()
    print('  ', data['encod'])
    host1 = data['host']
    port1 = data['port']
    user1 = data['user']
    pwd1 = data['pwd']
    db1 = data['db']
    encod = data['encod']
    try:
        conn_user = pymysql.connect(host=host1, port=3306, user=user1, password=pwd1, db=db1)
        cursor_user = conn_user.cursor()
        user_id = str(getcookie('userid'))
        # 连接测试函数
        sql_in = "insert into sql_connect (`host`,`db`,`port`,`user`,`pwd`,`userid`,`encod`)values('%s','%s','%s','%s','%s','%s','%s')" % (
        host1, db1, port1, user1, pwd1, user_id,encod)
        print(sql_in)
        conn_exec(sql_in)
        conn_user.close()
        cursor_user.close()
        return jsonify({'success': 200, 'state': 't'})
    except Exception as f:
        print(f)
        return jsonify({"error": 1001, "state": "f"})


# 删除连接
@app.route("/del_con", methods=['POST'])
def del_con():
    delda = request.form.to_dict()
    delda = delda['delda']
    print(type(delda))
    del_host = delda.split(' ')[0]
    del_db = delda.split(' ')[1]
    delsql = "delete from sql_connect where `host`='%s' and `db` = '%s'" %(del_host, del_db)
    re = conn_exec(delsql)
    if re:
        return jsonify({'mes': 't'})
    else:
        return jsonify({'mes':' f'})


# 判断上传的文件是否是允许的后缀
ALLOWED_EXTENSIONS = set(['zip', 'rar', 'xls', 'xlsx', 'csv'])


def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == 'GET':  # 请求方式是get
        return render_template('test.html')  # 返回模板
    else:
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files.get('file')  # 获取文件
        file_len = len(str(request.files.to_dict()['file']))
        if file_len == 46 or file_len < 46:
            return jsonify({'state': '00'})
        # sqlcon = request.form.get('con')
        # print(file,sqlcon)

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # 取出cookie
            user_id = str(getcookie('userid'))
            condb = str(getcookie('condb'))

            host_con = condb.split(' ')[0]
            try:
               db_con = condb.split(' ')[1]
            except Exception:
                return jsonify({"state": "0"})
            print('打印', user_id, condb)
            # 连接测试函数
            sql = "select `host`,`db`,`port`,`user`,`pwd`,`encod` from sql_connect where userid = '%s' and `host`='%s' and `db`='%s'" %(user_id, host_con,db_con)
            sql_dir = "select `userdir` from user where userid = '%s'" % user_id
            print(sql, sql_dir)
            con_da = conn_mysql(sql)
            print(con_da)
            userdir_da = conn_mysql(sql_dir)
            userdir = userdir_da[0]['userdir']
            # 数据库编码
            encod = con_da[0]['encod']
            # 每次启动前清空文件夹
            function. rem(userdir)
            # 保存文件
            f_name = file.filename
            f1_name = os.path.join(userdir, f_name)
            file.save(f1_name)  # 保存文件

            # 连接用户库
            a_path = userdir  # 用户上传目录
            host_u = con_da[0]['host']
            port_u = con_da[0]['port']
            user_u = con_da[0]['user']
            pwd_u = con_da[0]['pwd']
            db_u = con_da[0]['db']
            conn_user = pymysql.connect(host=host_u, port=int(port_u), user=user_u, password=pwd_u, db=db_u)
            cursor_user = conn_user.cursor()

            res = function.ruku(a_path, cursor_user,encod)

            if res:
                return jsonify({'success': 200, 'state': 't'})
            else:
                return jsonify({'success': 200, 'state': 'f'})
        else:
            return jsonify({'success': 200, 'state': 'F'})


# 数据库管理器
@app.route("/sql_manager", methods=['GET', 'POST'])
def sql_manager():
    if request.form.get('api') == 'no_table':
        condb = request.form.get('t_host')
    else:
        # 取出cookie
        condb = str(getcookie('condb'))
    sql_statement = request.form.get('sqls')
    user_id = str(getcookie('userid'))
    cursor_user = con_sql_user(user_id, condb)
    if sql_statement[0:6] == 'select':
        try:
            res_sqldata = function.conn_fetchall(sql_statement, cursor_user)
        except Exception as f:
            res_sqldata = str(f)
    else:
        try:
            res_sqldata = function.conn_exec(sql_statement, cursor_user)
        except Exception as fi:
            res_sqldata = str(fi)
    cursor_user.close()
    return jsonify({"res_sqldata": res_sqldata})


# 数据库管理显示table
@app.route("/show_tables", methods=['GET', 'POST'])
def show_tables():
    # 取出cookie
    user_id = str(getcookie('userid'))
    condb = request.form.get('con')
    cursor_user = con_sql_user(user_id, condb)
    res_table = function.list_fetchall("show tables;", cursor_user)
    cursor_user.close()
    return jsonify({"res_table": res_table})


# 字段合并
@app.route("/combine_field", methods=['POST'])
def combine_field():
    # 取出cookie
    user_id = str(getcookie('userid'))
    condb = str(getcookie('condb'))

    cursor_user = con_sql_user(user_id, condb)

    p_sql = "select table_name from information_schema.tables where table_schema='"+db+"' and (table_name = '交易明细' or table_name = '账户信息')"
    print(p_sql)
    p_data = function.list_fetchall(p_sql,cursor_user)
    print(p_data)
    if len(p_data) == 2:

        # 更新 账户信息  去掉_156_1 去掉金额的-
        up_sq = "update 账户信息 set 交易卡号 = substring_index(`交易卡号`,'_',1)"
        up_sq1 = "update `交易明细` set `交易金额`= replace(`交易金额`,'-','')"
        function.conn_exec(up_sq, cursor_user)
        function.conn_exec(up_sq1, cursor_user)

        up_sql1 = "update `交易明细` A left join `账户信息` B on A.`交易卡号`=B.`交易卡号`set A.`交易户名`" \
                  "=B.`账户开户名称`,A.`交易证件号码`=B.`开户人证件号码`"
        print('执行中........')
        function.conn_exec(up_sql1,cursor_user)
        print('更新完成')
    else:
        print('请先完成整合（combine）')
        return jsonify({"state": "1"})
    cursor_user.close()
    return jsonify({"state": "2"})


# 获取表字段
@app.route('/field_list', methods=['POST'])
def field_list():
    # 用户表
    user_id = str(getcookie('userid'))
    condb = str(getcookie('condb'))

    cursor_user = con_sql_user(user_id, condb)

    sql_field = "select CONCAT(COLUMN_NAME) from information_schema.COLUMNS where table_name = '分析总表'"
    field_li = function.list_fetchall(sql_field, cursor_user)
    return jsonify({'field_list': field_li})


# 整合表
@app.route('/table_combine', methods=['POST'])
def combine():
    table_combine = request.form.to_dict()['combine_tablename']
    print(table_combine)
    # 获取用户连接
    user_id = str(getcookie('userid'))
    condb = str(getcookie('condb'))

    cursor_user = con_sql_user(user_id, condb)

    condb = condb.strip()
    try:
        db_con = condb.split(' ')[1]
    except Exception as f1:
        return jsonify({"field_list": "0"})

    # 整合表
    zheng_sql = "select table_name from information_schema.tables where table_schema='"+db_con+"' and table_name like '%"+table_combine+"%'"
    print(zheng_sql)
    jy_ta = function.list_fetchall(zheng_sql, cursor_user)
    print(jy_ta)
    if jy_ta == []:
        print('没有相关信息表')
        return jsonify({"field_list":"1"})
    for j_table in jy_ta:
        if '子' in j_table:
            de = jy_ta.index(j_table)
            del jy_ta[de]
    print(jy_ta)
    # 创建新表
    main_tab = jy_ta[0]
    main_table = table_combine
    create_tab = "create table `%s` select * from `%s`" % (table_combine, main_tab)
    function.conn_exec(create_tab,cursor_user)
    cols_sql = "select column_name from INFORMATION_SCHEMA.Columns where table_name='%s'"%(main_table)
    cols = function.list_fetchall(cols_sql, cursor_user)
    print(cols)
    del cols[0]
    cols = str(cols)
    cols = cols.replace('[', '')
    cols = cols.replace(']', '')
    cols = cols.replace("'", "`")
    print(cols)
    for j_table in jy_ta[1:]:
        insert_sql = "insert into `%s` (%s) select %s from `%s` "%(main_table, cols, cols, j_table)
        print(insert_sql)
        if j_table == table_combine:
            continue
        function.conn_exec(insert_sql, cursor_user)
    return jsonify({"field_list": "2"})


# 银行流水分析
@app.route("/analysis", methods=['GET', 'POST'])
def analysis():
    analysis_field = request.form.to_dict()
    print(analysis_field)
    table_name = analysis_field['table_name']
    main_name = analysis_field['main_name']
    main_card = analysis_field['main_card']
    to_name = analysis_field['to_name']
    to_card = analysis_field['to_card']
    sign = analysis_field['sign']
    money = analysis_field['money']
    abstract = analysis_field['abstract']

    # 取出cookie
    user_id = str(getcookie('userid'))
    condb = str(getcookie('condb'))

    cursor_user = con_sql_user(user_id, condb)

    analysis_data = function.analysis(cursor_user, table_name, main_name, main_card, to_name, to_card, sign, money, abstract, 20)
    analysis_res_data = function.conn_fetchall("select * from `分析结果表`", cursor_user)
    cursor_user.close()
    return jsonify({"analysis_res_data": analysis_res_data})


# 创建super_table页面cookie
@app.route('/op_to_super', methods=['POST'])
def op_to_super():
    form_table_data = request.form.to_dict()
    t_host = form_table_data['host']
    t_name = form_table_data['name']
    response = make_response(jsonify({"code": 200, "data": "null", "msg": "null"}))
    response.set_cookie('t_host', t_host)
    response.set_cookie('t_name', t_name)
    return response


# 数据可视化
# 地图数据
@app.route("/location_map", methods=['GET', 'POST'])
def location_map():
    sql = "select `地理坐标` from `人员住址信息` where `地理坐标` is not null limit 200"
    # cons(conn)
    location_da = list_fetchall(sql)
    return jsonify({"lo_da":location_da})


if __name__ == '__main__':
    app.run()
