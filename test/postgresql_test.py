#! usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
sys.path.append("../")
from postgresql import get_conn, get_node_id_dict

if __name__=="__main__":
    conn = get_conn()
    cursor = conn.cursor()

    print(get_node_id_dict())
