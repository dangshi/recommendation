#! usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
import psycopg2


def get_conn():
    """
    获取数据库连接
    :return:
    """
    db = "flickr"
    user = "postgres"
    password = "root"
    host = "127.0.0.1"
    port = "5432"

    try:
        conn = psycopg2.connect(database=db, user=user, password=password,host=host, port=port)
        return conn
    except Exception as e:
        print("数据库连接失败, Exception:"+str(e))
        logging.ERROR("数据库连接失败, Exception:"+str(e))
        return None


def get_all_edges():
    # 数据库连接
    conn = get_conn()
    cursor = conn.cursor()

    # 执行查询语句
    select_sql = r"SELECT n1, n2, addr1, addr2, flow12, flow21, flow from edge_1031"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    # 进行格式转化
    all_edges = list()
    for row in rows:
        edge = dict()
        edge["n1"] = row[0]
        edge["n2"] = row[1]
        edge["addr1"] = row[2]
        edge["addr2"] = row[3]
        edge["flow12"] = row[4]
        edge["flow21"] = row[5]
        edge["flow"] = row[6]
        all_edges.append(edge)
    cursor.close()
    conn.close()
    return all_edges


def get_all_nodes():
    conn = get_conn()
    cursor = conn.cursor()

    # 获取所有节点
    select_sql = r"SELECT num, addr from node_1023"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    # 转换格式
    all_nodes = list()
    for row in rows:
        node = dict()
        node["num"] = row[0]
        node["addr"] = row[1]
        all_nodes.append(node)
    cursor.close()
    conn.close()
    return all_nodes


def find_node_by_id(all_nodes, id):
    """
    根据id 查找节点
    :param all_nodes: 所有的节点
    :param id: 节点id
    :return: 该节点
    """
    for node in all_nodes:
        if int(node["num"]) == int(id):
            return node
    return None


def get_node_id_dict():
    conn = get_conn()
    cursor = conn.cursor()

    # 获取所有节点
    select_sql = r"SELECT num, addr from node_1023"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    # 转换格式
    node_dict = dict()
    for row in rows:
        node_dict[row[0]] = row[1]
    cursor.close()
    conn.close()
    return node_dict

