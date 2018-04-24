#! usr/bin/env python3
# -*- coding:utf-8 -*-
"""
根据用户的协同推荐
"""

from postgresql import get_conn
import math
import json
import time
from ML.init_graph import AName, VName


def form_data():
    """
    初始化数据 填充item_user和user_dict
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 从数据库中读取数据
    sql = "select * from public.train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 分别是物品表和用户表
    item_user = dict()
    user_dict = dict()

    for row in rows:
        user_id = row[7]
        classroute = row[2]

        user_dict[user_id] = dict()

        for att in classroute:
            if att in user_dict[user_id].keys():
                user_dict[user_id][att] +=1
            else:
                user_dict[user_id][att] = 1

            if att not in item_user.keys():
                item_user[att] = {user_id:1}
            else:
                if user_id in item_user[att].keys():
                    item_user[att][user_id] +=1
                else:
                    item_user[att][user_id] = 1

    # 从test_set中读取数据 不记录路径的最后一个
    sql = "select * from public.test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[7]
        classroute = row[2]

        user_dict[user_id] = dict()

        for att in classroute[:-1]:
            if att in user_dict[user_id].keys():
                user_dict[user_id][att] +=1
            else:
                user_dict[user_id][att] = 1

            if att not in item_user.keys():
                item_user[att] = {user_id:1}
            else:
                if user_id in item_user[att].keys():
                    item_user[att][user_id] +=1
                else:
                    item_user[att][user_id] = 1


    cursor.close()
    conn.close()
    return user_dict, item_user


def cos_sm_item(item_user, t1, t2):
    """
    计算两个物品之间的余弦相似度
    :param item_user:
    :param t1: item1
    :param t2: item2
    :return:
    """
    sum_xy = 0
    sum_xx = 0
    sum_yy = 0

    for user in item_user[t1].keys():
        sum_xx += item_user[t1][user]
        if user in item_user[t2].keys():
            sum_xy += item_user[t1][user] * item_user[t2][user]

    for user in item_user[t2].keys():
        sum_yy += item_user[t2][user] * item_user[t2][user]

    if sum_xy == 0:
        return sum_xy

    return sum_xy / math.sqrt(sum_xx * sum_yy)


def recommend_by_item(user_dict, item_user, user):
    """
    基于物品相似对用户进行推荐
    :param user_dict:
    :param item_user:
    :param user:
    :return:
    """
    route = list(user_dict[user].keys())
    left_nodes = set(item_user.keys()) - set(route)
    recommend_dict = dict()

    for item in left_nodes:
        value = 0
        for past_node in route:
            value += len(item_user[item]) * cos_sm_item(item_user, item, past_node)
        if value != 0:
            recommend_dict[AName(item)] = value

    recommend_dict = dict(sorted(recommend_dict.items(), key=lambda x: x[1], reverse=True))
    return recommend_dict


def test():
    """
    开始进行预测
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()


    # 初始化矩阵
    user_dict, item_user = form_data()
    print("初始化矩阵完成")
    print(time.time())

    sql = "select * from public.test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    f = open("recommend_by_item.txt", "w", encoding="utf-8")
    i = 0
    for row in rows:
        i += 1
        if i % 100 == 0:
            print("完成:"+str(i))

        user = row[7]
        classroute = row[2]

        rec_dict = recommend_by_item(user_dict, item_user, user)
        f.writelines("%s\t%s\t%s\t%s\n" % (user, classroute[:-1], AName(classroute[-1]), json.dumps(rec_dict)))

    f.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    start = time.time()
    test()
    end = time.time()
    print(end-start)