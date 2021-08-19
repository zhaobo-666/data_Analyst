import pymysql
import function

"""
公共必要字段
main_name  主卡姓名
main_card  主卡卡号
to_name    对方姓名
to_card    对方卡号
sign       收付标志
money      交易金额
balance    余额
abstract   摘要


级别表 必须在总表中添加批次字段  一级卡号为第一批次主卡号
`批次` = 1
"""


# host ='172.16.2.190'
# user = 'hzdb'
# pwd = 'hzdb@2021'
# db = 'hzdb'
# port  = 3306

#函数
# def list_fetchall(sql):
#     conn = pymysql.connect(host=host, user=user, passwd=pwd, port=port, db=db)
#     cursor = conn.cursor()
#     cursor.execute(sql)
#     rows = cursor.fetchall()
#     row = [item[0] for item in rows]
#     cursor.close()
#     conn.close()
#     return row
#
# def conn_fetchall(sql):
#     conn = pymysql.connect(host=host, user=user, passwd=pwd, port=port, db=db)
#     cursor = conn.cursor()
#     cursor.execute(sql)
#     desc = cursor.description
#     ob_dict = [dict(zip([col[0] for col in desc],row)) for row in cursor.fetchall()]
#     cursor.close()
#     conn.close()
#     return ob_dict
#
# def conn_exec(sql):
#     conn = pymysql.connect(host=host, user=user, passwd=pwd, port=port, db=db)
#     cursor = conn.cursor()
#     num = cursor.execute(sql)
#     cursor.connection.commit()
#     cursor.close()
#     conn.close()
#     return num

#分析结果表字段
table_res = "分析结果表"



#table_name = "总表_去重"
# main_name = "主卡户名"
# main_card = "查询账号"
# to_name = "对方账号姓名"
# to_card = "对方账号卡号"
# sign = "借贷标志"
# money = "金额"
# balance = "余额"
# abstract = "交易摘要"
# limit_number = 20


