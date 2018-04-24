#! usr/bin/env python
# -*- coding:utf-8 -*-


def evaluate_prediction(file):
    """
    对机器学习的预测结果进行评价
    :param file: 文件路径
    :return: 返回precision,recall, F1
    precision = tp / predicted positive examples
    recall = tp / real positive examples
    F1 = 2 * (precision*recall / (precision + recall))
    """
    f = open(file, "r", encoding="utf-8")
    tp = 0  # true positive examples
    pp = 0
    rp = 0


    for line in f:
        line = line.strip()
        lst = line.split("\t")
        # print(lst)
        islink = lst[2]
        pred_result = int(lst[3])
        if islink == str(True):
            rp += 1
        if pred_result == 1:
            pp += 1
        if islink == str(True) and pred_result ==1:
            tp += 1

    precision = tp / pp
    recall = tp / rp
    F1 = 2 * precision * recall / (precision + recall)
    return precision, recall, F1


if  __name__ == "__main__":
    print(evaluate_prediction("predict_extract_direct.txt"))