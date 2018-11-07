import json

def test():
    b = open(r"/home/PV_Prediction/renqingmei/dataset/1.txt", "r",encoding='UTF-8')
    out = b.read()
    out =  json.loads(out)
    return out

def test_sklearn():
    from sklearn.datasets import load_boston
    from sklearn.cross_validation import train_test_split
    from sklearn.linear_model import LinearRegression
    model_LinearRegression = LinearRegression()
    iris=load_boston()
    X=iris.data
    y=iris.target
    from sklearn.cross_validation import cross_val_score
    scores=cross_val_score(model_LinearRegression,X,y,cv=5,scoring='neg_mean_squared_error')
    print(scores)

if __name__ == '__main__':
    test_sklearn()
