#! usr/bin/env python3
# -*- coding:utf-8 -*-
from sklearn import svm
from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV
from postgresql import get_conn, get_node_id_dict
from ML.init_graph import init_graph, AName, VName, my_weight, get_a_nodes, get_v_nodes
from ML.feature import extract_direct, extract_indirect, degrees
from networkx.algorithms import  bipartite
import time
import numpy as np
import json


def project(graph, nodes):
    """
    对图进行投影
    :param graph:
    :param nodes:
    :return:
    """
    prj_graph = bipartite.generic_weighted_projected_graph(graph, nodes, weight_function=my_weight)
    for node in prj_graph.nodes:
        prj_graph.nodes[node]["weight"] = degrees(prj_graph, node)
    return prj_graph


def train_test(extract_fun, kernel="rbf"):
    """
    调参
    :param extract_fun:
    :param kernel:
    :return:
    """
    f = open("param_" + extract_fun.__name__ + ".txt", "r", encoding="utf-8")
    x_list = f.readline()
    x_list.split()
    y_list = f.readline()
    y_list.split()
    f.close()
    x_list = json.loads(x_list)
    y_list = json.loads(y_list)
    print(len(x_list))
    print(len(y_list))
    print("读取参数结束")

    # 调参
    # tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 1e-2, 1e-1],
    #                      'C': [0.1, 1, 10, 100, 1000]},
    #                     {'kernel': ['linear'], 'C': [0.1, 1, 10, 100, 1000]}]
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 1e-2, 1e-1],
                         'C': [0.05, 0.1, 1, 10, 100, 1000]}]

    for score in ['precision', 'recall']:
        clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=5,
                           scoring='%s_macro' % score)
        print("开始训练")
        clf.fit(np.array(x_list), np.array(y_list))

        # 再调用 clf.best_params_ 就能直接得到最好的参数搭配结果
        print(clf.best_params_)

    # print("训练结束，保存模型")
    # joblib.dump(clf, "model_"+kernel+"_"+extract_fun.__name__+".pkl")



def train(extract_fun):
    """
    训练模型
    :param: extract_fun
    :return:
    """
    # 读取数据
    conn = get_conn()
    cursor = conn.cursor()

    # 二分网络
    graph = init_graph()
    print("构建二分网络完成")
    print(time.time())
    # 进行投影
    v_nodes = get_v_nodes()
    a_nodes = get_a_nodes()
    prjv_graph = project(graph, v_nodes)
    prja_graph = project(graph, a_nodes)
    print("网络投影完成")
    print(time.time())

    sql = "select * from public.ml_train_set"
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(len(rows))

    # 保存训练数据
    X_list = list()
    Y_list = list()

    i = 0
    for row in rows:
        user_id = VName(row[0])
        att_id = AName(row[1])

        i += 1
        print(i)
        # print(time.time())

        if extract_fun.__name__ == "extract_direct":
            feature = extract_direct(graph, user_id, att_id)
        elif extract_fun.__name__ == "extract_indirect":
            feature = extract_indirect(graph, prjv_graph, prja_graph, user_id, att_id)
            # print(feature)
        else:
            print("wrong function")
            break
        X_list.append(feature)
        if row[4]:
            Y_list.append(1)
        else:
            Y_list.append(-1)
    print("生成训练数据")
    print(time.time())

    cursor.close()
    conn.close()

    # 记录X_list， Y_list
    f = open("param_"+ extract_fun.__name__ +".txt", "w", encoding="utf-8")
    f.writelines(json.dumps(X_list) + "\n")
    f.writelines(json.dumps(Y_list) + "\n")
    f.close()
    print("训练数据保存成功")
    print(time.time())

    clf = svm.SVC(kernel="linear")
    clf.fit(X_list, Y_list)
    print("训练数据结束")
    print(time.time())

    joblib.dump(clf, "model_"+extract_fun.__name__+".pkl")
    print("保存模型")
    print(time.time())


