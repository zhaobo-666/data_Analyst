from chardet.universaldetector import UniversalDetector
import codecs
import csv
import zipfile
import pymysql
import shutil
# import rarfile
# from unrar import rarfile
import tarfile
import os
import json
import re
import pandas as pd


def json_read():
    with open('connect.json', 'r',encoding='utf8') as f:
        cons_json = f.read()
        cons = json.loads(cons_json)
        return cons
def cons(numb):
    cons_message = json_read()
    # 连接
    host = cons_message[numb]['host']
    user = cons_message[numb]['user']
    pwd = cons_message[numb]['passwd']
    db = cons_message[numb]['dbname']
    port = cons_message[numb]['port']
    return host, user, pwd, db, port

def db_look(msg,host,port,user,pwd,db):
  print(msg,"host:"+host, "port:"+port, "user:"+user, "pwd:"+pwd, "db:"+db)


def conn_local(sql,cursor_user_local):
    cursor_user_local.execute('set names utf8')
    cursor_user_local.execute('set character_set_connection=utf8')
    row = cursor_user_local.execute(sql)
    cursor_user_local.connection.commit()
    return row

def list_fetchall(sql,cursor_user):
    # cursor_user.execute('set names utf8')
    # cursor_user.execute('set character_set_connection=utf8')
    cursor_user.execute(sql)
    rows = cursor_user.fetchall()
    row = [item[0] for item in rows]
    # return list(rows)
    return row

def conn_fetchall(sql,cursor_user):
    cursor_user.execute(sql)
    desc = cursor_user.description
    ob_dict = [dict(zip([col[0] for col in desc],row)) for row in cursor_user.fetchall()]
    return ob_dict

def conn_fetchone(sql,cursor_user):
    cursor_user.execute('set names utf8')
    cursor_user.execute('set character_set_connection=utf8')
    cursor_user.execute(sql)
    rows = cursor_user.fetchone()
    return list(rows)

def conn_fetchmany(sql,cursor_user):
    cursor_user.execute('set names utf8')
    cursor_user.execute('set character_set_connection=utf8')
    cursor_user.execute(sql)
    rows = cursor_user.fetchmany(3)
    row = [item[0] for item in rows]
    return row

def conn_exec(sql,cursor_user):
    num = cursor_user.execute(sql)
    cursor_user.connection.commit()
    return num

def conn_executemany(sqls,args,cursor_user):
    cursor_user.execute('set names utf8')
    cursor_user.execute('set character_set_connection=utf8')
    num = cursor_user.executemany(sqls,args)
    cursor_user.connection.commit()
    return num


def get_encode_info(file):
    with open(file, 'rb') as f:
        detector = UniversalDetector()
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        return detector.result['encoding']


def read_file(file):
    with open(file, 'rb') as f:
        return f.read()


def write_file(content, file):
    with open(file, 'wb') as f:
        f.write(content)


def convert_encode2utf8(file, original_encode, des_encode):
    file_content = read_file(file)
    file_decode = file_content.decode(original_encode, 'ignore')
    file_encode = file_decode.encode(des_encode)
    write_file(file_encode, file)

def WriteFile(filePath,u,encoding="gbk"):
        with codecs.open(filePath, "wb") as f:
            f.write(u.encode(encoding, errors="ignore"))


#入库
def ruku(a_path,cursor_user,encod):
    sr = a_path
    des = a_path
    for z in os.listdir(sr):
        z_name = sr + '/' + z
        print(z_name)
        if os.path.isdir(z_name):
            pass
        else:
            uncompress(z_name, des)
    an_garcode(a_path)

    file_path = a_path
    shu = 0
    for root, dirs, files in os.walk(file_path):
        for name in files:
            shu = shu+1
            ft = name.split('.')[-1]
            if ft == 'rar' or ft == 'zip' or ft == 'unziped':  # 检查后缀名是rar  或  zip  跳过
                continue
            else:
                filename = os.path.join(root, name)
                filename = filename.replace('\\', '/')
                dirname = file_path.split('/')[-1]
                tablename = dirname + filename.split(dirname)[1]
                tablename = tablename[0:-4]
                if ' ' in tablename:
                    tablename = tablename.replace(' ', '')
                if '.' in tablename:
                    tablename = tablename.replace('.', '')
                print(tablename, filename)
                if encod=='GB18030' and ft == 'csv':
                    gb18030(filename=filename, tablename=tablename, cursor_user=cursor_user)
                elif ft == 'xls' or ft == 'xlsx':
                    ex_da = Excel(file_path,name,cursor_user)
                    ex_da.create_tab()
                else:
                    utf8_csv(filename=filename, tablename=tablename, cursor_user=cursor_user)
    rem(file_path)
    return True

