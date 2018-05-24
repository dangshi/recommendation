#! usr/bin/python3
# -*- coding:utf-8 -*-
from postgresql import get_conn
from MD.init_graph import AName


def statistical_attraction():
    """
    统计旅游景点的流行度
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 读数据
    sql = "select * from public.route_0320"
    cursor.execute(sql)
    rows = cursor.fetchall()

    node_pop = dict()
    for row in rows:
        classroute = row[2]
        for node in classroute:
            if node in node_pop.keys():
                node_pop[node] += 1
            else:
                node_pop[node] = 1

    node_pop = sorted(node_pop.items(), key=lambda x:x[1], reverse=True)
    node_pop = dict(node_pop)

    for (x, y) in node_pop.items():
        print(x, y)


def att_distribute():
    """
    景点的度分布
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 读数据
    sql = "select * from public.route_0320"
    cursor.execute(sql)
    rows = cursor.fetchall()

    node_pop = dict()
    for row in rows:
        classroute = row[2]
        for node in classroute:
            if node in node_pop.keys():
                node_pop[node] += 1
            else:
                node_pop[node] = 1

    node_pop = sorted(node_pop.items(), key=lambda x: x[1], reverse=True)
    node_pop = dict(node_pop)

    degree_dis = dict()
    for (x, y) in node_pop.items():
        if y not in degree_dis.keys():
            degree_dis[y] = 1
        else:
            degree_dis[y] += 1

    degree_dis = dict(sorted(degree_dis.items(), key=lambda x:x[1], reverse=True))
    for (x, y) in degree_dis.items():
        print(x, y)


def user_distribute():
    """
    用户的度分布
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 读数据
    sql = "select * from public.route_0320"
    cursor.execute(sql)
    rows = cursor.fetchall()

    user_dis = dict()
    for row in rows:
        classroute = row[2]
        if len(classroute) in user_dis.keys():
            user_dis[len(classroute)] += 1
        else:
            user_dis[len(classroute)] = 1

    node_pop = sorted(user_dis.items(), key=lambda x: x[0])
    node_pop = dict(node_pop)

    for (x, y) in node_pop.items():
        print(x, y)


def att_degree():
    conn = get_conn()
    cursor = conn.cursor()

    # 读数据
    sql = "select * from public.route_0320"
    cursor.execute(sql)
    rows = cursor.fetchall()

    node_pop = dict()
    for row in rows:
        classroute = row[2]
        for node in classroute:
            if AName(node) in node_pop.keys():
                node_pop[AName(node)] += 1
            else:
                node_pop[AName(node)] = 1

    node_pop = sorted(node_pop.items(), key=lambda x: x[1], reverse=True)
    node_pop = dict(node_pop)
    return node_pop


if __name__ == "__main__":
    statistical_attraction()
    # att_distribute()
    # user_distribute()