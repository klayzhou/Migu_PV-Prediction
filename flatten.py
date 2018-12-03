# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 从feature_1.0下读取数据，根据要求制作数据集x和y，存放到dataset文件夹下
"""

import os
import json
import math
import numpy
import imp
from sklearn.externals import joblib

"""
数据过滤条件，可自定义，只要目标数据在此函数中返回True即可
"""


def judge(PV):
    if int(PV) < 10:
        return False
    return True

"""
pv到类别的对应关系，可自定义
0.1 0.2 4 18 78
"""
def get_class(pv_str):
    pv = int(pv_str)
    
    if pv<10:
        return 0
    elif pv < 100:
        return 1
    elif pv < 500:
        return 2
    elif pv < 1000:
        return 3
    else:
        return 4


"""
生成数据x和y
file_list：要遍历的特征文件的list，可以选取1-21中的任意多个文件
feature_list：要使用的特征索引的list，一共12个特征，特征索引（0-11）和特征名字的对应关系如下
0--displaytype
1--formtype
2--duration
3--主题_one_hot
4--program_type
5-演员_one_hot
6-时间vector
7-时间数
8-星期数
9-创建时间间隔
10-上映时间间隔
11-历史pv
12-pv
"""
def flatten(file_list):
    flatten_data = []
    flatten_target = []

    count = 0
    for index in file_list:
        print('file ' + str(index) + ' is processing')
        with open(os.path.join(os.path.abspath('..'), 'feature_1.0', str(index) + '.txt'), 'r', encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            
            for item in res:
                #if not judge(res[item][16]):
                #    continue
                if int(res[item][0]) != 1:
                    continue
                count = count + 1
                tmp = []
                tmp.extend(res[item][6])
                tmp.append(res[item][11])
                flatten_data.append(tmp)
                flatten_target.append(int(res[item][12]))
                   
    '''target = list(flatten_target)
    target.sort(reverse=True)
    level1 = int(len(target)*0.001)
    level2 = int(len(target)*0.003)
    level3 = int(len(target)*0.043)
    level4 = int(len(target)*0.243)
    print(str(target[0]) + ' ' + str(target[len(target)-1]))
    print(str(target[level1]) + ' ' + str(target[level2]) + ' ' + str(target[level3]) + ' ' + str(target[level4]))
    for i in range(len(flatten_target)):
        if flatten_target[i] < target[level4]:
            flatten_target[i] = 0 
        elif flatten_target[i] < target[level3]:
            flatten_target[i] = 1
        elif flatten_target[i] < target[level2]:
            flatten_target[i] = 2
        elif flatten_target[i] < target[level1]:
            flatten_target[i] = 3
        else:
            flatten_target[i] = 4'''
    
    print(count)
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'data.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(flatten_data, ensure_ascii=False))
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'target.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(flatten_target, ensure_ascii=False))

def flatten_incomplete(file_list, feature_list):
    incomplete_data = []
    incomplete_target = []
    for index in file_list:
        print('file ' + str(index) + ' is processing')
        with open(os.path.join(os.path.abspath('..'), 'knn_feature', str(index) + '.txt'), 'r',
                  encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)

            for item in res:
                tmp = []
                for i in feature_list:
                    if i == 10:
                        res[item][i] = res[item][i][0:300]
                    if i == 13 or i == 14:
                        res[item][i] = math.exp(-1 * res[item][i])
                    if isinstance(res[item][i], list):
                        tmp.extend(res[item][i])
                    else:
                        tmp.append(res[item][i])
                incomplete_data.append(tmp)
                incomplete_target.append(get_class(res[item][15]))

    data = numpy.array(incomplete_data, dtype='float64')
    data_max = numpy.max(data,axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data,axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)

    save_path_name = '../feature_1.0/' + 'KNN_model.m'
    model = joblib.load(save_path_name)

    predicted = model.predict(data)

    data = data.tolist()

    complete_data = []
    count = 0
    for item in data:
        tmp = item
        tmp.append(predicted[count])
        count = count + 1
        complete_data.append(tmp)

    print(len(complete_data))

    with open(os.path.join(os.path.abspath('..'), 'dataset', 'data_waiting.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(complete_data, ensure_ascii=False))

    with open(os.path.join(os.path.abspath('..'), 'dataset', 'target_waiting.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(incomplete_target, ensure_ascii=False))


if __name__ == '__main__':

    #flatten([1,2])
    flatten([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21])