def analysis(cursor_user, table_name, main_name, main_card, to_name, to_card, sign, money, abstract, limit_number):
#def analysis(cursor_user, **attrs):
    # table_name = attrs['table_name']
    # main_name = attrs['main_name']
    # main_card = attrs['main_card']
    # to_name = attrs['to_name']
    # to_card = attrs['to_card']
    # sign = attrs['sign']
    # money = attrs['money']
    # abstract = attrs['abstract']
    # limit_number = attrs['limit_number']
    #创建卡号级别表
    create_card_level = "create table if not exists 卡号级别表 (`卡号` varchar(255),`级别` varchar(255))"
    print(create_card_level)
    function.conn_exec(create_card_level,cursor_user)
    sql_1 = "select  `%s` from `%s` where `批次`= 1 group by `%s`"%(main_card,table_name,main_card)
    cards = function.list_fetchall(sql_1,cursor_user)
    for card in cards:
        #插入级别表
        card_level_sql_1 = "insert into `卡号级别表`(`卡号`,`级别`)values('%s','%s')"%(card,'一级卡号')
        print(card_level_sql_1)
        function.conn_exec(card_level_sql_1,cursor_user)
        # 查询下级卡号
        sql_2 = "select `%s` from `%s` where `%s`='%s' and (`%s`= '借' or  `%s`= '出') group by `%s`" % (to_card,table_name,main_card,card,sign,sign,to_card)
        print(sql_2)
        cards_2 = function.list_fetchall(sql_2,cursor_user)
    for card_2 in cards_2:
        #判断是否是已经调取的卡号
        if card_2 in cards:
            continue
        # 插入级别表
        card_level_sql_2 = "insert into `卡号级别表`(`卡号`,`级别`)values('%s','%s')" % (card_2, '二级卡号')
        print(card_level_sql_2)
        function.conn_exec(card_level_sql_2,cursor_user)
        # 查询下级卡号
        sql_3 = "select `%s` from `%s` where `%s`='%s'and (`%s`= '借' or  `%s`= '出') group by `%s`" % (to_card, table_name, main_card, card_2,sign,sign,to_card)
        print(sql_3)
        cards_3 = function.list_fetchall(sql_3,cursor_user)
    for card_3 in cards_3:
        # 判断是否是已经调取的卡号
        if card_3 in cards or card_3 in cards_2:
            continue
        # 插入级别表
        card_level_sql_3 = "insert into `卡号级别表`(`卡号`,`级别`)values('%s','%s')" % (card_3, '三级卡号')
        print(card_level_sql_3)
        function.conn_exec(card_level_sql_3,cursor_user)
        # 查询下级卡号
        sql_4 = "select `%s` from `%s` where `%s`='%s'and (`%s`= '借' or  `%s`= '出') group by `%s`" % (
        to_card, table_name, main_card, card_3, sign, sign,to_card)
        print(sql_4)
        cards_4 = function.list_fetchall(sql_4,cursor_user)


    #创建分析结果表
    create_res_tab = "create table if not exists 分析结果表 (`户名` varchar(255) DEFAULT NULL,`卡号`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`交易金额`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`标志`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`分析原因`" \
                     " varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,`账户级别`" \
                     " varchar(255) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8"
    print(create_res_tab)
    function.conn_exec(create_res_tab,cursor_user)

    #查询提现
    sql_cash = " select `%s`,`%s`,sum(`%s`) as `交易总额`,'现金提现' as `分析原因` from `%s`" \
               " where `%s`>10000 and(`%s` like '提现' or `%s` like '现金' or `%s` like '取款' or %s !='其他')"\
               %(main_name,main_card,money,table_name,money,abstract,abstract,abstract,sign)
    print(sql_cash)
    cash_data = function.conn_fetchall(sql_cash,cursor_user)
    for cash_da in cash_data:
        cash_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                      "('%s','%s','%s','%s')"%(table_res,cash_da[main_name],cash_da[main_card],cash_da['交易总额'],cash_da['分析原因'])
        print(cash_insert)
        function.conn_exec(cash_insert,cursor_user)

    #打给公司
    sql_company = "select `%s`,`%s`,sum(`%s`) as `交易总额`,'打给公司' as `分析原因` from" \
                  " `%s`where char_length(`%s`)>4 and `%s`>10000 group by `%s`"%(main_name,main_card,money,table_name,to_name,money,main_card)
    print(sql_company)
    company_data = function.conn_fetchall(sql_company,cursor_user)
    for company_da in company_data:
        company_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                      "('%s','%s','%s','%s')"%(table_res,company_da[main_name],company_da[main_card],company_da['交易总额'],company_da['分析原因'])
        print(company_insert)
        function.conn_exec(company_insert,cursor_user)



    #交叉账户
    sql_max_money = "select ToUser,ToCard,round(sum(sum)/10000,0) as `交易总额`,'交叉账户' as `分析原因`,count(*) as count from " \
               "(select `%s` as `FromUser`,`%s` as FromCard,`%s` as ToUser,`%s`" \
               " as ToCard, `%s` as Direction,count(*) as count,sum(`%s`) as sum from %s" \
               " group by `%s`,`%s`,`%s`,`%s`,`%s`) A group by ToUser,ToCard having count(*)>=3 limit %d"\
               %(main_name,main_card,to_name,to_card,sign,money,table_name,main_name,main_card,to_name,to_card,sign,limit_number)
    print(sql_max_money)
    max_money_data = function.conn_fetchall(sql_max_money,cursor_user)
    for max_money_da in max_money_data:
        max_money_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                      "('%s','%s','%s','%s')"%(table_res,max_money_da['ToUser'],max_money_da['ToCard'],max_money_da['交易总额'],max_money_da['分析原因'])
        print(max_money_insert)
        function.conn_exec(max_money_insert,cursor_user)



    #交易金额较大
    sql_relation = "select ToUser,ToCard,round(sum(sum)/10000,0) as `交易总额`,'交易金额较大' as `分析原因`,sum(count) from " \
                   "(select `%s` as `FromUser`,`%s` as FromCard,`%s` as ToUser," \
                   "`%s` as ToCard, `%s` as Direction,count(*) as count,sum(`%s`)" \
                   " as sum from `%s` group by `%s`,`%s`,`%s`,`%s`,`%s`)" \
                   " A group by ToUser,ToCard order by round(sum(sum)/10000,0) desc limit %d"\
                   %(main_name,main_card,to_name,to_card,sign,money,table_name,main_name,main_card,to_name,to_card,sign,limit_number)
    print(sql_relation)
    relation_data = function.conn_fetchall(sql_relation,cursor_user)
    for relation_da in relation_data:
        relation_insert = "insert into `%s` (`户名`,`卡号`,`交易金额`,`分析原因`)values" \
                      "('%s','%s','%s','%s')"%(table_res,relation_da['ToUser'],relation_da['ToCard'],relation_da['交易总额'],relation_da['分析原因'])
        print(relation_insert)
        function.conn_exec(relation_insert,cursor_user)









