# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 从dataset下读取数据x和y，进行简单的预处理后，返回可用于直接训练的x和y
2. 使用不同的模型对x和y进行交叉验证
"""

import json
import os
import numpy
import imp
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
    train_data, train_target = get_data('data.txt', 'target.txt')
    test_data, test_target = get_data('test_data.txt', 'test_target.txt')
    model_rfc = BalancedBaggingClassifier(n_estimators=100, base_estimator=DecisionTreeClassifier(), sampling_strategy='auto', replacement=False,random_state=0)
    #return model_rfc
    #model_rfc = BalancedRandomForestClassifier(n_estimators=50, random_state=0)

    model_rfc.fit(train_data, train_target)
    predicted_target = model_rfc.predict(test_data)
    print(classification_report(test_target,predicted_target))
    #行代表真实数据，列代表预测数据
    print(confusion_matrix(test_target,predicted_target, labels=[0,1,2,3,4], sample_weight=None))
    #y_one_hot = label_binarize(test_target, numpy.arange(5))
    #print(roc_auc_score(y_one_hot,predicted_target, average='micro'))

def KNN_train():
    print('knn model is training')
    train_data = numpy.loadtxt('../dataset/'+ 'knn_data.txt')
    train_target = numpy.loadtxt('../dataset/'+ 'knn_target.txt')

    copy = train_data[:, 0:29] #no normalize
    data = train_data[:, 29:]
    data_max = numpy.max(data, axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data, axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)
    train_data = numpy.hstack((copy, data))

    data_dict = {}
    target_dict = {}
    num = train_data.shape[0]
    for index in range(num):
        item = train_data[index, :]
        key = str(item[0])+'_'+str(item[1])+'_'+str(item[2])
        if key not in data_dict:
            data_dict[key] = [item[29:]]
            target_dict[key] = [[train_target[index]]]
        else:
            data_dict[key].append(item[29:])
            target_dict[key].append(train_target[index])

    model_dict = {}
    for key in data_dict:
        neighbors = 4
        if len(data_dict[key])<4:
            neighbors = len(data_dict[key])
        data = numpy.array(data_dict[key])
        model = KNeighborsRegressor(n_neighbors=neighbors)
        model.fit(numpy.array(data), numpy.array(target_dict[key]))
        model_dict[key]= model

    print('knn model is done')
    return model_dict


def KNN_predict():
    print('knn model is testing')
    test_data = numpy.loadtxt('../dataset/'+ 'knn_test_data.txt')
    #test_target = numpy.loadtxt('../dataset/'+ 'knn_test_target.txt')

    copy = test_data[:, 0:29] #no normalize
    #print(copy.shape)
    data = test_data[:, 29:]
    data_max = numpy.max(data, axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data, axis=0)
    data = (data - data_min)/(data_max - data_min)
    data = numpy.nan_to_num(data)
    #print(data.shape)
    test_data = numpy.hstack((copy,data))
    #print(test_data.shape)


    predict_target = []
    data_dict = {}
    num = test_data.shape[0]
    for index in range(num):
        item = test_data[index, :]
        key = str(item[0])+'_'+str(item[1])+'_'+str(item[2])
        if key not in data_dict:
            data_dict[key] = []
        data_dict[key].append(item[3:])

    data, target = [], []
    test_target  = []
    predicted = []
    model_dict = KNN_train()
    for key in data_dict:
        if key in model_dict:
            model = model_dict[key]
            value = numpy.array(data_dict[key])
            tmp = model.predict(value[:, 26:])

            predicted.extend(tmp)
            test_target.extend(value[:, 24])

            tmp = tmp.reshape(-1, 1)
            tmp_data = value[:, :24]
            tmp_data = numpy.hstack((tmp_data, tmp))
            target.extend(value[:, 25])
            data.extend(tmp_data)
        else:
            tmp = numpy.array([[5] for i in range(value.shape[0])])
            tmp_data = value[:, :24]
            tmp_data = numpy.hstack((tmp_data, tmp))
            target.extend(value[:, 25])

            predicted.extend(tmp.reshape(-1))
            test_target.extend(value[:, 24])

            data.extend(tmp_data)

    print('mean squared error')
    print(mean_squared_error(numpy.array(predicted), numpy.array(test_target)))
    
    data = numpy.array(data)
    target = numpy.array(target)
    print('knn predict is done')
    return data, target


def coldstart():
    print('cold start is training')
    knn_data, knn_target = KNN_predict()

    data_max = numpy.max(knn_data, axis=0)  # axis=0 -> max value of each column
    data_max[data_max == 0] = 1
    data_min = numpy.min(knn_data, axis=0)
    data = (knn_data - data_min) / (data_max - data_min)
    knn_data = numpy.nan_to_num(data)

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
    KNN_predict()
    #Logistic_Regression()
