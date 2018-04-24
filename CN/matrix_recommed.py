#! usr/bin/env python3
# -*- coding:utf-8 -*-
from CN.init_matrix import init_matrix, gen_nodes_list
from postgresql import get_conn, get_node_id_dict
from ML.init_graph import VName, AName
import json


def recommend_list(route_length=3, coeffs=[]):
    """

    :param route_length:
    :return:
    """
    nodes_list = gen_nodes_list()
    matrix = init_matrix()

    conn = get_conn()
    cursor = conn.cursor()

    if route_length == 3:
        final_matrix = (matrix ** 3)
    elif route_length == 5:
        if coeffs_list:
            final_matrix = (matrix ** 3) + (matrix ** 5) / coeffs_list[0]
        else:
            final_matrix = (matrix ** 3) + (matrix ** 5) / 20
    elif route_length ==7 :
        final_matrix = (matrix ** 3) + (matrix ** 5) / 2 + (matrix ** 7) / 3
    else:
        print("暂时没有对应的公式")
        return

    sql = "select * from public.test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    file_name = "cn_route_" + str(route_length) + ".txt"
    f = open(file_name, "w", encoding="utf-8")

    # 所有的景点
    a_nodes = list(get_node_id_dict().keys())
    # 用于记录所有测试案例的推荐结果
    record_result = dict()
    for row in rows:
        classroute = row[2]
        user_id = VName(row[7])
        user_index = nodes_list.index(user_id)

        # 剩余的 待推荐景点
        left_nodes = list(set(a_nodes) - set(classroute[:-1]))
        result_dict = dict()
        for node in left_nodes:
            node = AName(node)
            att_index = nodes_list.index(node)

            imag_coeff = final_matrix[user_index, att_index].imag

            if imag_coeff == 0.0:
                continue
            else:
                result_dict[node] = imag_coeff

        # 对结果进行排序
        result_dict = dict(sorted(result_dict.items(), key=lambda x:x[1], reverse=True))
        # 记录推荐结果
        f.write("%s\t%s\t%s\t%s\n" % (user_id, classroute[:-1], AName(classroute[-1]), json.dumps(result_dict)))
        record_result[user_id] = {"user_id":user_id, "classroute":classroute[-1], "answer":AName(classroute[-1]),
                                  "recommend":result_dict}
    return record_result


def cal_precision(result, n):
    """
    计算前n个推荐结果的准确率
    :param result:
    :param n:
    :return:
    """
    total = 0
    right = 0
    for user_id in result.keys():
        total += 1
        answer = result[user_id]["answer"]
        recommend = result[user_id]["recommend"]
        if AName(answer) in list(recommend.keys())[:n]:
            right += 1
    return right / total


def com_precision(a_result, b_result):
    """
    比较不同的结果 推荐前十的准确率
    :param a_result:
    :param b_result:
    :return:
    """
    # a_result 是空字典
    if not a_result:
        return True
    if not b_result:
        return False

    b_better = 0
    for i in range(1, 11):
        a_precision = cal_precision(a_result, i)
        b_precision = cal_precision(b_result, i)
        if b_precision > a_precision:
            b_better += 1

    if b_better > 5:
        return True
    else:
        return False


def grid_search(route_length, coeffs_list):
    """

    :param route_length:
    :param coeffs_list:
    :return:
    """
    best_coeff = list()
    best_result = dict()

    for coeffs in coeffs_list:
        temp_result = recommend_list(route_length, coeffs)

        if com_precision(best_result, temp_result):
            best_result = temp_result
            best_coeff = coeffs
    return best_coeff, best_result


if __name__ == "__main__":
    coeffs_list = list()
    for i in range(1, 101, 4):
        coeffs_list.append([i])

    best_coeff, best_result = grid_search(route_length=5, coeffs_list=coeffs_list)
    print(best_coeff)
    print(best_result)
    for i in range(1, 11):
        print(cal_precision(best_result, i))
