#! usr/bin/python3
# -*- coding:utf-8 -*-
from postgresql import get_conn


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


if __name__ == "__main__":
    statistical_attraction()