#excel入库
class Excel(object):
    def __init__(self,da_path,file_name,cursor_user):
        self.path = da_path
        self.filename = file_name
        self.cursor_user = cursor_user
        self.file_path = self.path+'/'+self.filename

    def create_tab(self):
        with open(self.file_path, 'rb') as f:
            sheets = pd.read_excel(f, sheet_name=None, keep_default_na=False)
            for sheet in sheets.keys():
                excel_sheet_data = pd.read_excel(self.file_path, sheet_name=sheet, keep_default_na=False)
                print('行数是',excel_sheet_data.shape[0])
                column_field = ''
                # 读取excel获取每个表的列名
                for column in excel_sheet_data:
                    column_field = column_field + '`'+column+'`'+' '+'varchar(255),'
                column_field = column_field[:-1]
                column_insert = column_field.replace(' varchar(255)','')
                create_tab_sql = "create table if not exists `%s`(%s) DEFAULT CHARSET=utf8"%(self.filename.split('.')[0]+'/'+sheet,column_field)
                print(create_tab_sql)
                conn_exec(create_tab_sql,self.cursor_user)
                #获取行数超过10000拼接insert
                in_val_row = ""
                for index,row in excel_sheet_data.iterrows():
                    in_val_field = ""
                    for column in excel_sheet_data:
                         in_val_field = in_val_field+"'"+str(row[column])+"',"
                    in_val_field = in_val_field[:-1]
                    in_val_field = in_val_field.replace('(','（')
                    in_val_field = in_val_field.replace(')', '）')
                    in_val_field = in_val_field.replace('\\t', '')
                    in_val_row = in_val_row + "("+in_val_field+"),"
                in_val_row = in_val_row[:-1]
                if excel_sheet_data.shape[0] > 10000:
                    in_val_row = re.findall(r"[\(][^\)]+[\)]", in_val_row, re.S)
                    yu = len(in_val_row) // 10000 + 1
                    ri = 1
                    for i in range(yu):
                        if ri <= yu:
                            st = in_val_row[ri * 10000 - 10000:ri * 10000]
                        else:
                            st = in_val_row[10000 * (ri - 1):]
                        ri += 1
                        print(st)
                        st = str(st)
                        print(st)
                        st = st.replace('[', '')
                        st = st.replace(']', '')
                        st = st.replace('"', '')
                        print(st)
                        insert_sql = "insert into `%s` (%s)values %s" % (self.filename.split('.')[0] + '/' + sheet, column_insert, st)
                        print(insert_sql)
                        res = conn_exec(insert_sql,self.cursor_user)
                else:
                     insert_sql = "insert into `%s` (%s)values %s" % (self.filename.split('.')[0] + '/' + sheet, column_insert, in_val_row)
                     print(insert_sql)
                     res = conn_exec(insert_sql,self.cursor_user)
        return res


