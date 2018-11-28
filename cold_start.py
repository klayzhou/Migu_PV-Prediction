# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 从feature_1.0下读取数据，根据要求制作数据集x和y，存放到dataset文件夹下
"""

import os
import json
import math
import numpy
from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsRegressor
from sklearn import linear_model


"""
数据过滤条件，可自定义，只要目标数据在此函数中返回True即可
"""
def judge(data_feature_list):
    if int(data_feature_list[15]) < 10:
        return False
    return True

"""
生成数据x和y
file_list：要遍历的特征文件的list，可以选取1-21中的任意多个文件
feature_list：要使用的特征索引的list，特征索引和特征名字的对应关系如下
0--标题
1--createtime
2--displaytype_one_hot
3--formtype_one_hot
4--duration
5--detail
6--keywords
7--releasetime
8--主题_one_hot
9--program_type_one_hot
10-演员_one_hot
11-星期vector
12-24小时vector
13-创建时间间隔
14-上映时间间隔
15-上个小时的点击量
16--点击量
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
                if not judge(res[item]): # in practice useless
                    continue
                tmp = []

                for i in feature_list:
                    if i==10:
                        res[item][i] = res[item][i][0:300]
                    if i==13 or i==14:
                        res[item][i] = math.exp(-1*res[item][i])
                    if isinstance(res[item][i],list):
                        tmp.extend(res[item][i])
                    else:
                        tmp.append(res[item][i])
                flatten_data.append(tmp)
                flatten_target.append(res[item][15])

    data = numpy.array(flatten_data, dtype = 'float64')
    target = numpy.array(flatten_target, dtype='int')

    data_max = numpy.max(data,axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data,axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)
    return data, target

def Linear_Regression(data, target):
    model_LinearRegression = linear_model.Lasso(alpha=0.1)
    model_LinearRegression.fit(data, target)
    return model_LinearRegression

def KNN(data, target):
    regressor = KNeighborsRegressor(n_neighbors=4)
    regressor.fit(data, target)
    return regressor

def save_model(input):
     data, target = flatten([1,2,3,4,5],[2,3,4,8,9,10,11,12,13,14])
     save_path_name = '../feature_1.0/' + input + '_model.m'
     if 'Linear' in input:
         model = Linear_Regression(data, target)
         joblib.dump(model, save_path_name)
     else:
         model = KNN(data, target)
         joblib.dump(model, save_path_name)


if __name__ == '__main__':
    input = 'Linear'
    save_model(input)


