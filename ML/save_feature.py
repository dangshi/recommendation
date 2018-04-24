#! usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
sys.path.append("../")
import pandas as pd
from postgresql import get_conn, get_node_id_dict
from ML.init_graph import init_graph, get_v_nodes, get_a_nodes, AName, VName
from ML.svm import project
from ML.feature import extract_direct, extract_indirect
import time
import csv


def write_train_feature(func, have_sd=0):
    """
    生成训练集特征
    并写入文件
    :param func:
    :param have_sd: 间接特征 是否含有最短距离
    :return:
    """
    if have_sd:
        file_name = func.__name__ + "_has_sd_train.csv"
    else:
        file_name = func.__name__ + "_train.csv"

    # 读取数据
    conn = get_conn()
    cursor = conn.cursor()

    # 二分网络
    graph = init_graph()
    print("构建二分网络完成")
    print(time.time())
    # 进行投影
    v_nodes = get_v_nodes()
    a_nodes = get_a_nodes()
    prjv_graph = project(graph, v_nodes)
    prja_graph = project(graph, a_nodes)
    print("网络投影完成")
    print(time.time())

    sql = "select * from public.ml_train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("len_rows:" + str(len(rows)))

    if func.__name__ == "extract_direct":
        title = ["label", "snv", "sna", "cn", "jc", "aa", "pa", "sd"]
    elif func.__name__ == "extract_indirect":
        if have_sd:
            title = ["label", "snv", "sna", "cn", "jc", "aa", "pa", "sd", "prj_cnv", "prj_cna", "prj_jcv", "prj_jca",
                     "prj_aav", "prj_aaa", "prj_pav", "prj_paa", "prj_sdv", "prj_sda"]
        else:
            title = ["label", "snv", "sna", "cn", "jc", "aa", "pa", "sd", "prj_cnv", "prj_cna", "prj_jcv", "prj_jca",
                     "prj_aav", "prj_aaa", "prj_pav", "prj_paa"]
    else:
        print("函数错误")
        return

    i = 0
    train_f = []
    for row in rows:
        i += 1
        print(i)

        user_id = VName(row[0])
        att_id = AName(row[1])

        if func.__name__ == "extract_direct":
            feature = func(graph, user_id, att_id)
        elif func.__name__ == "extract_indirect":
            feature = func(graph, prjv_graph, prja_graph, user_id, att_id, have_sd)
        else:
            print("函数错误")

        if row[4]:
            line = [1]
            line.extend(feature)
            train_f.append(line)
        else:
            line = [0]
            line.extend(feature)
            train_f.append(line)

    # 写入到csv文件中
    df = pd.DataFrame(train_f, columns=title)
    df.to_csv(file_name, encoding="utf-8")

    print("训练特征保存完成")


def write_test_feature(func, has_sd=0):
    """
    保存测试集的特征
    :param func:
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    if has_sd:
        file_name = func.__name__ + "_has_sd_test.csv"
    else:
        file_name = func.__name__ + "_test.csv"

    if func.__name__ == "extract_direct":
        title = ["anode", "snv", "sna", "cn", "jc", "aa", "pa", "sd"]
    elif func.__name__ == "extract_indirect":
        if has_sd:
            title = ["anode", "snv", "sna", "cn", "jc", "aa", "pa", "sd", "prj_cnv", "prj_cna", "prj_jcv", "prj_jca",
                     "prj_aav", "prj_aaa", "prj_pav", "prj_paa", "prj_sdv", "prj_sda"]
        else:
            title = ["anode", "snv", "sna", "cn", "jc", "aa", "pa", "sd", "prj_cnv", "prj_cna", "prj_jcv", "prj_jca",
                     "prj_aav", "prj_aaa", "prj_pav", "prj_paa"]
    else:
        print("函数错误")
        return

    # 读数据
    sql = "select * from public.ml_test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 二分网络
    graph = init_graph()
    print("构建二分网络完成")
    print(time.time())
    # 进行投影
    v_nodes = get_v_nodes()
    a_nodes = get_a_nodes()
    prjv_graph = project(graph, v_nodes)
    prja_graph = project(graph, a_nodes)
    print("投影完成")
    print(time.time())
    # 所有的景点
    a_nodes = list(get_node_id_dict().keys())

    test_f = []
    i = 0
    for row in rows:
        print(i)
        i += 1

        user_id = VName(row[0])
        att_id = AName(row[1])
        is_link = row[4]

        if not is_link:
            continue

        sql = "select classroute from public.route_0320 where id={user_id}".format(user_id=row[0])
        cursor.execute(sql)
        result = cursor.fetchone()
        classroute = result[0]

        # 待预测的集合
        left_set = set(a_nodes) - set(classroute[0:-1])

        for anode in left_set:
            anode = AName(anode)
            if func.__name__ == "extract_direct":
                feature = func(graph, user_id, anode)
            elif func.__name__ == "extract_indirect":
                feature = func(graph, prjv_graph, prja_graph, user_id, anode, has_sd)
            else:
                print("函数名错误")

            line = [anode]
            line.extend(feature)
            test_f.append(line)

    # 写入到csv文件中
    df = pd.DataFrame(test_f, columns=title)
    df.to_csv(file_name, encoding="utf-8")

    print("测试特征保存完成")


if __name__ == "__main__":
    print(time.time())
    # write_train_feature(extract_direct)
    # print("直接训练特征提取完成")
    # print(time.time())
    # write_test_feature(extract_direct)
    # print("直接测试特征提取完成")
    print(time.time())
    print("间接训练特征提取开始")
    write_train_feature(extract_indirect, have_sd=0)
    print("间接训练特征提取完成")
    print(time.time())
    print("间接测试特征提取开始")
    write_test_feature(extract_indirect, has_sd=0)
    print("间接测试特征提取完成")
    print(time.time())

    print("间接训练特征提取开始 有最短距离")
    write_train_feature(extract_indirect, have_sd=1)
    print("间接训练特征提取完成 有最短距离")
    print(time.time())
    print("间接测试特征提取开始 有最短距离")
    write_test_feature(extract_indirect, has_sd=1)
    print("间接测试特征提取完成 有最短距离")
    print(time.time())