# GB18030 入库
def gb18030(filename,tablename,cursor_user):
    file = csv.reader(open(filename, 'r', encoding='gb18030', errors='ignore'))
    cols = next(file)
    column = ''
    columns = ''
    for col in cols:
        if '(' in col:
            col = col.replace('(', '')
        if ')' in col:
            col = col.replace(')', '')
        if '	' in col:
            col = col.replace('	', '')
        if '"' in col:
            col = col.replace('"', '')
        if "'" in col:
            col = col.replace("'", "")
        column = column + '`' + col + '`' + ' ' + 'varchar(255)' + ','
        columns = columns + '`' + col + '`' + ','
    column = column[0:-1]
    # columns = columns[0:-1]
    table = 'create table if not exists ' + '`' + tablename + '`' + ' ' + '('+ '`序号ID` int(50) primary key not null auto_increment,' + column +',`路径` varchar(255)' + ')' + ' DEFAULT CHARSET=gb18030'
    #table = 'create table if not exists `%s` (`序号ID` int(50) primary key not null auto_increment,%s,`路径` varchar(255)) DEFAULT CHARSET=gb18030' %(tablename,column)
    print(table)
    conn_exec(table,cursor_user)

    table_da = ''
    for row in file:
        table_data = row
        table_data = str(table_data)
        table_data = table_data.replace('(','（')
        table_data = table_data.replace(')', '）')
        table_data = table_data.replace('[', '')
        table_data = table_data.replace(']', '')
        table_data = table_data.replace('\\t', '')
        table_data = table_data+","+"'"+filename+"'"
        table_data = '(' + table_data + ')' + ','

        table_da = table_da + table_data
    table_da = table_da[0:-1]
    if table_da.count(')')>15000:
        table_da = re.findall(r"[\(][^\)]+[\)]", table_da, re.S)
        yu = len(table_da)//10000+1
        ri = 1
        for i in range(yu):
           if ri <= yu:
               st = table_da[ri * 10000 - 10000:ri * 10000]
           else:
               st = table_da[10000 * (ri - 1):]
           ri += 1
           print(st)
           st = str(st)
           print(st)
           st = st.replace('[', '')
           st = st.replace(']', '')
           st = st.replace('"', '')
           print(st)
           insert_sql = "insert  into " + ' ' + '`' + tablename + '`' + ' ' + '(' + columns + '`' + '路径' + '`' + ')' + 'values' + st + ';'
           #insert_sql = 'insert  into `%s` (%s `路径`)values %s;' %(tablename,columns,st)
           print(insert_sql)
           conn_exec(insert_sql, cursor_user)
    else:
        insert_sql = "insert  into " + ' ' + '`' + tablename + '`' + ' ' + '(' + columns+'`'+'路径'+'`' + ')' + 'values' + table_da + ';'
        #insert_sql = "insert  into `tablename`(columns `路径`)values table_da ;"%(tablename,columns,table_da)
        print(insert_sql)
        conn_exec(insert_sql,cursor_user)
    print('数据入库成功')


#进度函数
def jindu(a_path):
    shu = 0
    for root, dirs, files in os.walk(a_path):
        for name in files:
            shu =shu+1
    return shu


#load 入库

def load_gb (filename,tablename):
    file = csv.reader(open(filename, 'r', encoding='gb18030', errors='ignore'))
    cols = next(file)
    column = ''
    columns = ''
    for col in cols:
        if '(' in col:
            col = col.replace('(', '')
        if ')' in col:
            col = col.replace(')', '')
        if '	' in col:
            col = col.replace('	', '')
        if '"' in col:
            col = col.replace('"', '')
        if "'" in col:
            col = col.replace("'", "")
        column = column + '`' + col + '`' + ' ' + 'varchar(255)' + ','
        columns = columns + '`' + col + '`' + ','
    column = column[0:-1]
    columns = columns[0:-1]
    if '(' in tablename:
        tablename = tablename.replace('(', '')
    if ')' in tablename:
        tablename = tablename.replace(')', '')
    # table = 'create table if not exists ' + '`' + tablename + '`' + ' ' + '(' + column + ')' + ' DEFAULT CHARSET=gb18030'
    table = 'create table if not exists ' + '`' + tablename + '`' + ' ' + '(' + '`序号ID` int(50) primary key not null auto_increment,' + column + ',`路径` varchar(255)' + ')' + ' DEFAULT CHARSET=gb18030'
    conn_local(table)
    print(table)
    data = "load data local infile'" + filename + "'" + "into table" + ' '  + tablename + ' ' + "character set gb18030 fields  enclosed by '\"' terminated by ','"  "lines terminated by '\\n' ignore 1 lines ; "
    upsql = "update"+" "+"`"+tablename+"`"+" "+ "set" +"`路径` = "+"'"+filename+"'"
    print(data)
    conn_local(data)
    print(upsql)
    conn_local(upsql)
    print('数据入库成功')

