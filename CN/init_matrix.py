#! usr/bin/env python3
# -*- coding:utf-8 -*-
from postgresql import get_conn
import numpy as np
from ML.init_graph import VName, AName


def gen_nodes_list():
    """
    产生所有的节点列表
    包括游客和景点
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    nodes_list = list()

    # 先添加游客节点
    sql = "select * from public.route_0320"
    cursor.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        user_id = row[7]
        user_id = VName(user_id)
        nodes_list.append(user_id)

    # 添加景点节点
    sql = "select * from public.node_1023"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        att_id = row[0]
        att_id = AName(att_id)
        nodes_list.append(att_id)
    return nodes_list


def init_matrix():
    """
    根据训练集的数据
    生成邻接矩阵
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 矩阵的维数
    nodes_list = gen_nodes_list()
    n = len(nodes_list)
    # 初始化矩阵
    matrix = np.mat(np.full((n ,n), np.complex(0, 0)))

    sql = "select * from public.train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 填充训练数据
    for row in rows:
        classroute = row[2]
        user_id = VName(row[7])
        user_index = nodes_list.index(user_id)

        for att_id in classroute:
            att = AName(att_id)
            att_index = nodes_list.index(att)

            matrix[user_index, att_index] = np.complex(0, 1)
            matrix[att_index, user_index] = np.complex(0, -1)

    sql = "select * from public.train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 填充测试数据
    sql = "select * from public.test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        classroute = row[2]
        user_id = VName(row[7])
        user_index = nodes_list.index(user_id)

        for att_id in classroute[:-1]:
            att = AName(att_id)
            att_index = nodes_list.index(att)

            matrix[user_index, att_index] = np.complex(0, 1)
            matrix[att_index, user_index] = np.complex(0, -1)

    return matrix


