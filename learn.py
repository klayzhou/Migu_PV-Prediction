# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 从dataset下读取数据x和y，进行简单的预处理后，返回可用于直接训练的x和y
2. 使用不同的模型对x和y进行交叉验证
"""

import json
import os
import numpy
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, LogisticRegression
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import mean_squared_error, classification_report, precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler

"""
获取数据x和y
"""
def get_data():
    data = None
    target = None
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'data.txt'), 'r', encoding='UTF-8') as fread:
        res = fread.read()
        data = json.loads(res)
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'target.txt'), 'r', encoding='UTF-8') as fread:
        res = fread.read()
        target = json.loads(res)
   
    
    data = numpy.array(data, dtype = 'float64')    
    target = numpy.array(target, dtype='int')

    data_max = numpy.max(data,axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data,axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)
    train_data,test_data,train_target,test_target = train_test_split(data,target,test_size=0.3,random_state=1)
    count = Counter(train_target)
    print(count)
    train_data, train_target = SMOTE().fit_sample(train_data, train_target) 
    count = Counter(train_target)
    print(count)
    return test_data, test_target, train_data, train_target


"""
线性回归
"""
def Linear_Regression():
    data, target = get_data()
    model_LinearRegression = LinearRegression()
    score =cross_val_score(model_LinearRegression,data,target,cv=5,scoring='roc_auc')
    print(str(len(target)))
    print(score)


"""
逻辑斯蒂分类
"""
def Logistic_Regression():
    test_data, test_target, train_data, train_target = get_data()
    model_LogisticRegression = LogisticRegression()
    model_LogisticRegression.fit(train_data,train_target)
    predicted_target = model_LogisticRegression.predict(test_data)
    #print(precision_recall_fscore_support(test_target, predicted_target, average=None, labels=[0,1,2,3,4]))
    #print(classification_report(test_target, predicted_target))
    #predicted_target = cross_val_predict(model_LogisticRegression, train_data , train_target, cv=5)
    print(classification_report(test_target, predicted_target)) 


def RFC():
    test_data, test_target, train_data, train_target = get_data()
    model_rfc = RandomForestClassifier(n_estimators=100, criterion='gini')
    model_rfc.fit(train_data, train_target)
    predicted_target = model_rfc.predict(test_data)
    print(classification_report(test_target,predicted_target))

if __name__ == '__main__':
    Logistic_Regression()