# utf_8 入库
def utf8_csv(filename,tablename,cursor_user):

    #恶心的编码
    file_name = filename
    file_content = read_file(file_name)
    encode_info = get_encode_info(file_name)
    if encode_info != 'utf-8':
        convert_encode2utf8(file_name, encode_info, 'utf-8')
    encode_info = get_encode_info(file_name)
    #恶心的编码

    file = csv.reader(open(filename, 'r', encoding='utf-8', errors='ignore'))
    cols = next(file)
    column = ''
    columns = ''
    for col in cols:
        if '(' in col:
            col = col.replace('(', '')
        if ')' in col:
            col = col.replace(')', '')
        if '	' in col:
            col = col.replace('	', '')
        if '"' in col:
            col = col.replace('"', '')
        if "'" in col:
            col = col.replace("'", "")
        column = column + '`' + col + '`' + ' ' + 'varchar(255)' + ','
        columns = columns + '`' + col + '`' + ','
    column = column[0:-1]
    # columns = columns[0:-1]
    table = 'create table if not exists ' + '`' + tablename + '`' + ' ' + '('+ '`序号ID` int(50) primary key not null auto_increment,' + column +',`路径` varchar(255)' + ')' + ' DEFAULT CHARSET=utf8'
    print(table)
    conn_exec(table,cursor_user)


    table_da = ''
    for row in file:
        table_data = row
        table_data = str(table_data)
        table_data = table_data.replace('(', '（')
        table_data = table_data.replace(')', '）')
        table_data = table_data.replace('[', '')
        table_data = table_data.replace(']', '')
        table_data = table_data.replace('\\t', '')
        table_data = table_data+","+"'"+filename+"'"
        table_data = '(' + table_data + ')' + ','

        table_da = table_da + table_data
    # print(table_da)
    table_da = table_da[0:-1]
    # 万级数据入库
    if table_da.count(')') > 15000:
        table_da = re.findall(r"[\(][^\)]+[\)]", table_da, re.S)
        tiaoshu = 10000
        yu = len(table_da) // tiaoshu + 1
        ri = 1
        for i in range(yu):
            if ri <= yu:
                st = table_da[ri * tiaoshu - tiaoshu:ri * tiaoshu]
            else:
                st = table_da[tiaoshu * (ri - 1):]
            ri += 1
            print(st)
            st = str(st)
            print(st)
            st = st.replace('[', '')
            st = st.replace(']', '')
            st = st.replace('"', '')
            print(st)
            insert_sql = "insert  into " + ' ' + '`' + tablename + '`' + ' ' + '(' + columns + '`' + '路径' + '`' + ')' + 'values' + st + ';'
            # insert_sql = 'insert  into `%s` (%s `路径`)values %s;' %(tablename,columns,st)
            print(insert_sql)
            conn_exec(insert_sql, cursor_user)
    else:
        insert_sql = "insert  into " + ' ' + '`' + tablename + '`' + ' ' + '(' + columns + '`' + '路径' + '`' + ')' + 'values' + table_da + ';'
        # insert_sql = "insert  into `tablename`(columns `路径`)values table_da ;"%(tablename,columns,table_da)
        print(insert_sql)
        conn_exec(insert_sql, cursor_user)
    print('数据入库成功')



# 解压
def uncompress(src_file,dest_dir):
    """
    :param src_file: 你要解压的文件
    :param dest_dir: 你要解压的路径
    :return:
    """
    file_name,file_type = os.path.splitext(src_file)  #获取文件后缀名
    #print(file_type)
    try:
        if file_type == '.zip':
            fz = zipfile.ZipFile(src_file, 'r')
            for file in fz.namelist():
                # print(file)
                fz.extract(file, dest_dir)
            fz.close()
            newname = file_name + '.unziped'
            os.rename(src_file,newname)
        #
        # elif file_type == '.rar':
        #     rar = rarfile.RarFile(src_file)#创建rar实例对象 包含数据
        #     rar.extractall(dest_dir)
        #     rar.close
        else:
            tar = tarfile.open(fileobj=src_file)
            for name in tar.getnames():
                tar.extract(name,dest_dir)
            tar.close()
    except Exception as ex:
       return False
    return True

