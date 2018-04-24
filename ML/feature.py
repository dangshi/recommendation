#! usr/bin/env python3
# -*- coding:utf-8 -*-

import networkx
import math
import time


MAXD = 999999


def degrees(graph, node_id):
    weight = 0
    for node in graph.neighbors(node_id):
        weight += graph[node_id][node]["weight"]
    return weight


def neighbors_of_nei(graph, node):
    """
    节点邻居的邻居
    :param graph:
    :param node:
    :return:
    """
    nn = list()
    for n1 in graph.neighbors(node):
        for n2 in graph.neighbors(n1):
            if n2 != node and (n2 not in nn):
                nn.append(n2)
    return nn


def sn(graph, node_id):
    """
    node_id连边的总权重
    :param graph:
    :param node_id:
    :return:
    """
    weight = 0
    for node in graph.neighbors(node_id):
        weight += graph[node_id][node]["weight"]
    return weight


def cn(graph, nodev, nodea):
    """
    nodea与nodev的共同邻居
    :param graph:
    :param nodea:
    :param nodev:
    :return:
    """
    # 节点v的邻居
    nv = list(graph.neighbors(nodev))

    # 寻找节点a的邻居的邻居
    na = neighbors_of_nei(graph, nodea)

    cn = set(nv) & set(na)
    return len(cn)


def jc(graph, nodev, nodea):
    """
    交集除以并集
    :param graph:
    :param nodev:
    :param nodea:
    :return:
    """
    # 节点v的邻居
    nv = list(graph.neighbors(nodev))

    # 寻找节点a的邻居的邻居
    na = neighbors_of_nei(graph, nodea)

    # 交集
    cn = set(nv) & set(na)
    # 并集
    tn = set(nv) | set(na)

    if len(cn) == 0:
        return 0

    return len(cn) / len(tn)


def aa(graph, nodev, nodea):
    """
    Adamic/Adar
    :param graph:
    :param nodev:
    :param nodea:
    :return:
    """
    # 节点v的邻居
    nv = list(graph.neighbors(nodev))

    # 寻找节点a的邻居的邻居
    na = neighbors_of_nei(graph, nodea)

    # 交集
    cn = set(nv) & set(na)

    aa = 0
    for node in cn:
        weight = degrees(graph, node)
        if weight != 1:
            aa += 1 / math.log10(weight)
    return aa


def pa(graph, nodev, nodea):
    """
    Preferential Attachment |(e)|×|(a)|
    :param graph:
    :param nodev:
    :param nodea:
    :return:
    """
    return degrees(graph, nodev) * degrees(graph, nodea)


def sd(graph, nodev, nodea):
    """
    两个节点之间的最短距离
    :param graph:
    :param nodev:
    :param nodea:
    :return:
    """
    try:
        length = networkx.dijkstra_path_length(graph, nodev, nodea)
        return length
    except Exception as e:
        return MAXD


def prj_cn(graph, nodev, node_list):
    """
    投影图中共同邻居数目  选择最大的那个
    :param graph:
    :param nodev:
    :param node_list:
    :return:
    """
    max_number = 0
    nv = list(graph.neighbors(nodev))
    for nodea in node_list:
        if nodea == nodev:
            continue
        na = list(graph.neighbors(nodea))
        cn = set(nv) & set(na)
        if len(cn) > max_number:
            max_number = len(cn)
    return max_number


def prj_jc(graph, nodev, node_list):
    """
    投影图中jc指标
    :param graph:
    :param nodev:
    :param node_list:
    :return:
    """
    max_jc = 0
    nv = list(graph.neighbors(nodev))
    for node in node_list:
        if node == nodev:
            continue
        nn = list(graph.neighbors(node))
        cn = set(nv) & set(nn)
        tn = set(nv) | set(nn)

        if len(cn) == 0:
            continue

        if len(cn) / len(tn) > max_jc:
            max_jc = len(cn) / len(tn)
    return max_jc


