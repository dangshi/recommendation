#! usr/bin/env python3
# -*- coding:utf-8 -*-
import json
from ML.init_graph import AName
from constant_data import POPULAR_ATTR


def av_position(file):
    """
    对结果进行评价
    计算正确景点的平均推荐位置
    :param file:
    :return:
    """
    f = open(file, "r", encoding="utf-8")

    pos_lst = list()
    for line in f:
        line = line.strip()
        s_lst = line.split('\t')
        answer = s_lst[2]
        predict_lst = s_lst[3]
        predict_lst = predict_lst.replace("'", '"')
        predict_lst = json.loads(predict_lst)
        predict_lst = list(predict_lst.keys())

        try:
            pos = predict_lst.index(AName(answer))
            pos_lst.append(pos/len(predict_lst))
        except Exception as e:
            pos_lst.append(1)

    print(pos_lst)

    av_pos = sum(pos_lst) / len(pos_lst)
    print(av_pos)


def av_position_except_pop(file):
    """
    不计流行景点
    对结果进行评价
    计算正确景点的平均推荐位置
    :param file:
    :return:
    """
    f = open(file, "r", encoding="utf-8")

    pos_lst = list()
    for line in f:
        line = line.strip()
        s_lst = line.split('\t')
        answer = AName(s_lst[2])
        predict_lst = s_lst[3]
        predict_lst = predict_lst.replace("'", '"')
        predict_lst = json.loads(predict_lst)
        predict_lst = list(predict_lst.keys())

        # 不计流行景点
        if answer in POPULAR_ATTR.keys():
            continue

        try:
            pos = predict_lst.index(AName(answer))
            pos_lst.append(pos/len(predict_lst))
        except Exception as e:
            pos_lst.append(1)

    print(pos_lst)

    av_pos = sum(pos_lst) / len(pos_lst)
    print(av_pos)


def top_N(file):
    for n in range(1, 221):
        f = open(file, "r", )

        right = 0
        total = 0
        for line in f:
            total += 1
            line = line.strip()
            s_lst = line.split('\t')
            answer = AName(s_lst[2])
            predict_lst = s_lst[3]
            predict_lst = predict_lst.replace("'", '"')
            predict_lst = json.loads(predict_lst)
            predict_lst = list(predict_lst.keys())

            if AName(answer) in predict_lst[:n]:
                right += 1
        print("top_%s: %s"% (n, right/total))


def top_N_except_pop(file):
    """
    去掉流行景点的准确度
    :param file:
    :return:
    """
    for n in range(1, 221):
        f = open(file, "r", )

        right = 0
        total = 0
        for line in f:
            line = line.strip()
            s_lst = line.split('\t')
            answer = AName(s_lst[2])
            predict_lst = s_lst[3]
            predict_lst = predict_lst.replace("'", '"')
            predict_lst = json.loads(predict_lst)
            predict_lst = list(predict_lst.keys())

            if answer not in POPULAR_ATTR.keys():
                total += 1
            else:
                continue

            if AName(answer) in predict_lst[:n]:
                right += 1
        print("top_%s: %s"% (n, right/total))


if __name__ == "__main__":
    # av_position(r"MD\hs.txt")
    # top_N(r"MD\hs.txt")
    # av_position(r"MD\md.txt")
    # top_N(r"MD\md.txt")
    # av_position(r"CF\recommend.txt")
    # top_N(r"CF\recommend.txt")
    # av_position(r"CF\recommend_by_item.txt")
    # top_N(r"CF\recommend_by_item.txt")
    # av_position(r"ML\recommend_extract_direct_rbf_C0.1_gamma0.0001.txt")
    # top_N(r"ML\recommend_extract_direct_rbf_C0.1_gamma0.0001.txt")
    # av_position(r"ML/xgboost_result/direct.txt")
    # top_N(r"ML/xgboost_result/direct.txt")
    av_position(r"CN/cn_route_7.txt")
    top_N(r"CN/cn_route_7.txt")

    # av_position_except_pop(r"CF\recommend.txt")
    # top_N_except_pop(r"CF\recommend.txt")
    # av_position_except_pop(r"CF\recommend_by_item.txt")
    # top_N_except_pop(r"CF\recommend_by_item.txt")
    # av_position_except_pop(r"MD\hs.txt")
    # top_N_except_pop(r"MD\hs.txt")
    # av_position_except_pop(r"MD\md.txt")
    # top_N_except_pop(r"MD\md.txt")
    # av_position_except_pop(r"ML\recommend_extract_direct.txt")
    # top_N_except_pop(r"ML\recommend_extract_direct.txt")
    # av_position_except_pop(r"ML\recommend_extract_direct_rbf_C0.1_gamma0.0001.txt")
    # top_N_except_pop(r"ML\recommend_extract_direct_rbf_C0.1_gamma0.0001.txt")
    # av_position_except_pop(r"ML\recommend_extract_direct_rbf_C0.1_gamma0.1.txt")
    # top_N_except_pop(r"ML\recommend_extract_direct_rbf_C0.1_gamma0.1.txt")
    # av_position_except_pop(r"ML/xgboost_result/direct.txt")
    # top_N_except_pop(r"ML/xgboost_result/direct.txt")
    # av_position_except_pop(r"CN/cn_route_3.txt")
    # top_N_except_pop(r"CN/cn_route_3.txt")
