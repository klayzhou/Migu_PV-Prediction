import json
import os
import numpy
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor

def GBDT():
    data_path = '../dataset_3.0/data/'
    target_path = '../dataset_3.0/target/'
    files = os.listdir(data_path)
    data = []
    target = []
    for iter in files:
        if os.path.isdir(os.path.join(data_path, iter)):
            continue
        data_file = os.path.join(data_path, iter)
        print(data_file)
        with open(data_file, 'r', encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                data.append(item)
        target_file = os.path.join(target_path, iter)
        with open(target_file, 'r', encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                target.append(item)

    data = numpy.array(data)
    target = numpy.array(target)

    data_max = numpy.max(data, axis=0)  # axis=0 -> max value of each column
    data_max[data_max == 0] = 1
    data_min = numpy.min(data, axis=0)
    data = (data - data_min) / (data_max - data_min)
    data = numpy.nan_to_num(data)

    gbdt = GradientBoostingRegressor(loss='ls',n_estimators=100,learning_rate=0.1,max_depth=1,random_state=0)
    score = cross_val_score(gbdt, data, target, cv=5,scoring='neg_mean_squared_error')
    print(score)


def Lasso_Regression():
    data_path = '../dataset_actors/data/'
    target_path = '../dataset_actors/target/'
    files = os.listdir(data_path)
    data = []
    target = []
    for iter in files:
        if os.path.isdir(os.path.join(data_path, iter)):
            continue
        data_file = os.path.join(data_path, iter)
        print(data_file)
        with open(data_file, 'r', encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                data.append(item)
        target_file = os.path.join(target_path, iter)
        with open(target_file, 'r', encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                target.append(item)

    data = numpy.array(data)
    target = numpy.array(target)

    data_max = numpy.max(data, axis=0)  # axis=0 -> max value of each column
    data_max[data_max == 0] = 1
    data_min = numpy.min(data, axis=0)
    data = (data - data_min) / (data_max - data_min)
    data = numpy.nan_to_num(data)
    # return data,target
    print('train begin')
    model_Lasso = Lasso(alpha=0.1)
    score = cross_val_score(model_Lasso, data, target, cv=5,scoring='neg_mean_squared_error')
    print(score)
    

def Linear_Regression():
    data_path = '../dataset_3.0/data/'
    target_path = '../dataset_3.0/target/'
    files = os.listdir(data_path)
    data = []
    target = []
    for iter in files:
        if os.path.isdir(os.path.join(data_path, iter)):
            continue
        data_file = os.path.join(data_path, iter)
        with open(data_file,'r',encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                data.append(item)
        target_file = os.path.join(target_path, iter)
        with open(target_file,'r',encoding='UTF-8') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                target.append(item)
    
    data = numpy.array(data)    
    target = numpy.array(target)
    
    data_max = numpy.max(data,axis=0)#axis=0 -> max value of each column
    data_max[data_max==0]=1
    data_min = numpy.min(data,axis=0)
    data = (data - data_min)/(data_max-data_min)
    data = numpy.nan_to_num(data)
    #return data,target   
    model_LinearRegression = LinearRegression()
    score =cross_val_score(model_LinearRegression,data,target,cv=5)
    #score = mean_squared_error(numpy.zeros(200000), target[:200000])
    print(score)
    #print(predicted[predicted>100000])
    #print(predicted[:100], target[:100])

def test_sklearn():
    from sklearn.datasets import load_boston
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    model_LinearRegression = LinearRegression()
    iris=load_boston()
    print(iris)
    X=iris.data
    y=iris.target
    from sklearn.model_selection import cross_val_score
    scores=cross_val_score(model_LinearRegression,X,y,cv=5,scoring='neg_mean_squared_error')
    print(scores)

if __name__ == '__main__':
    Lasso_Regression()
