#! usr/bin/env python3
# -*- coding:utf-8 -*-
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


def cos_sm_user(user_dict, u1, u2):
    """
    计算两个用户之间的余弦相似度
    :param user_dict:
    :param u1: 用户1
    :param u2: 用户2
    :return:
    """
    sum_xy = 0
    sum_xx = 0
    sum_yy = 0

    for item in user_dict[u1].keys():
        sum_xx += user_dict[u1][item]
        if item in user_dict[u2].keys():
            sum_xy += user_dict[u1][item] * user_dict[u2][item]

    for item in user_dict[u2].keys():
        sum_yy += user_dict[u2][item] * user_dict[u2][item]

    if sum_xy == 0:
        return sum_xy

    return sum_xy / math.sqrt(sum_xx * sum_yy)


def gen_near_neighbors(user_dict, item_user, user):
    """
    计算user 较为相似的用户集
    :param user_dict:
    :param item_user:
    :param user:
    :return:
    """
    neighbors = list()
    for item in user_dict[user].keys():
        for neighbor in item_user[item].keys():
            if neighbor != user and neighbor not in neighbors:
                neighbors.append(neighbor)

    neighbor_dict = dict()
    for neighbor in neighbors:
        sm = cos_sm_user(user_dict, neighbor, user)
        neighbor_dict[neighbor] = sm
    neighbor_dict = dict(sorted(neighbor_dict.items(), key= lambda x:x[1], reverse=True))
    return neighbor_dict


def recommend_by_user(user_dict, item_user, user, k=10):
    """
    对该用户进行推荐
    :param user_dict:
    :param item_user:
    :param user:
    :param k: 选择最近的k个邻居
    :return:
    """
    neighbor_dict = gen_near_neighbors(user_dict, item_user, user)
    neighbor_dict = dict(list(neighbor_dict.items())[:k])
    recommend_dict = dict()
    route = list(user_dict[user].keys())
    left_nodes = set(item_user.keys()) - set(route)
    for item in left_nodes:
        up = 0
        down = 0
        for neighbor in neighbor_dict.keys():
            if item in user_dict[neighbor].keys():
                up += neighbor_dict[neighbor] * user_dict[neighbor][item]
            down += neighbor_dict[neighbor]
        if up != 0:
            recommend_dict[AName(item)] = up / down

    recommend_dict = dict(sorted(recommend_dict.items(), key=lambda x:x[1], reverse=True))
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

    f = open("recommend_20.txt", "w", encoding="utf-8")
    i = 0
    for row in rows:
        i += 1
        if i % 100 == 0:
            print("完成:"+str(i))

        user = row[7]
        classroute = row[2]

        rec_dict = recommend_by_user(user_dict, item_user, user, 20)
        f.writelines("%s\t%s\t%s\t%s\n" % (user, classroute[:-1], AName(classroute[-1]), json.dumps(rec_dict)))

    f.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    start = time.time()
    test()
    end = time.time()
    print(end-start)