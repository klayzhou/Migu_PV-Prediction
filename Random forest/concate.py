# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 将dat_1.0下的数据文件和feature下的特征文件进行拼接，对应存放到feature_1.0下
"""

from extra_feature import process_time, calculate_releasetime_interval, calculate_createtime_interval
import os
import json
import math
import numpy

"""
将特征和数据进行拼接，feature_1.0中的格式如下
Key:
    time_contentID
Value(13):
    displaytype #0
    formtype #1
    duration #2
    主题_one_hot #3
    program_type #4
    演员_one_hot #5
    时间vector #6
    时间数 #7
    星期数 #8
    创建时间间隔 #9
    上映时间间隔 #10
    历史pv #11
    PV值 #12
"""
def concate_to_feature_1():
    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        dataset = {}

        empty = {}
        with open(os.path.join(os.path.abspath('..'), 'feature', str(index) + '.txt'), 'r', encoding='UTF-8') as fread_feature, \
                open(os.path.join(os.path.abspath('..'), 'dat_2.0', str(index) + '.txt'), 'r', encoding='UTF-8') as fread_data, \
                open(os.path.join(os.path.abspath('..'), 'feature_1.0', str(index) + '.txt'), 'w', encoding='UTF-8') as fwrite:

            feature_dict = fread_feature.read()
            feature_dict = json.loads(feature_dict)
            
            for line in fread_data.readlines():
                line = line.replace('\r','').replace('\n','')
                tmp = line.split('|')
                if tmp[1] not in feature_dict:
                    continue

                #if not judge(tmp[2]):
                #    continue

                Item = feature_dict[tmp[1]]
                time_vector, time_num, weekday_num = process_time(tmp[0])
                releasetime_interval = calculate_releasetime_interval(tmp[0], Item[4])
                createtime_interval = calculate_createtime_interval(tmp[0], Item[0])
                key = tmp[0] + '_' + tmp[1]

                dataset[key] = []
                dataset[key].extend(Item[1:4])
                dataset[key].extend(Item[5:7])
                dataset[key].append(Item[7][0:300])
                dataset[key].extend([time_vector, time_num, weekday_num, createtime_interval, releasetime_interval, tmp[2], tmp[3]])


            fwrite.write(json.dumps(dataset, ensure_ascii=False))

            dataset.clear()

if __name__ == '__main__':
    concate_to_feature_1()
