#! usr/bin/env python3
# -*- coding:utf-8 -*-

from postgresql import get_conn
import networkx
from networkx.algorithms import bipartite
from ML.init_graph import get_a_nodes, get_v_nodes


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

    sql = "select * from public.train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[7]
        classroute = row[2]
        classroutestr = row[3]

        for atrraction_id in classroute:
            if (VName(user_id), AName(atrraction_id)) in graph.edges:
                graph[VName(user_id)][AName(atrraction_id)]["weight"] += 1
            else:
                graph.add_edge(VName(user_id), AName(atrraction_id), weight=1)

    sql = "select * from public.test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[7]
        classroute = row[2]
        classroutestr = row[3]

        for atrraction_id in classroute[:-1]:
            if (VName(user_id), AName(atrraction_id)) in graph.edges:
                graph[VName(user_id)][AName(atrraction_id)]["weight"] += 1
            else:
                graph.add_edge(VName(user_id), AName(atrraction_id), weight=1)
    return graph









if __name__ == "__main__":
    graph = init_graph()
    print(bipartite.is_bipartite(graph))
    a, b = bipartite.sets(graph)
    print(len(a))
    for i in graph.neighbors("V1"):
        print(i)

