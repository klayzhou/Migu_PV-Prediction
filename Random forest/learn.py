# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 从dataset下读取数据x和y，进行简单的预处理后，返回可用于直接训练的x和y
2. 使用不同的模型对x和y进行交叉验证
"""

import time
import json
import os
import numpy
import imp
import math
from collections import Counter
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Lasso, LogisticRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error, classification_report, precision_recall_fscore_support, confusion_matrix, roc_auc_score

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import RandomOverSampler, SMOTE 
from imblearn.under_sampling import RandomUnderSampler
from imblearn.ensemble import BalancedBaggingClassifier, BalancedRandomForestClassifier
from tensorflow import keras
from sklearn.preprocessing import label_binarize
from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsRegressor

"""
获取数据x和y
"""
def get_data(data_dir, target_dir):
    data = []
    target = []
    data = numpy.loadtxt('../dataset/'+ data_dir)
    target = numpy.loadtxt('../dataset/'+ target_dir)
    
    data = numpy.array(data, dtype = 'float64')    
    target = numpy.array(target, dtype='int')

    data_max = numpy.max(data, axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data, axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)

    #train_data,test_data,train_target,test_target = train_test_split(data,target,test_size=0.3,random_state=1)
    #count = Counter(train_target)
    #print(count)

    return data, target

"""
try regression again 
"""
def Linear_Regression():
    test_data, test_target, train_data, train_target = get_data()
    model_LinearRegression = Lasso(alpha=0.1)
    model_LinearRegression.fit(train_data, train_target)
    predicted = model_LinearRegression.predict(test_data)
    print(mean_squared_error(predicted, test_target)) 
    print(predicted.tolist()[:30])
    print(test_target.tolist()[:30])
    # save_path_name = ''
    #joblib.dump(model, save_path_name)

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
    train_data, train_target = get_data('train_data.txt', 'train_target.txt')
    test_data, test_target = get_data('test_data.txt', 'test_target.txt')
    model_rfc = BalancedBaggingClassifier(n_estimators=100, base_estimator=DecisionTreeClassifier(), sampling_strategy='auto', replacement=False,random_state=0)

    model_rfc.fit(train_data, train_target)
    predicted_target = model_rfc.predict(test_data)
    print(classification_report(test_target,predicted_target))
    #行代表真实数据，列代表预测数据
    print(confusion_matrix(test_target,predicted_target, labels=[0,1,2,3,4], sample_weight=None))

def RFC_knn():
    train_data, train_target = get_data('knn_data.txt', 'train_target.txt')
    test_data, test_target = get_data('knn_test_data.txt', 'test_target.txt')
    model_rfc = BalancedBaggingClassifier(n_estimators=100, base_estimator=DecisionTreeClassifier(), sampling_strategy='auto', replacement=False,random_state=0)

    model_rfc.fit(train_data, train_target)
    predicted_target = model_rfc.predict(test_data)
    print(classification_report(test_target, predicted_target))
    #行代表真实数据，列代表预测数据
    print(confusion_matrix(test_target,predicted_target, labels=[0,1,2,3,4], sample_weight=None))

def KNN_train():
    print('knn model is training')
    train_data, train_target = get_data('knn_data.txt', 'knn_target.txt')

    model = KNeighborsRegressor(n_neighbors=1)
    model.fit(train_data[:, 24:], train_target)
    print('knn model is done')
    return model


def KNN_predict():
    print('knn model is testing')
    test_data, test_target = get_data('knn_test_data.txt', 'knn_test_target.txt')
    model = KNN_train()

    print(test_data.shape)
    predict_target = []
    start = time.time()
    num = test_data.shape[0]
    for i in range(math.ceil(num/1000)):
        print('round '+str(i))
        predict_lst = model.predict(test_data[1000*i:1000*(i+1), 24:])
        predict_target.extend(predict_lst)
        end = time.time()
        print(end-start)

    predict_target = numpy.array(predict_target).reshape(-1,1)
    print(predict_target.shape)

    target_max = numpy.max(predict_target)#axis=0 -> max value of each column
    target_min = numpy.min(predict_target)
    predict_target = (predict_target - target_min)/(target_max - target_min)
    predict_target = numpy.nan_to_num(predict_target)
    data = numpy.hstack((test_data[:,:24], predict_target))

    target = numpy.loadtxt('../dataset/test_target.txt')

    print('knn predict is done')
    return data, target


def coldstart():
    print('cold start is training')
    knn_data, knn_target = KNN_predict()

    train_data, train_target = get_data('train_data.txt', 'train_target.txt')
    print('train_target:')
    print(Counter(train_target))
    #test_data, test_target = get_data('test_data.txt', 'test_target.txt')
    model_rfc = BalancedBaggingClassifier(n_estimators=100, base_estimator=DecisionTreeClassifier(),
                                          sampling_strategy='auto', replacement=False, random_state=0)
    model_rfc.fit(train_data, train_target)

    predicted_target = model_rfc.predict(knn_data)
    print(classification_report(knn_target, predicted_target))
    # 行代表真实数据，列代表预测数据
    print(confusion_matrix(knn_target, predicted_target, labels=[0, 1, 2, 3, 4], sample_weight=None))



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
    RFC_knn()
    #Logistic_Regression()
