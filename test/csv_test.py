#! usr/bin/env python3
# -*- coding:utf-8 -*-
import pandas as pd
import xgboost as xgb
import numpy as np


if __name__ == "__main__":
    title = ["one", "two", "three"]
    rows = [[1,2,3], [4,5,6], [7,8,9]]
    df = pd.DataFrame(rows, columns=title)
    df.to_csv(r"test.csv")

    df = pd.read_csv("test.csv")
    l = df.one
    df = df.drop("one", axis=1)
    print(df)
    print(np.array(df.ix[:,1:]).tolist())
    # for i in l:
    #     print(i)
    print(np.array(l))