# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 将dat_1.0下的数据文件和feature下的特征文件进行拼接，对应存放到feature_1.0下
"""

from extra_feature import process_time, calculate_releasetime_interval, calculate_createtime_interval
import os
import json
import math
from sklearn.externals import joblib
import numpy as np

def judge(PV):
    if int(PV) < 10:
        return False
    return True

"""
将特征和数据进行拼接，feature_1.0中的格式如下
Key:
    time_contentID
Value(15):
    标题 #0
    createtime #1
    displaytype_one_hot #2
    formtype_one_hot
    duration
    detail
    keywords
    releasetime
    主题_one_hot
    program_type_one_hot
    演员_one_hot
    星期vector
    创建时间间隔
    上映时间间隔
    PV值
"""
def concate_to_feature_1():
    total_num = 0
    vv = []
    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        dataset = {}
        empty = {}
        with open(os.path.join(os.path.abspath('..'), 'feature', str(index) + '.txt'), 'r', encoding='UTF-8') as fread_feature, \
                open(os.path.join(os.path.abspath('..'), 'dat_1.0', str(index) + '.txt'), 'r', encoding='UTF-8') as fread_data, \
                open(os.path.join(os.path.abspath('..'), 'feature_1.0', str(index) + '.txt'), 'w', encoding='UTF-8') as fwrite_complete, \
                open(os.path.join(os.path.abspath('..'), 'knn_feature', str(index) + '.txt'), 'w', encoding='UTF-8') as fwrite_incomplete:

            feature_dict = fread_feature.read()
            feature_dict = json.loads(feature_dict)

            previous_click = dict()

            for line in fread_data.readlines():
                tmp = line.strip().split('|')
                if tmp[1] not in feature_dict:
                    continue

                #if not judge(tmp[2]):
                #    continue

                Item = feature_dict[tmp[1]]
                if Item[2][1] != 1:
                    continue
                vv.append(tmp[2])

                if '娘道'in Item[0]:
                    print('VV:'+str(tmp[2])+'...')
                    print(Item[2])

                weekday_vector, time_vector = process_time(tmp[0])
                releasetime_interval = calculate_releasetime_interval(tmp[0], Item[7])
                createtime_interval = calculate_createtime_interval(tmp[0], Item[1])
                key = tmp[0] + '_' + tmp[1]
                if tmp[1] not in previous_click:
                    empty[key] = []
                    empty[key].extend(Item)
                    empty[key].extend([weekday_vector, time_vector, createtime_interval, releasetime_interval, tmp[2]])
                else:
                    dataset[key] = []
                    dataset[key].extend(Item)
                    dataset[key].extend([weekday_vector, time_vector, createtime_interval, releasetime_interval, previous_click[tmp[1]], tmp[2]])

                previous_click[tmp[1]] = tmp[2]
            total_num = total_num + len(dataset)
            fwrite_complete.write(json.dumps(dataset, ensure_ascii=False))
            dataset.clear()
            total_num = total_num + len(empty)
            fwrite_incomplete.write(json.dumps(empty, ensure_ascii=False))
            empty.clear()

    vv = np.array(vv, dtype='int')
    print('total nums:'+str(total_num))
    print(np.max(vv))
    print(np.sum(np.where(vv>5,1,0)))
    print(np.sum(np.where(vv>10,1,0)))
    print(np.sum(np.where(vv>15,1,0)))

if __name__ == '__main__':
    concate_to_feature_1()
