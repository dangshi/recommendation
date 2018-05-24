#! usr/bin/env python3
# -*- coding:utf-8 -*-

from MD.init_graph import init_graph, VName, AName
from postgresql import get_conn
import time


def node_all_weight(graph, node_id):
    """
    计算该节点 所链接边的所有权重之和
    :param graph:
    :param node_id:
    :return:
    """
    weight = 0
    for node in graph.neighbors(node_id):
        weight += graph[node_id][node]["weight"]
    return weight


def md(graph, user_id):
    """
    根据生成的二分图， 为该用户提供推荐
    :param graph:
    :param user_id:
    :return:
    """
    first_item_dict = dict()
    for node in graph.neighbors(VName(user_id)):
        first_item_dict[node] = 1

    temp_user_dict = dict()
    for item in first_item_dict.keys():
        for user in graph.neighbors(item):
            if user in temp_user_dict.keys():
                temp_user_dict[user] += first_item_dict[item]* graph[item][user]["weight"] / node_all_weight(graph, item)
            else:
                temp_user_dict[user] = first_item_dict[item]*graph[item][user]["weight"] / node_all_weight(graph, item)

    final_item_dict = dict()
    for user in temp_user_dict.keys():
        for item in graph.neighbors(user):
            if item in final_item_dict.keys():
                final_item_dict[item] +=temp_user_dict[user] * graph[user][item]["weight"] / node_all_weight(graph, user)
            else:
                final_item_dict[item] = temp_user_dict[user] * graph[user][item]["weight"] / node_all_weight(graph, user)

    route = list()
    for item in graph.neighbors(VName(user_id)):
        route.append(item)

    result = dict()
    for k in final_item_dict.keys():
        if k not in route:
            result[k] = final_item_dict[k]

    result = dict(sorted(result.items(),key = lambda x:x[1],reverse = True))
    return result


def hs(graph, user_id):
    """
    根据生成的二分图， 为该用户提供推荐
    :param graph:
    :param user_id:
    :return:
    """
    first_item_dict = dict()
    for node in graph.neighbors(VName(user_id)):
        first_item_dict[node] = 1

    temp_user_dict = dict()
    for item in first_item_dict.keys():
        for user in graph.neighbors(item):
            if user in temp_user_dict.keys():
                temp_user_dict[user] += first_item_dict[item]* graph[item][user]["weight"] / node_all_weight(graph, user)
            else:
                temp_user_dict[user] = first_item_dict[item]*graph[item][user]["weight"] / node_all_weight(graph, user)

    final_item_dict = dict()
    for user in temp_user_dict.keys():
        for item in graph.neighbors(user):
            if item in final_item_dict.keys():
                final_item_dict[item] +=temp_user_dict[user] * graph[user][item]["weight"] / node_all_weight(graph, item)
            else:
                final_item_dict[item] = temp_user_dict[user] * graph[user][item]["weight"] / node_all_weight(graph, item)

    route = list()
    for item in graph.neighbors(VName(user_id)):
        route.append(item)

    result = dict()
    for k in final_item_dict.keys():
        if k not in route:
            result[k] = final_item_dict[k]

    result = dict(sorted(result.items(),key = lambda x:x[1],reverse = True))
    return result


def hunhe(graph, user_id, lam=0.5):
    """
    根据生成的二分图， 为该用户提供推荐
    :param graph:
    :param user_id:
    :return:
    """
    first_item_dict = dict()
    for node in graph.neighbors(VName(user_id)):
        first_item_dict[node] = 1

    temp_user_dict = dict()
    for item in first_item_dict.keys():
        for user in graph.neighbors(item):
            if user in temp_user_dict.keys():
                temp_user_dict[user] += first_item_dict[item]* graph[item][user]["weight"] / pow(node_all_weight(graph, item), lam)
            else:
                temp_user_dict[user] = first_item_dict[item]*graph[item][user]["weight"] / pow(node_all_weight(graph, item), lam)

    final_item_dict = dict()
    for user in temp_user_dict.keys():
        for item in graph.neighbors(user):
            if item in final_item_dict.keys():
                final_item_dict[item] +=temp_user_dict[user] * graph[user][item]["weight"] / (node_all_weight(graph, user) * pow(node_all_weight(graph, item), 1-lam))
            else:
                final_item_dict[item] = temp_user_dict[user] * graph[user][item]["weight"] / (node_all_weight(graph, user) * pow(node_all_weight(graph, item), 1-lam))

    route = list()
    for item in graph.neighbors(VName(user_id)):
        route.append(item)

    result = dict()
    for k in final_item_dict.keys():
        if k not in route:
            result[k] = final_item_dict[k]

    result = dict(sorted(result.items(),key = lambda x:x[1],reverse = True))
    return result


def test(algorithm, lam=0.5):
    conn = get_conn()
    cursor = conn.cursor()

    # 从md_test_set中读取数据
    select_sql = r"select * from public.test_set"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    # 初始化二部图
    graph = init_graph()

    # 写结果
    if algorithm.__name__ == "hunhe":
        f = open("hunhe_"+str(lam) + ".txt", "w", encoding="utf-8")
    else:
        f = open(algorithm.__name__ + ".txt", "w", encoding="utf-8")

    for row in rows:
        user_id = row[7]
        classroute = row[2]
        classroutestr = row[3]

        if algorithm.__name__ == "hunhe":
            result = algorithm(graph, user_id, lam)
        else:
            result = algorithm(graph, user_id)
        f.write("%s\t%s\t%s\t%s\n" % (user_id,classroute[:-1] ,classroute[-1], str(result)))

    f.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # start = time.time()
    # print(start)
    # test(md)
    # mid = time.time()
    # print(mid)
    # test(hs)
    # end = time.time()
    # print(end)
    # print(end-start)
    print(time.time())
    test(hunhe, 0.3)
    # print(time.time())
    # test(hunhe, 0.5)
    # print(time.time())
    # test(hunhe, 0.8)
    # print(time.time())