def prj_aa(graph, nodev, node_list):
    """

    :param graph:
    :param nodev:
    :param node_list:
    :return:
    """
    max_aa = 0
    nv = list(graph.neighbors(nodev))
    for node in node_list:
        if node == nodev:
            continue
        nn = list(graph.neighbors(node))
        cn = set(nv) & set(nn)

        aa = 0
        for neighbor in cn:
            if graph.nodes[neighbor]["weight"] != 1:
                aa += 1 / math.log10(graph.nodes[neighbor]["weight"])
        if aa > max_aa:
            max_aa = aa
    return max_aa


def prj_pa(graph, nodev, node_list):
    """

    :param graph:
    :param nodev:
    :param node_list:
    :return:
    """
    max_pa = 0
    dv = degrees(graph, nodev)
    for node in node_list:
        if node == nodev:
            continue
        pa = degrees(graph, node) * dv
        if pa > max_pa:
            max_pa = pa
    return max_pa


def prj_sd(graph, nodev, node_list):
    """
    最短距离
    :param graph:
    :param nodev:
    :param node_list:
    :return:
    """
    min_sd = MAXD
    for node in node_list:
        if node == nodev:
            continue
        dis = sd(graph, nodev, node)
        if dis < min_sd:
            min_sd = dis
    return min_sd





def extract_direct(graph, nodev, nodea):
    """
    提取直接特征
    :param graph: 二分网络
    :param nodev:
    :param nodea:
    :return:
    """
    # 提取的特征向量
    features = list()
    # 节点v的度
    dv = sn(graph, nodev)
    da = sn(graph, nodea)

    features.append(dv)
    features.append(da)

    # 共同邻居数量
    features.append(cn(graph, nodev, nodea))
    # jc指标
    features.append(jc(graph, nodev, nodea))
    # aa指标
    features.append(aa(graph, nodev, nodea))
    # pa指标
    features.append(pa(graph, nodev, nodea))
    # sd
    features.append(sd(graph, nodev, nodea))
    return features


def extract_indirect(graph, prjv_graph, prja_graph, nodev, nodea, has_sd):
    """
    提取直接特征与间接特征
    :param graph: 二分网络
    :param prjv_graph: 在游客的投影
    :param prja_graph: 在景点的投影
    :param nodev:
    :param nodea:
    :return:
    """
    # 提取的特征向量
    features = list()
    # 节点v的度
    dv = sn(graph, nodev)
    da = sn(graph, nodea)

    features.append(dv)
    features.append(da)

    # 共同邻居数量
    features.append(cn(graph, nodev, nodea))
    # jc指标
    features.append(jc(graph, nodev, nodea))
    # aa指标
    features.append(aa(graph, nodev, nodea))
    # pa指标
    features.append(pa(graph, nodev, nodea))
    # sd
    features.append(sd(graph, nodev, nodea))

    # 间接特征

    # cn
    # print("cn")
    # print(time.time())
    features.append(prj_cn(prjv_graph, nodev, list(graph.neighbors(nodea))))
    features.append(prj_cn(prja_graph, nodea, list(graph.neighbors(nodev))))

    # jc
    # print("jc")
    # print(time.time())
    features.append(prj_jc(prjv_graph, nodev, list(graph.neighbors(nodea))))
    features.append(prj_jc(prja_graph, nodea, list(graph.neighbors(nodev))))

    # aa
    # print("aa")
    # print(time.time())
    features.append(prj_aa(prjv_graph, nodev, list(graph.neighbors(nodea))))
    features.append(prj_aa(prja_graph, nodea, list(graph.neighbors(nodev))))

    # pa
    # print("pa")
    # print(time.time())
    features.append(prj_pa(prjv_graph, nodev, list(graph.neighbors(nodea))))
    features.append(prj_pa(prja_graph, nodea, list(graph.neighbors(nodev))))

    # # sd
    # print("sd")
    # print(time.time())
    if has_sd:
        features.append(prj_sd(prjv_graph, nodev, list(graph.neighbors(nodea))))
        features.append(prj_sd(prja_graph, nodea, list(graph.neighbors(nodev))))

    # print("结束提取")
    # print(time.time())
    return features