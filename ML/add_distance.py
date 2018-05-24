#! usr/bin/env python3
# -*- coding:utf-8 -*-
from math import radians, cos, sin, asin, sqrt
from postgresql import get_conn, get_node_id_dict
from ML.init_graph import init_graph, get_v_nodes, get_a_nodes, AName, VName
import pandas as pd


def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """
    根据经纬度计算两点之间的距离 单位为公里
    :param lon1:
    :param lat1:
    :param lon2:
    :param lat2:
    :return:
    """
    # 将十进制度数转化为弧度
    # math.degrees(x):为弧度转换为角度
    # math.radians(x):为角度转换为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin( dlat /2 ) **2 + cos(lat1) * cos(lat2) * sin( dlon /2 ) **2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r


def get_node_loc_dict():
    """
    景点id  及其对应的经纬度
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    sql = "select * from public.node_1023"
    cursor.execute(sql)
    rows = cursor.fetchall()

    node_loc_dict = dict()
    for row in rows:
        att_id = AName(row[0])
        lon = row[2]
        lat = row[3]

        node_loc_dict[att_id] = (lon, lat)
    return node_loc_dict


def get_dis_feature(node_loc_dict, classroute, att_id):
    # 没有历史记录
    if len(classroute) == 0:
        return [0, 0, 0, 0]
    # 计算最近一次游览的距离
    last_loc = node_loc_dict[AName(classroute[-1])]
    att_loc = node_loc_dict[att_id]
    last_d = haversine(last_loc[0], last_loc[1], att_loc[0], att_loc[1])
    min_d = last_d
    max_d = last_d
    total_d = 0
    # 计算最小距离，平均距离， 最大距离
    for node in classroute:
        temp_loc = node_loc_dict[AName(node)]
        dis = haversine(temp_loc[0], temp_loc[1], att_loc[0], att_loc[1])
        total_d += dis
        if dis < min_d:
            min_d = dis
        if dis > max_d:
            max_d = dis
    mean_d = total_d / len(classroute)
    return [min_d, mean_d, max_d, last_d]


def cal_train_distance(save_dis_file="train_distance.csv"):
    """
    计算 训练集 的距离特征
    并保存
    :param save_dis_file: 保存训练集距离特征的文件
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 节点对应的经纬度
    node_loc_dict = get_node_loc_dict()

    sql = "select * from public.ml_train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    distance = []
    title = ["min_d", "mean_d", "max_d", "last_d"]

    for row in rows:
        user_id = VName(row[0])
        att_id = AName(row[1])

        sql = "select * from public.route_0320 where id={user_id}".format(user_id=row[0])
        cursor.execute(sql)
        item = cursor.fetchone()
        classroute = item[2][:-1]

        dis_feature = get_dis_feature(node_loc_dict, classroute, att_id)
        distance.append(dis_feature)

    # 写入到csv文件中
    df = pd.DataFrame(distance, columns=title)
    df.to_csv(save_dis_file, encoding="utf-8")


def  cal_test_distance(save_dis_file="test_distance.csv"):
    """
    计算测试集的距离特征
    :param save_dis_file:
    :return:
    """



if __name__ == "__main__":
    cal_train_distance()






