#! usr/bin/env python3
# -*- coding:utf-8 -*-

import random
from postgresql import get_conn, get_node_id_dict


def id_in_set(data_set, id):
    """
    判断 该id 是否在data_set中
    :param data_set: 数据集
    :param id:
    :return:
    """
    for data in data_set:
        if int(data[7]) == int(id):
            return True
    return False


def init_set():
    """
    从route表中取数据
    并根据此初始化训练集和测试集
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 节点字典
    node_dict = get_node_id_dict()
    all_nodes = list(node_dict.keys())

    # 获取数量
    count_sql = r"select count(*) from public.train_set"
    cursor.execute(count_sql)
    number = cursor.fetchone()[0]
    print(number)

    # 从train_set中读数据 加入ml_train_set和ml_graph_set中
    sql = "select * from public.train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    train_number = int(0.2 * number)
    train_set = random.sample(rows, train_number)

    for row in rows:
        classroute = row[2]
        classroutestr = row[3]
        routetime = row[4]
        id = row[7]
        if not id_in_set(train_set, row[7]):
            for i in range(len(classroute)):
                insert_sql = """
                            insert into public.ml_graph_set(user_id, attraction, attractionstr, visittime, islink) 
                            values(%s, %s, %s, %s, %s);
                    """
                cursor.execute(insert_sql, (id, classroute[i], node_dict[classroute[i]], routetime[i], True))
        else:
            for i in range(len(classroute) - 1):
                insert_sql = """
                            insert into public.ml_graph_set(user_id, attraction, attractionstr, visittime, islink) 
                            values(%s, %s, %s, %s, %s);
                    """
                cursor.execute(insert_sql, (id, classroute[i], node_dict[classroute[i]], routetime[i], True))
            insert_sql = """
                        insert into public.ml_train_set(user_id, attraction, attractionstr, visittime, islink) 
                            values(%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_sql, (id, classroute[-1], node_dict[classroute[-1]], routetime[-1], True))
            left_nodes = set(all_nodes) - set(classroute)
            neg_examples = random.sample(left_nodes, 2)
            for neg in neg_examples:
                cursor.execute(insert_sql, (id, neg, node_dict[neg], None, False))

        conn.commit()

    # 从test_set中读数据 加入ml_test_set和ml_graph_set中
    sql = "select * from public.test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        classroute = row[2]
        classroutestr = row[3]
        routetime = row[4]
        id = row[7]
        for i in range(len(classroute) - 1):
            insert_sql = """
                        insert into public.ml_graph_set(user_id, attraction, attractionstr, visittime, islink) 
                        values(%s, %s, %s, %s, %s);
                """
            cursor.execute(insert_sql, (id, classroute[i], node_dict[classroute[i]], routetime[i], True))
        insert_sql = """
                    insert into public.ml_test_set(user_id, attraction, attractionstr, visittime, islink) 
                        values(%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_sql, (id, classroute[-1], node_dict[classroute[-1]], routetime[-1], True))
        left_nodes = set(all_nodes) - set(classroute)
        neg_examples = random.sample(left_nodes, 2)
        for neg in neg_examples:
            cursor.execute(insert_sql, (id, neg, node_dict[neg], None, False))

        conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_set()