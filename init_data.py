#! usr/bin/env python3
# -*- coding:utf-8 -*-

from postgresql import get_conn, get_all_nodes
import networkx
import random


def id_in_set(data_set, id):
    """
    判断 该id 是否在data_set中
    :param data_set: 数据集
    :param id:
    :return:
    """
    for data in data_set:
        if int(data[7]) == int(id):
            return True
    return  False


def init_set():
    """
    从route表中取数据
    并根据此初始化训练集和测试集
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 获取数量
    count_sql = r"select count(*) from public.route_0320"
    cursor.execute(count_sql)
    number = cursor.fetchone()[0]
    print(number)

    # 取出所有元素
    select_sql = r"select * from public.route_0320 order by id"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    train_number = int(0.9*number)
    test_number = number - train_number
    train_set = random.sample(rows, train_number)

    for row in rows:
        if id_in_set(train_set, row[7]):
            insert_sql = """
                            insert into public.train_set(id_base64,route, classroute, classroutestr, routetime, starttime,
                            endtime, id, route_length) values(%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
        else:
            insert_sql = """
                            insert into public.test_set(id_base64,route, classroute, classroutestr, routetime, starttime,
                            endtime, id, route_length) values(%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
        cursor.execute(insert_sql, row)
        conn.commit()

    cursor.close()
    conn.close()




if __name__ == "__main__":
    init_set()