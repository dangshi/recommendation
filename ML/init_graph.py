#! usr/bin/env python3
# -*- coding:utf-8 -*-

from postgresql import get_conn
import networkx
from networkx.algorithms import bipartite


def VName(visitor_id):
    """
    对游客id进行修饰
    :param visitor_id:
    :return:
    """
    if isinstance(visitor_id, int):
        return "V" + str(visitor_id)
    elif isinstance(visitor_id, str) and visitor_id[0] != "V":
        return "V" + visitor_id
    else:
        return visitor_id


def AName(attraction_id):
    """
    对景点id进行修饰
    :param attraction_id:
    :return:
    """
    if isinstance(attraction_id, int):
        return "A" + str(attraction_id)
    elif isinstance(attraction_id, str) and attraction_id[0] != "A":
        return "A" + attraction_id
    else:
        return attraction_id


def get_v_nodes():
    conn = get_conn()
    cursor = conn.cursor()

    sql = "select id from public.route_0320"
    cursor.execute(sql)
    rows = cursor.fetchall()

    id_list = list()
    for row in rows:
        user_id = VName(row[0])
        id_list.append(user_id)

    cursor.close()
    conn.close()
    return set(id_list)


def get_a_nodes():
    conn = get_conn()
    cursor = conn.cursor()

    sql = "select num from public.node_1023"
    cursor.execute(sql)
    rows = cursor.fetchall()

    a_list = list()
    for row in rows:
        att_id = AName(row[0])
        a_list.append(att_id)

    cursor.close()
    conn.close()
    return set(a_list)


def init_graph():
    conn = get_conn()
    cursor = conn.cursor()

    graph = networkx.Graph()

    # 添加 游客节点
    VNodes = get_v_nodes()
    for node in VNodes:
        graph.add_node(node, bipartite=0)
    # 添加景点节点
    ANodes = get_a_nodes()
    for node in ANodes:
        graph.add_node(node, bipartite=1)

    # 从ml_graph_set中读取数据
    select_sql = r"select * from public.ml_graph_set"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    for row in rows:
        user_id = row[0]
        atrraction_id = row[1]
        atrraction_name = row[2]

        if (VName(user_id), AName(atrraction_id)) in graph.edges:
            graph[VName(user_id)][AName(atrraction_id)]["weight"] += 1
        else:
            graph.add_edge(VName(user_id), AName(atrraction_id), weight=1)

    return graph


def my_weight(graph, u, v, weight="weight"):
    """
    用于二分网络的投影
    :param graph:
    :param u:
    :param v:
    :param weight:
    :return:
    """
    w = 0
    for nbr in set(graph[u]) & set(graph[v]):
        w += graph[u][nbr][weight] + graph[v][nbr][weight]
    return w



if __name__ == "__main__":
    graph = init_graph()
    print(bipartite.is_bipartite(graph))
    a, b = bipartite.sets(graph)
    print(len(a))
    for i in graph.neighbors("V1"):
        print(i)


