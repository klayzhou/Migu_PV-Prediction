import json
import os
import numpy
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import mean_squared_error

def Linear_Regression():
    data_path = '../dataset_2.0/data/tmp/'
    target_path = '../dataset_2.0/target/'
    files = os.listdir(data_path)
    data = []
    target = []
    for iter in files:
        data_file = os.path.join(data_path, iter)
        print(data_file)
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
    model_LinearRegression = LinearRegression().fit(data, target)
    print(model_LinearRegression.coef_)
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
    Linear_Regression()
