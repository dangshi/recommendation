#! usr/bin/env python
# -*- coding:utf-8 -*-
import sys
sys.path.append("../")
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from postgresql import get_conn, get_node_id_dict
from ML.init_graph import VName, AName
import json
from lib.encoder import MyEncoder
from xgboost.sklearn import XGBClassifier
from sklearn.grid_search import GridSearchCV


params = {
        'booster': 'gbtree',
        'objective': 'binary:logistic',  # 二分类的问题
        # 'num_class': 10,  # 类别数，与 multisoftmax 并用
        'gamma': 0.1,  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
        'max_depth': 2,  # 构建树的深度，越大越容易过拟合
        'alpha':1 ,  # L1
        'lambda': 0.1,  # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
        'subsample': 0.8,  # 随机采样训练样本
        'colsample_bytree': 0.8,  # 生成树时进行的列采样
        'min_child_weight': 2,
        # 这个参数默认是 1，是每个叶子里面 h 的和至少是多少，对正负样本不均衡时的 0-1 分类而言
        # ，假设 h 在 0.01 附近，min_child_weight 为 1 意味着叶子节点中最少需要包含 100 个样本。
        # 这个参数非常影响结果，控制叶子节点中二阶导的和的最小值，该参数值越小，越容易 overfitting。
        'silent': 0,  # 设置成1则没有运行信息输出，最好是设置为0.
        'eta': 0.1,  # 如同学习率
        'seed': 0,
        # 'eval_metric': 'auc'
    }


def train_model(train_file, model_name):
    train_data = pd.read_csv(train_file)

    # 用sklearn.cross_validation进行训练数据集划分，这里训练集和交叉验证集比例为7：3
    train_xy, val = train_test_split(train_data, test_size=0.3, random_state=1)

    y = train_xy.label
    X = train_xy.drop(['label'], axis=1)
    val_y = val.label
    val_X = val.drop(['label'], axis=1)

    # xgb矩阵赋值
    xgb_val = xgb.DMatrix(val_X, label=val_y)
    xgb_train = xgb.DMatrix(X, label=y)

    num_rounds = 200  # 迭代次数
    watchlist = [(xgb_train, 'train'), (xgb_val, 'val')]

    # 训练模型并保存
    # early_stopping_rounds 当设置的迭代次数较大时，early_stopping_rounds 可在一定的迭代次数内准确率没有提升就停止训练
    model = xgb.train(params, xgb_train, num_rounds, watchlist)
    model.save_model('xgboost_result/'+model_name+'.model')  # 用于存储训练出的模型


def recommend(test_file, model_path, save_file):
    """
    根据上面生成的模型
    进行预测推荐
    :param model_path:
    :return:
    """
    # 加载模型
    model = xgb.Booster()
    model.load_model(model_path)
    # print(dir(model))

    # 构造训练集数据
    test_data = pd.read_csv(test_file)
    anode_list = list(test_data["anode"])
    test_set = test_data.drop("anode", axis=1)
    # xgb矩阵赋值
    xgb_test = xgb.DMatrix(test_set)

    # 进行预测
    preds = model.predict(xgb_test)

    conn = get_conn()
    cursor = conn.cursor()
    sql = "select * from public.ml_test_set "
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 所有的景区节点
    a_nodes = list(get_node_id_dict().keys())

    index = 0
    f = open(save_file, "w", encoding="utf-8")
    for row in rows:
        user_id = VName(row[0])
        att_id = AName(row[1])
        is_link = row[4]

        # 对于测试的负案例 直接跳过
        if not is_link:
            continue

        sql = "select classroute from public.route_0320 where id={user_id}".format(user_id=row[0])
        cursor.execute(sql)
        result = cursor.fetchone()
        classroute = result[0]

        # 待预测的集合
        left_set = set(a_nodes) - set(classroute[0:-1])
        n = len(left_set)

        recommend_list = dict()
        for i in range(n):
            recommend_list[anode_list[index+i]] = preds[index+i]
        index += n

        recommend_list = dict(sorted(recommend_list.items(), key=lambda x:x[1], reverse=True))
        f.write("%s\t%s\t%s\t%s\n" % (user_id, classroute[:-1], att_id, json.dumps(recommend_list, cls=MyEncoder)))

    f.close()
    cursor.close()
    conn.close()


def tunning(train_file):
    """
    进行调参
    :param train_file:
    :return:
    """
    train_data = pd.read_csv(train_file)
    Y = np.array(train_data.label)
    X = np.array(train_data.drop(['label'], axis=1).ix[:,1:])
    # print(Y)
    # print(X)

    # cv_params = {'n_estimators': [100, 150 , 200]}
    # other_params = {'learning_rate': 0.1,  'max_depth': 5, 'min_child_weight': 1, 'seed': 0,
    #                 'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1,
    #                 'booster': 'gbtree', 'objective': 'binary:logistic' }
    # cv_params = {'max_depth': [1, 2, 3, 4, 5, 6, 7], 'min_child_weight': [1, 2, 3, 4, 5, 6]}
    # other_params = {'learning_rate': 0.1, 'n_estimators': 100, 'min_child_weight': 1, 'seed': 0,
    #                 'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

    # cv_params = {'gamma': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]}
    # other_params = {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 2, 'min_child_weight': 2, 'seed': 0,
    #                 'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

    # cv_params = {'subsample': [0.6, 0.7, 0.8, 0.9], 'colsample_bytree': [0.6, 0.7, 0.8, 0.9]}
    # other_params = {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 2, 'min_child_weight': 2, 'seed': 0,
    #                 'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0.1, 'reg_alpha': 0, 'reg_lambda': 1}

    # cv_params = {'reg_alpha': [0.05, 0.1, 1, 2, 3], 'reg_lambda': [0.05, 0.1, 1, 2, 3]}
    # other_params = {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 2, 'min_child_weight': 2, 'seed': 0,
    #                 'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0.1, 'reg_alpha': 0, 'reg_lambda': 1}

    cv_params = {'learning_rate': [0.01, 0.05, 0.07, 0.1, 0.2]}
    other_params = {'learning_rate': 0.1, 'n_estimators': 100, 'max_depth': 2, 'min_child_weight': 2, 'seed': 0,
                    'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0.1, 'reg_alpha': 1, 'reg_lambda': 0.1}

    model = xgb.XGBClassifier(**other_params)
    optimized_GBM = GridSearchCV(estimator=model, param_grid=cv_params, scoring='accuracy', cv=5, verbose=1, n_jobs=4)
    optimized_GBM.fit(X, Y)
    evalute_result = optimized_GBM.grid_scores_
    print('每轮迭代运行结果:{0}'.format(evalute_result))
    print('参数的最佳取值：{0}'.format(optimized_GBM.best_params_))
    print('最佳模型得分:{0}'.format(optimized_GBM.best_score_))

if __name__ == "__main__":
    train_model("extract_indirect_train.csv", "indirect")
    recommend("extract_indirect_test.csv",'xgboost_result/indirect.model', "xgboost_result/indirect.txt")
    # tunning("extract_indirect_train.csv")