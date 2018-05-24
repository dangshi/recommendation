#! usr/bin/env python3
# -*- coding:utf-8 -*-

from math import radians, cos, sin, asin, sqrt
# from math import *


def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）
    # 将十进制度数转化为弧度
    # math.degrees(x):为弧度转换为角度
    # math.radians(x):为角度转换为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin( dlat /2 ) **2 + cos(lat1) * cos(lat2) * sin( dlon /2 ) **2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r*1000


if __name__=='__main__':
    a=haversine(103.85012,36.03653,103.84085,36.03842)
    print(a)