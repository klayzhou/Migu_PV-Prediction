# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 遍历program_information_1.0下的21个文件，提取词向量等特征，对应存放到feature下
"""

#import jieba
import os
import json
from datetime import datetime as dt
import collections
from numpy import *


"""
处理content_type字符串
"""
def process_content_type(content_str):
    if content_str.isdigit():
        return []
    elif content_str.find('|') >= 0:
        return content_str.split('|')
    else:
        return [content_str]


"""
处理date字符串
"""
def process_date(date_str):
    if len(date_str)<=2:
        return ''
    temp = []
    if date_str[0] == '-':
        #print('1')
        pass
    elif date_str.find('年') >= 0:
        #print('5')
        temp = date_str.split('年')
        temp[1] = temp[1].split('月')[0]
    elif date_str.find(r'/') >= 0:
        #print('2')
        temp = date_str.split(r'/')
    elif date_str.find('-') >= 0:
        #print('3')
        temp = date_str.split('-')
    elif date_str.find('.') >= 0:
        date_str.split('.')
        #print('4')
        temp = date_str.split('.')
    elif int(date_str) > 9999:
        #print('6')
        pass
    else:
        #print('7')
        temp.append(date_str)

    if not temp:
        return ''
    elif len(temp) == 1 or (not temp[1]):
            return temp[0]+'-01'
    else:
        if temp[1].isdigit():
            return temp[0]+'-'+temp[1]
        else:
            return '19'+temp[0]+'-01'


"""
处理形如“2018100901”的时间字符串，返回时间和星期的one-hot向量
"""
def process_time(time_str):
    year = int(time_str[0:4])
    month = int(time_str[4:6])
    day = int(time_str[6:8])
    time_id = int(time_str[8:])
    weekday_id = dt(year,month,day).weekday()
    time_vector = zeros(24)
    time_vector[time_id] = 1
    return time_vector.tolist(), time_id, weekday_id
    


"""
计算从上映时间到当前时间为止，共多少个月间隔
"""
def calculate_releasetime_interval(time_str, releasetime_str):
    year = int(time_str[0:4])
    month = int(time_str[4:6])
    day = int(time_str[6:8])

    temp = releasetime_str.split('-')
    releasetime_year = int(temp[0])
    releasetime_month = int(temp[1])

    return ((dt(year,month,day)-dt(releasetime_year,releasetime_month,1)).days//30)


"""
计算从创建时间到当前时间为止，共多少天间隔
"""
def calculate_createtime_interval(time_str, createtime_str):
    year = int(time_str[0:4])
    month = int(time_str[4:6])
    day = int(time_str[6:8])

    temp = createtime_str.split('-')
    createtime_year = int(temp[0])
    createtime_month = int(temp[1])
    createtime_day = int(temp[2].split(' ')[0])

    return (dt(year,month,day)-dt(createtime_year,createtime_month,createtime_day)).days


'''
最后版本的feature 
Key : contentID
Value: 标题，createtime, displaytype_one_hot, formtype_one_hot, duration, detail, keywords, releasetime, 主题_one_hot, program_type_one_hot, 演员_one_hot
'''
def extra_feature():
    program_information_dir = os.path.join(os.path.abspath('..'), 'program_information_1.0')
    feature_dir = os.path.join(os.path.abspath('..'), 'feature')
    actor_lst = []
    feature = []
    file_count = []
    file_count_num = -1

    program_type_set = set()
    topic_set = set()
    form_type_set = set()


    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        with open(os.path.join(program_information_dir,str(index)+'.txt'),'r',encoding='UTF-8')	as fread:
            res = fread.read()
            res = json.loads(res)
            file_count_num = file_count_num + len(res)
            file_count.append(file_count_num)

            for item in res:
                name_list = None
                release_time = ''
                topic = []
                formtype = ''
                peoples = set() # delete the repeated words
                peoples_ID = set() # delete the repeated words
                time_flag = False

                if item[9] and isinstance(item[9],list):
                    for iter in item[9]:
                        if iter['propertyKey'] in ['主演','演员','男主角','嘉宾','主持人','导演','编剧','人物','演出人员','报道人物','歌手姓名','解说员','明星','原著作者']:
                            if 'propertyValue' in iter.keys() and iter['propertyValue']!='其他' and iter['propertyValue']!='无':
                                peoples.add(iter['propertyValue'])
                                if 'propertyItem' in iter.keys() and iter['propertyItem'].isdigit():
                                    peoples_ID.add(iter['propertyItem'])

                        elif time_flag== False and iter['propertyKey'] in ['国内首映时间','首播时间','上映时间','播出时间','待映日期','发行年份','事件发生时间','播出年代']:
                            time = process_date(iter['propertyValue'])
                            if time:
                                release_time = time
                                time_flag = True

                        elif iter['propertyKey'] in ['内容形态','节目形态']:
                            formtype = iter['propertyValue']
                            if formtype:
                                program_type_set.add(formtype)

                        elif iter['propertyKey'] in ['内容类型','内容分类','主题','描述年代']:
                            temp = process_content_type(iter['propertyValue'])
                            if not temp:
                                pass
                            elif len(temp) == 1:
                                topic.append(temp[0])
                                topic_set.add(temp[0])
                            else:
                                for j in temp:
                                    topic.append(j)
                                    topic_set.add(j)

                if time_flag==False:
                    release_time = dt.strftime(dt.strptime(item[2],'%Y-%m-%d %H:%M:%S'),'%Y-%m')

                keywords = item[8].split(',')
                #print(peoples_ID)

                actor_lst.extend(list(peoples))

                feature.append([item[0],item[1],item[2],item[3],item[5],item[6],item[7],keywords,release_time,topic,formtype,peoples,peoples_ID])

                # form_type one-hot encoder
                form_type_set.add(item[5])

    # find the top 2000 actors
    counter = collections.Counter(actor_lst)
    sorted_actor = sorted(counter.items(), key= lambda x:x[1], reverse=True)
    invalid_actor = dict(sorted_actor[:2000])

    # one-hot encoding for actor id
    num = 0
    for item in invalid_actor:
        invalid_actor[item] = num
        num = num + 1

    num = 0

    display_dict = {'1000':0,'1001':1,'1002':2,'1003':3,'1004':4,'1005':5,'1006':6,'1007':7,'1008':8,'1009':9,'1010':10,'1011':11}
    form_type_dict = {}
    form_type_len = len(form_type_set)
    for i in form_type_set:
        form_type_dict[i] = num
        num = num + 1

    programtype_dict = {}
    programtype_len = len(program_type_set)
    num=0
    for i in program_type_set:
        programtype_dict[i] = num
        num = num + 1

    topic_dict = {}
    topic_len = len(topic_set)
    num = 0
    for i in topic_set:
        topic_dict[i] = num
        num = num + 1

    count = 0
    tmp_feature = {}
    file_index = 0
    for index in range(len(feature)):
        # delete the useless actor name and actor id
        
        count = count + 1
        display_vector = zeros(12)
        form_type_vector = zeros(form_type_len)
        one_hot_actor = zeros(2000)
        programtype_vector = zeros(programtype_len)
        topic_vector = zeros(topic_len)

        if feature[index][3]:
            if feature[index][3] in display_dict:
                display_vector[display_dict[feature[index][3]]] =1

        if feature[index][4]:
            form_type_vector[form_type_dict[feature[index][4]]] = 1

        for iter in feature[index][11]:
            if iter in invalid_actor:
                one_hot_actor[invalid_actor[iter]] = 1

        if feature[index][10]:
            programtype_vector[programtype_dict[feature[index][10]]] = 1

        for iter in feature[index][9]:
            topic_vector[topic_dict[iter]] = 1

        tmp_lst = feature[index][1:3]
        tmp_lst.append(display_vector.tolist())
        tmp_lst.append(form_type_vector.tolist())
        tmp_lst.extend(feature[index][5:9])
        tmp_lst.append(topic_vector.tolist())
        tmp_lst.append(programtype_vector.tolist())
        tmp_lst.append(one_hot_actor.tolist())
        tmp_feature[feature[index][0]] = tmp_lst

        if index == file_count[file_index]:
            print('file ' + str(file_index + 1) + ' is processing')
            with open(os.path.join(feature_dir, str(file_index + 1) + '.txt'), 'w', encoding='UTF-8') as fwrite:
                fwrite.write(json.dumps(tmp_feature, ensure_ascii=False))
                tmp_feature.clear()
            file_index = file_index + 1


'''
最后版本的feature 
Key : contentID
Value: createtime, displaytype, formtype, duration, releasetime, 主题_one_hot, program_type, 演员_one_hot
'''
def extra_feature_optimization():
    program_information_dir = os.path.join(os.path.abspath('..'), 'program_information_1.0')
    feature_dir = os.path.join(os.path.abspath('..'), 'feature')
    feature = []

    file_count = []
    file_count_num = -1

    program_type_set = set()
    topic_set = set()
    form_type_set = set()
    actor_lst = []

    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        with open(os.path.join(program_information_dir,str(index)+'.txt'),'r',encoding='UTF-8')	as fread:
            res = fread.read()
            res = json.loads(res)
            file_count_num = file_count_num + len(res)
            file_count.append(file_count_num)

            for item in res:
                release_time = ''
                topic = []
                programtype = ''
                peoples = set() # delete the repeated words
                peoples_ID = set() # delete the repeated words
                keywords = []

                # name_list = None
                #name_list = list(jieba.cut(item[1],cut_all = False))
                #print(name_list)
                time_flag = False

                if item[9] and isinstance(item[9],list):
                    for iter in item[9]:
                        if iter['propertyKey'] in ['主演','演员','男主角','嘉宾','主持人','导演','编剧','人物','演出人员','报道人物','歌手姓名','解说员','明星','原著作者']:
                            if 'propertyValue' in iter.keys() and iter['propertyValue']!='其他' and iter['propertyValue']!='无':
                                peoples.add(iter['propertyValue'])
                                if 'propertyItem' in iter.keys() and iter['propertyItem'].isdigit():
                                    peoples_ID.add(iter['propertyItem'])

                        elif time_flag== False and iter['propertyKey'] in ['国内首映时间','首播时间','上映时间','播出时间','待映日期','发行年份','事件发生时间','播出年代']:
                            time = process_date(iter['propertyValue'])
                            if time:
                                release_time = time
                                time_flag = True

                        elif iter['propertyKey'] in ['内容形态','节目形态']:
                            programtype = iter['propertyValue']
                            if programtype:
                                program_type_set.add(programtype)

                        elif iter['propertyKey'] in ['内容类型','内容分类','主题','描述年代']:
                            temp = process_content_type(iter['propertyValue'])
                            if not temp:
                                pass
                            else:
                                for j in temp:
                                    topic.append(j)
                                    topic_set.add(j)

                if time_flag==False:
                    release_time = dt.strftime(dt.strptime(item[2],'%Y-%m-%d %H:%M:%S'),'%Y-%m')

                keywords = item[8].split(',')
                #print(peoples_ID)

                actor_lst.extend(list(peoples))
                # form_type one-hot encoder
                form_type_set.add(item[5])

                feature.append([item[0],item[1],item[2],item[3],item[5],item[6],item[7],keywords,release_time,topic,programtype,peoples,peoples_ID])

# ID, name, createtime, displaytime, formtype, cduration, detail, keywords, release_time, topic, programtype, peoples, peoplesID

    # find the top 2000 actors
    counter = collections.Counter(actor_lst)
    sorted_actor = sorted(counter.items(), key= lambda x:x[1], reverse=True)
    invalid_actor = dict(sorted_actor[:2000])

    # one-hot encoding for actor id
    num = 0
    for item in invalid_actor:
        invalid_actor[item] = num
        num = num + 1

    display_dict = {'1000':0,'1001':1,'1002':2,'1003':3,'1004':4,'1005':5,'1006':6,'1007':7,'1008':8,'1009':9,'1010':10,'1011':11}

    num = 0
    form_type_dict = {}
    for i in form_type_set:
        form_type_dict[i] = num
        num = num + 1

    programtype_dict = {}
    num=0
    for i in program_type_set:
        programtype_dict[i] = num
        num = num + 1

    topic_dict = {}
    topic_len = len(topic_set)
    num = 0
    for i in topic_set:
        topic_dict[i] = num
        num = num + 1

    count = 0
    tmp_feature = {}
    file_index = 0
    for index in range(len(feature)):
        # delete the useless actor name and actor id
        
        count = count + 1
        one_hot_actor = zeros(2000)
        topic_vector = zeros(topic_len)

        display_num = len(display_dict)
        if feature[index][3] and feature[index][3] in display_dict:
            display_num = display_dict[feature[index][3]]

        form_type_num = len(form_type_dict)
        if feature[index][4]:
            form_type_num = form_type_dict[feature[index][4]]

        programtype_num = len(programtype_dict)
        if feature[index][10]:
            programtype_num = programtype_dict[feature[index][10]]


        for iter in feature[index][11]:
            if iter in invalid_actor:
                one_hot_actor[invalid_actor[iter]] = 1


        for iter in feature[index][9]:
            topic_vector[topic_dict[iter]] = 1

        #最终特征
        tmp_lst = []
        tmp_lst.append(feature[index][2])#
        tmp_lst.append(display_num)
        tmp_lst.append(form_type_num)
        tmp_lst.append(feature[index][5])
        tmp_lst.append(feature[index][8])
        tmp_lst.append(topic_vector.tolist())
        tmp_lst.append(programtype_num)
        tmp_lst.append(one_hot_actor.tolist())
        tmp_feature[feature[index][0]] = tmp_lst

        if index == file_count[file_index]:
            print('file ' + str(file_index + 1) + ' is processing')
            with open(os.path.join(feature_dir, str(file_index + 1) + '.txt'), 'w', encoding='UTF-8') as fwrite:
                fwrite.write(json.dumps(tmp_feature, ensure_ascii=False))
                tmp_feature.clear()
            file_index = file_index + 1

if __name__ == '__main__':
    extra_feature_optimization()
