# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 从feature_1.0下读取数据，根据要求制作数据集x和y，存放到dataset文件夹下
"""

import os
import json
import math


"""
数据过滤条件
"""
def judge(data_feature_list):
    if int(data_feature_list[15]) < 10:
        return False
    return True


def get_class(pv_str):
    pv = int(pv_str)
    if pv < 13:
        return 6
    elif pv < 15:
        return 5
    elif pv < 20:
        return 4
    elif pv < 30:
        return 3
    elif pv < 50:
        return 0
    elif pv < 100:
        return 1
    else:
        return 2


"""
生成数据x和y
"""
def flatten(file_list, feature_list):
    flatten_data = []
    flatten_target = []
    for index in file_list:
        print('file ' + str(index) + ' is processing')
        with open(os.path.join(os.path.abspath('..'), 'feature_1.0', str(index) + '.txt'), 'r', encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            
            for item in res:
                if not judge(res[item]):
                    continue
                tmp = []
                for i in feature_list:
                    if isinstance(res[item][i],list):
                        tmp.extend(res[item][i])
                    else:
                        tmp.append(res[item][i])
                flatten_data.append(tmp)
                flatten_target.append(get_class(res[item][15]))

    
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'data.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(flatten_data, ensure_ascii=False))
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'target.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(flatten_target, ensure_ascii=False))




if __name__ == '__main__':
    flatten([1],[2,3,4])

