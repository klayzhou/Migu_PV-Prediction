# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 将dat_1.0下的数据文件和feature下的特征文件进行拼接，对应存放到feature_1.0下
"""

from extra_feature import process_time, calculate_releasetime_interval, calculate_createtime_interval
import os
import json
import math


"""
将特征和数据进行拼接，feature_1.0中的格式如下
Key:
    time_contentID
Value(17):
    标题
    createtime
    displaytype_one_hot
    formtype_one_hot
    duration
    detail
    keywords
    releasetime
    主题_one_hot
    program_type_one_hot
    演员_one_hot
    星期vector
    时间vector
    创建时间间隔
    上映时间间隔
    历史pv
    PV值
"""
def concate_to_feature_1():
    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        dataset = {}
        with open(os.path.join(os.path.abspath('..'), 'feature', str(index) + '.txt'), 'r', encoding='UTF-8') as fread_feature, open(os.path.join(os.path.abspath('..'), 'dat_1.0', str(index) + '.txt'), 'r', encoding='UTF-8') as fread_data, open(os.path.join(os.path.abspath('..'), 'feature_1.0', str(index) + '.txt'), 'w', encoding='UTF-8') as fwrite:
            
            feature_dict = fread_feature.read()
            feature_dict = json.loads(feature_dict)
            
            """
            previous_pv = {}

            for line in fread_data.readlines():
                tmp = line.strip().split('|')
                if tmp[1] not in feature_dict:
                    continue
                
                if tmp[1] not in previous_pv.keys():
                    previous_pv.clear()
                    previous_pv[tmp[1]] = []
                
                Item = feature_dict[tmp[1]]
                weekday_vector, time_vector = process_time(tmp[0])
                releasetime_interval = calculate_releasetime_interval(tmp[0], Item[7])
                createtime_interval = calculate_createtime_interval(tmp[0], Item[1])
                previous_pv_tmp = list(previous_pv[tmp[1]])
                key = tmp[0] + '_' + tmp[1]
                dataset[key] = []
                dataset[key].extend(Item)
                dataset[key].extend([weekday_vector, time_vector, createtime_interval,releasetime_interval, previous_pv_tmp, tmp[2]])
                
                previous_pv[tmp[1]].append(int(tmp[2]))

            
            fwrite.write(json.dumps(dataset, ensure_ascii=False))
            dataset.clear()
            """

            previous_pv = {}

            for line in fread_data.readlines():
                tmp = line.strip().split('|')
                if tmp[1] not in feature_dict:
                    continue
               
                if tmp[1] not in previous_pv.keys():
                    previous_pv.clear()
                    previous_pv[tmp[1]] = [0,-1]
                else:
                    interval = int(tmp[0])-previous_pv[tmp[1]][0]
                    if interval==1 or interval==77:
                        pass
                    else:
                        previous_pv[tmp[1]] = [0,-1]                    

                previous_pv_tmp = previous_pv[tmp[1]][1]
                Item = feature_dict[tmp[1]]
                weekday_vector, time_vector = process_time(tmp[0])
                releasetime_interval = calculate_releasetime_interval(tmp[0], Item[7])
                createtime_interval = calculate_createtime_interval(tmp[0], Item[1])
           
                key = tmp[0] + '_' + tmp[1] 
                dataset[key] = []
                dataset[key].extend(Item)
                dataset[key].extend([weekday_vector, time_vector, createtime_interval,releasetime_interval, previous_pv_tmp, tmp[2]])

                previous_pv[tmp[1]] = [int(tmp[0]),int(tmp[2])]


            fwrite.write(json.dumps(dataset, ensure_ascii=False))
            dataset.clear()

if __name__ == '__main__':
    concate_to_feature_1()