#修改乱码文件
def an_garcode(dir_names):
    """anti garbled code"""
    os.chdir(dir_names)


    for temp_name in os.listdir('.'):
        try:
            #使用cp437对文件名进行解码还原
            new_name = temp_name.encode('cp437')
            #win下一般使用的是gbk编码
            new_name = new_name.decode("gbk")
            #对乱码的文件名及文件夹名进行重命名
            os.rename(temp_name, new_name)
            #传回重新编码的文件名给原文件名
            temp_name = new_name
        except:
            #如果已被正确识别为utf8编码时则不需再编码
            pass


        if os.path.isdir(temp_name):
            #对子文件夹进行递归调用
            an_garcode(temp_name)
            #记得返回上级目录
            os.chdir('..')


def rem(a_path):
    sr = a_path
    for z in os.listdir(sr):
        f_na = os.path.splitext(z)
        # if f_na[1] == '.zip' or f_na[1] == '.unziped' or f_na[1] == '.rar':
        #     continue
        z_name = sr + '/' + z
        print(z_name)
        if os.path.isdir(z_name):
            for fi in os.listdir(z_name):
                fipath = os.path.join(z_name,fi)
                if os.path.isfile(fipath):
                    os.remove(fipath)
                    print(fipath,'已经删除')
                elif os.path.isdir(fipath):
                    shutil.rmtree(fipath,True)
                    print("Directory: "+fipath+"已经删除")
            os.removedirs(z_name)
        else:
            os.remove(z_name)





