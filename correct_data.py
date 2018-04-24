#! usr/bin/env python3
# -*- coding:utf-8 -*-
"""
在route表中，对于classroute， 一天之内会重复计算多个景点
该脚本用于去除重复的数据
"""
from postgresql import get_conn


def is_same_day(d1, d2):
    """
    判断两个日期是否为同一天
    :return: true/false
    """
    if d1.year==d2.year and d1.month==d2.month and d1.day==d2.day:
        return True
    else:
        return False


def correct_data():
    conn = get_conn()
    cursor = conn.cursor()

    select_sql = r"select * from public.route"
    cursor.execute(select_sql)
    rows = cursor.fetchall()

    for row in rows:
        line = dict()
        line["id_base64"] = row[0]
        line["route"] = row[1]
        line["classroute"] = row[2]
        line["classroutestr"] = row[3]
        line["routetime"] = row[4]
        line["starttime"] = row[5]
        line["endtime"] = row[6]
        line["id"] = row[7]
        line["route_length"] = row[8]

        # 轨迹为空 跳过
        if not line["classroute"]:
            continue

        classroute = [line["classroute"][0]]
        classroutestr = [line["classroutestr"][0]]
        routetime = [line["routetime"][0]]

        for i in range(len(line["classroute"]) - 1):
            if line["classroute"][i+1] not in classroute:
                classroute.append(line["classroute"][i+1])
                classroutestr.append((line["classroutestr"][i+1]))
                routetime.append(line["routetime"][i+1])
            else:
                for j in range(len(classroute)):
                    if classroute[j] == line["classroute"][i+1]:
                        index = j
                if is_same_day(routetime[index], line["routetime"][i+1]):
                    continue
                else:
                    classroute.append(line["classroute"][i + 1])
                    classroutestr.append((line["classroutestr"][i + 1]))
                    routetime.append(line["routetime"][i + 1])

        line["classroute"] = classroute
        line["classroutestr"] = classroutestr
        line["routetime"] = routetime

        insert_sql = """
                    insert into public.route_0320(id_base64,route, classroute, classroutestr, routetime, starttime,
                            endtime, id, route_length) values(%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        cursor.execute(insert_sql, (line["id_base64"], line["route"], line["classroute"], line["classroutestr"],
                                    line["routetime"], line["starttime"], line["endtime"], line["id"], line["route_length"]))
        conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    correct_data()