def predict(extract_fun):
    """
    对结果进行预测
    :param extract_fun:
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 恢复模型
    clf = joblib.load( "model_" + extract_fun.__name__ + ".pkl")

    # 二分网络
    graph = init_graph()
    print("构建二分网络完成")
    print(time.time())
    # 进行投影
    v_nodes = get_v_nodes()
    a_nodes = get_a_nodes()
    prjv_graph = project(graph, v_nodes)
    prja_graph = project(graph, a_nodes)
    print("投影完成")
    print(time.time())

    sql = "select * from public.ml_test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    f = open("predict_"+extract_fun.__name__+".txt", "w", encoding="utf-8")
    for row in rows:
        user_id = VName(row[0])
        att_id = AName(row[1])
        is_link = row[4]
        if extract_fun.__name__ == "extract_direct":
            feature = extract_direct(graph, user_id, att_id)
        elif extract_fun.__name__ == "extract_indirect":
            feature = extract_indirect(graph, prjv_graph, prja_graph, user_id, att_id)

        result = clf.predict([feature])[0]
        f.writelines("%s\t%s\t%s\t%s\n" % (user_id, att_id, is_link, result))

    f.close()
    cursor.close()
    conn.close()


def recommend_list(extract_fun):
    """
    利用之前生成的模型 进行推荐
    :param extract_fun:
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 读数据
    sql = "select * from public.ml_test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 读模型
    clf = joblib.load( "model_" + extract_fun.__name__ + ".pkl")

    # 二分网络
    graph = init_graph()
    print("构建二分网络完成")
    print(time.time())
    # 进行投影
    v_nodes = get_v_nodes()
    a_nodes = get_a_nodes()
    prjv_graph = project(graph, v_nodes)
    prja_graph = project(graph, a_nodes)
    print("投影完成")
    print(time.time())
    # 所有的景点
    a_nodes = list(get_node_id_dict().keys())

    # 记录结果数据
    f = open("recommend_"+extract_fun.__name__+".txt", "w", encoding="utf-8")

    for row in rows:
        user_id = VName(row[0])
        att_id = AName(row[1])
        is_link = row[4]

        if not is_link:
            continue

        sql = "select classroute from public.route_0320 where id={user_id}".format(user_id=row[0])
        cursor.execute(sql)
        result = cursor.fetchone()
        classroute = result[0]

        # 待预测的集合
        left_set = set(a_nodes) - set(classroute[0:-1])

        recommendation = dict()
        for anode in left_set:
            anode = AName(anode)
            if extract_fun.__name__ == "extract_direct":
                feature = extract_direct(graph, user_id, anode)
            elif extract_fun.__name__ == "extract_indirect":
                feature = extract_indirect(graph, prjv_graph, prja_graph, user_id, anode)

            result = clf.predict([feature])[0]
            dis = abs(clf.decision_function([feature]))
            if result == 1:
                recommendation[anode] = dis[0]

        recommendation = dict(sorted(recommendation.items(), key=lambda x:x[1], reverse=True))
        f.write("%s\t%s\t%s\t%s\n" % (user_id, classroute[:-1], att_id, json.dumps(recommendation)))

    f.close()
    cursor.close()
    conn.close()


def test():
    # 读模型
    clf = joblib.load("model_" +"extract_indirect"+ ".pkl")

    result = clf.predict([[3, 52, 2, 0.03508771929824561, 0.8957294239399778, 156, 1, 1084, 51, 0.31477139507620167, 0.46875, 268.96004159072316, 15.232727280906579, 50802780, 7698866]])
    print(result)


def recommend_test(extract_fun, tuned_params):
    """
    根据GridSearchCV求得的参数  检验调参结果
    :param tuned_params:
    :return:
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 读数据
    sql = "select * from public.ml_test_set"
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 构建模型
    clf = svm.SVC(kernel=tuned_params["kernel"], C=tuned_params["C"], gamma=tuned_params["gamma"])
    f = open("param_" + extract_fun.__name__ + ".txt", "r", encoding="utf-8")
    x_list = f.readline()
    x_list.split()
    y_list = f.readline()
    y_list.split()
    f.close()
    x_list = json.loads(x_list)
    y_list = json.loads(y_list)
    clf.fit(x_list, y_list)


    # 二分网络
    graph = init_graph()
    print("构建二分网络完成")
    print(time.time())
    # 进行投影
    v_nodes = get_v_nodes()
    a_nodes = get_a_nodes()
    prjv_graph = project(graph, v_nodes)
    prja_graph = project(graph, a_nodes)
    print("投影完成")
    print(time.time())
    # 所有的景点
    a_nodes = list(get_node_id_dict().keys())

    # 记录结果数据
    f = open("recommend_" + extract_fun.__name__+"_" +tuned_params["kernel"]+"_C" +str(tuned_params["C"])+"_gamma"+ str(tuned_params["gamma"]) + ".txt", "w", encoding="utf-8")

    i = 0
    for row in rows:
        i += 1
        print(i)
        user_id = VName(row[0])
        att_id = AName(row[1])
        is_link = row[4]

        if not is_link:
            continue

        sql = "select classroute from public.route_0320 where id={user_id}".format(user_id=row[0])
        cursor.execute(sql)
        result = cursor.fetchone()
        classroute = result[0]

        # 待预测的集合
        left_set = set(a_nodes) - set(classroute[0:-1])

        recommendation = dict()
        for anode in left_set:
            anode = AName(anode)
            if extract_fun.__name__ == "extract_direct":
                feature = extract_direct(graph, user_id, anode)
            elif extract_fun.__name__ == "extract_indirect":
                feature = extract_indirect(graph, prjv_graph, prja_graph, user_id, anode)

            result = clf.predict([feature])[0]
            dis = abs(clf.decision_function([feature]))
            if result == 1:
                recommendation[anode] = dis[0]

        recommendation = dict(sorted(recommendation.items(), key=lambda x: x[1], reverse=True))
        f.write("%s\t%s\t%s\t%s\n" % (user_id, classroute[:-1], att_id, json.dumps(recommendation)))

    f.close()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # # train(extract_direct)
    # train(extract_indirect)
    # # predict(extract_direct)
    # predict(extract_indirect)
    # recommend_list(extract_direct)
    # recommend_list(extract_indirect)
    # train_test(extract_direct, "rbf")
    # recommend_test(extract_direct, {'C': 0.1, 'gamma': 0.0001, 'kernel': 'rbf'})
    # recommend_test(extract_direct, {'C': 0.1, 'gamma': 0.1, 'kernel': 'rbf'})
    recommend_test(extract_indirect, {'C': 0.1, 'gamma': 0.001, 'kernel': 'rbf'})
    recommend_test(extract_indirect, {'C': 1, 'gamma': 0.01, 'kernel': 'rbf'})


