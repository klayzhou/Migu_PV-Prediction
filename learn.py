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
from sklearn.metrics import mean_squared_error, classification_report, precision_recall_fscore_support
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler, SMOTE 
from imblearn.under_sampling import RandomUnderSampler
from imblearn.ensemble import BalancedBaggingClassifier, BalancedRandomForestClassifier
from tensorflow import keras

"""
获取数据x和y
"""
def get_data():
    data = []
    target = []
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'data.txt'), 'r', encoding='UTF-8') as fread:
        res = fread.read()
        data = json.loads(res)
    with open(os.path.join(os.path.abspath('..'), 'dataset', 'target.txt'), 'r', encoding='UTF-8') as fread:
        res = fread.read()
        target = json.loads(res)
          
    with open(os.path.join(os.path.abspath('..'),'dataset','data_waiting.txt'),'r',encoding='UTF-8') as fread:
        res = fread.read()
        data.extend(json.loads(res))

    with open(os.path.join(os.path.abspath('..'),'dataset','target_waiting.txt'),'r',encoding='UTF-8') as fread:
        res = fread.read()
        target.extend(json.loads(res))
    
    data = numpy.array(data, dtype = 'float64')    
    target = numpy.array(target, dtype='int')

    data_max = numpy.max(data, axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data, axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)
    train_data,test_data,train_target,test_target = train_test_split(data,target,test_size=0.3,random_state=1)
    count = Counter(train_target)
    print(count)
    return test_data, test_target, train_data, train_target

"""
逻辑斯蒂分类
"""
def Logistic_Regression():
    test_data, test_target, train_data, train_target = get_data()
    model_LogisticRegression = LogisticRegression()
    model_LogisticRegression.fit(train_data,train_target)
    print(model_LogisticRegression.coef_)
    predicted_target = model_LogisticRegression.predict(test_data)
    print(classification_report(test_target, predicted_target)) 


def RFC():
    test_data, test_target, train_data, train_target = get_data()
    model_rfc = BalancedBaggingClassifier(n_estimators=100, base_estimator=DecisionTreeClassifier(), sampling_strategy='auto',replacement=False,random_state=0)
    model_rfc.fit(train_data, train_target)
    predicted_target = model_rfc.predict(test_data)
    print(classification_report(test_target,predicted_target))

def nn():
    test_data, test_target, train_data, train_target = get_data()
    target = keras.utils.to_categorical(train_target)
    model = keras.Sequential()
    model.add(keras.layers.Dense(300, activation='relu',input_shape=(train_data.shape[1],)))
    model.add(keras.layers.Dense(100, activation='relu'))
    model.add(keras.layers.Dense(40, activation='relu'))
    model.add(keras.layers.Dense(5, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_data, target,epochs=20,batch_size=100)
    predicted = model.predict(test_data)
    proba = numpy.argmax(predicted, axis=1)
    #label = numpy.where(proba=predicted)
    print(classification_report(test_target, proba))
    #print(proba)

if __name__ == '__main__':
    RFC()