table_res = "分析结果表"
def analysis(cursor_user, table_name, main_name, main_card, to_name, to_card, sign, money, abstract, limit_number):
    # 创建卡号级别表
    create_card_level = "create table if not exists 卡号级别表 (`卡号` varchar(255),`级别` varchar(255))"
    print(create_card_level)
    conn_exec(create_card_level,cursor_user)
    sql_1 = "select  `%s` from `%s`group by `%s`" % (main_card, table_name, main_card)
    cards = list_fetchall(sql_1,cursor_user)
    cards_2 = []
    for card in cards:
        # 插入级别表
        card_level_sql_1 = "insert into `卡号级别表`(`卡号`,`级别`)values('%s','%s')" % (card, '一级卡号')
        print(card_level_sql_1)
        conn_exec(card_level_sql_1,cursor_user)
        # 查询下级卡号
        sql_2 = "select `%s` from `%s` where `%s`='%s' and (`%s`= '借' or  `%s`= '出') group by `%s`" % (
        to_card, table_name, main_card, card, sign, sign, to_card)
        print(sql_2)
        cards_t_2 = list_fetchall(sql_2,cursor_user)
        cards_2.extend(cards_t_2)
    cards_3 = []
    for card_2 in cards_2:
        # 判断是否是已经调取的卡号
        if card_2 in cards:
            continue
        # 插入级别表
        card_level_sql_2 = "insert into `卡号级别表`(`卡号`,`级别`)values('%s','%s')" % (card_2, '二级卡号')
        print(card_level_sql_2)
        conn_exec(card_level_sql_2,cursor_user)
        # 查询下级卡号
        sql_3 = "select `%s` from `%s` where `%s`='%s'and (`%s`= '借' or  `%s`= '出') group by `%s`" % (
        to_card, table_name, main_card, card_2, sign, sign, to_card)
        print(sql_3)
        cards_t_3 = list_fetchall(sql_3,cursor_user)
        cards_3.extend(cards_t_3)
    cards_4 = []
    for card_3 in cards_3:
        # 判断是否是已经调取的卡号
        if card_3 in cards or card_3 in cards_2:
            continue
        # 插入级别表
        card_level_sql_3 = "insert into `卡号级别表`(`卡号`,`级别`)values('%s','%s')" % (card_3, '三级卡号')
        print(card_level_sql_3)
        conn_exec(card_level_sql_3,cursor_user)
        # 查询下级卡号
        sql_4 = "select `%s` from `%s` where `%s`='%s'and (`%s`= '借' or  `%s`= '出') group by `%s`" % (
            to_card, table_name, main_card, card_3, sign, sign, to_card)
        print(sql_4)
        cards_t_4 = list_fetchall(sql_4,cursor_user)
        cards_4.extend(cards_t_4)

    # 创建分析结果表
    create_res_tab = "create table if not exists 分析结果表 (`户名` varchar(255) DEFAULT NULL,`卡号`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`交易金额`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`标志`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`分析原因`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`账户级别`" \
                     " varchar(255) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8"
    print(create_res_tab)
    conn_exec(create_res_tab,cursor_user)

    # 查询提现
    sql_cash = " select `%s`,`%s`,sum(`%s`) as `交易总额`,'现金提现' as `分析原因` from `%s`" \
               " where `%s`>10000 and(`%s` like '提现' or `%s` like '现金' or `%s` like '取款' or %s !='其他')" \
               % (main_name, main_card, money, table_name, money, abstract, abstract, abstract, sign)
    print(sql_cash)
    cash_data = conn_fetchall(sql_cash,cursor_user)
    for cash_da in cash_data:
        cash_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                      "('%s','%s','%s','%s')" % (
                      table_res, cash_da[main_name], cash_da[main_card], cash_da['交易总额'], cash_da['分析原因'])
        print(cash_insert)
        conn_exec(cash_insert,cursor_user)

    # 打给公司
    sql_company = "select `%s`,`%s`,sum(`%s`) as `交易总额`,'打给公司' as `分析原因` from" \
                  " `%s`where char_length(`%s`)>4 and `%s`>10000 group by `%s`" % (
                  main_name, main_card, money, table_name, to_name, money, main_card)
    print(sql_company)
    company_data = conn_fetchall(sql_company,cursor_user)
    for company_da in company_data:
        company_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                         "('%s','%s','%s','%s')" % (
                         table_res, company_da[main_name], company_da[main_card], company_da['交易总额'],
                         company_da['分析原因'])
        print(company_insert)
        conn_exec(company_insert,cursor_user)

    # 交叉账户
    sql_max_money = "select ToUser,ToCard,round(sum(sum)/10000,0) as `交易总额`,'交叉账户' as `分析原因`,count(*) as count from " \
                    "(select `%s` as `FromUser`,`%s` as FromCard,`%s` as ToUser,`%s`" \
                    " as ToCard, `%s` as Direction,count(*) as count,sum(`%s`) as sum from %s" \
                    " group by `%s`,`%s`,`%s`,`%s`,`%s`) A group by ToUser,ToCard having count(*)>=3 limit %d" \
                    % (main_name, main_card, to_name, to_card, sign, money, table_name, main_name, main_card, to_name,
                       to_card, sign, limit_number)
    print(sql_max_money)
    max_money_data = conn_fetchall(sql_max_money,cursor_user)
    for max_money_da in max_money_data:
        max_money_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                           "('%s','%s','%s','%s')" % (
                           table_res, max_money_da['ToUser'], max_money_da['ToCard'], max_money_da['交易总额'],
                           max_money_da['分析原因'])
        print(max_money_insert)
        conn_exec(max_money_insert,cursor_user)

    # 交易金额较大
    sql_relation = "select ToUser,ToCard,round(sum(sum)/10000,0) as `交易总额`,'交易金额较大' as `分析原因`,sum(count) from " \
                   "(select `%s` as `FromUser`,`%s` as FromCard,`%s` as ToUser," \
                   "`%s` as ToCard, `%s` as Direction,count(*) as count,sum(`%s`)" \
                   " as sum from `%s` group by `%s`,`%s`,`%s`,`%s`,`%s`)" \
                   " A group by ToUser,ToCard order by round(sum(sum)/10000,0) desc limit %d" \
                   % (main_name, main_card, to_name, to_card, sign, money, table_name, main_name, main_card, to_name,
                      to_card, sign, limit_number)
    print(sql_relation)
    relation_data = conn_fetchall(sql_relation,cursor_user)
    for relation_da in relation_data:
        relation_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                          "('%s','%s','%s','%s')" % (
                          table_res, relation_da['ToUser'], relation_da['ToCard'], relation_da['交易总额'],
                          relation_da['分析原因'])
        print(relation_insert)
        conn_exec(relation_insert,cursor_user)

    return 1

if __name__ == '__main__':
    # conn_user = pymysql.connect(host='172.16.2.89', port=3306, user='root', password='zb19980329zb', db='gbtest')
    # cursor_user = conn_user.cursor()
    # ruku('C:/Users/Administrator/PycharmProjects/untitled/upload',cursor_user)
    # conn_user.close()
      print(jindu('templates'))

    #uncompress('upload/370中文编码.zip','upload')




