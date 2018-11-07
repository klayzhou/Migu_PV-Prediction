import os
import json

#the train folder and test folder
'''
数组元素列表及其含义

'''
def normalize():
    train_path = '../GBDT/train/'
    files = os.listdir(train_path)
    train = []
    for item in files:
        file = os.path.join(train_path, item)
        print(file)
        with open(file, 'r') as fread:
            res = fread.read()
            res = json.loads(res)
            for item in res:
                


if __name__ == '__main__':
    normalize()