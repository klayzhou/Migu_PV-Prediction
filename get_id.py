# -*- encoding: utf-8 -*-
"""
本文件主要有以下几个作用：
1 遍历dat文件生成result.csv文件
2 处理result.csv文件生成result_merge.csv文件
3 根据result_merge.csv文件生成IDs下边的21个txt文件
4 根据IDs下的21个文件，将result_merge.csv文件进行切分，对应存放到dat_1.0下
5 遍历IDs下的21个文件，进行es查询，对应存放到program_information下
6 遍历program_information下的21个文件，过滤掉垃圾ID及其节目信息后，对应存放到program_information_1.0下
"""

import json
import os
import time
from es_search import es_search


"""
记录函数运行的时间
"""
def log_time(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        end = time.time()
        print(str(func.__name__) + ' running time:' + str(end - start) + 's')
        return

    return wrapper


"""
处理dat文件，生成csv文件，每一行都是"时间|comp id|节目ID|节目PV"的格式
"""
def process_dat():
    count = 0
    rootdir = os.path.join(os.path.abspath('..'), 'dat')
    with open(os.path.join(rootdir, 'result.csv'), 'w', encoding='UTF-8') as fwrite:
        for file in os.listdir(rootdir):
            if file.endswith('.csv'):
                continue

            with open(os.path.join(rootdir, file), 'r', encoding='UTF-8') as fread:
                for line in fread.readlines():
                    temp = line.split('|')
                    if temp[1] == '' or temp[1] == 'LIST' or temp[5] == '-998' or temp[5] == '' or (not temp[5].isdigit()):
                        continue
                    fwrite.write(temp[0] + '|' + temp[1] + '|' + temp[5][0:9] + '|' + temp[6] + '\r')
                    fwrite.flush()
            count = count + 1
            print('file' + str(count) + ' : ' + str(file) + ' has done')


"""
处理result.csv文件，将comp id不同，但是时间和节目id相同的数据合并
生成的result_merge.csv文件，每一行都是"时间|节目ID|节目PV"的格式
"""
def process_csv():
    rootdir = os.path.join(os.path.abspath('..'), 'dat')
    dict = {}
    with open(os.path.join(rootdir, 'result.csv'), 'r', encoding='UTF-8') as fread:
        for line in fread.readlines():
            temp = line.split('|')
            key = temp[0] + '_' + temp[2]
            if key in dict.keys():
                dict[key] = dict[key] + int(temp[3])
            else:
                dict[key] = int(temp[3])

    with open(os.path.join(rootdir, 'result_merge.csv'), 'w', encoding='UTF-8') as fwrite:
        for item in dict:
            temp = item.split('_')
            fwrite.write(temp[0] + '|' + temp[1] + '|' + str(dict[item]) + '\r')


"""
读取csv文件，生成节目ID的集合
"""
def get_IDs():
    filePath = os.path.join(os.path.abspath('..'), 'dat', 'result_merge.csv')
    count = 0
    Idset = set()
    with open(filePath, 'r', encoding='UTF-8') as fread:
        for line in fread.readlines():
            count = count + 1
            temp = line.split('|')
            Idset.add(temp[1])
            # if len(Idset) >= 25000:
            #    break
    print(str(count) + ' ' + str(len(Idset)))
    return Idset


"""
将节目ID的集合以单位为10000划分到21个txt文件中去
2.txt文件中有一个‘yes_id’什么的，我给手动删除了，所以2.txt只有9999个ID
"""
def write_IDs():
    IDs_dir = os.path.join(os.path.abspath('..'), 'IDs')
    IDs = get_IDs()
    count = 0
    ids_temp = []
    for id in IDs:
        count = count + 1
        ids_temp.append(id)
        if count % 10000 == 0:
            with open(os.path.join(IDs_dir, str(int(count / 10000)) + '.txt'), 'w', encoding='UTF-8') as fwrite:
                for ID in ids_temp:
                    fwrite.write(str(ID) + '\r')
            ids_temp.clear()
    with open(os.path.join(IDs_dir, str(int(1 + count / 10000)) + '.txt'), 'w', encoding='UTF-8') as fwrite:
        for ID in ids_temp:
            fwrite.write(str(ID) + '\r')


"""
根据IDs下边的21个文件，将result_merge.csv文件分成21份
"""
def split_result_merge_csv():
    dict = {}
    with open(os.path.join(os.path.abspath('..'), 'dat', 'result_merge.csv'), 'r', encoding='UTF-8') as fread:
        for line in fread.readlines():
            temp = line.split('|')
            if temp[1] not in dict.keys():
                dict[temp[1]] = []
            dict[temp[1]].append(temp[0] + '_' + str(temp[2]))
    
    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        with open(os.path.join(os.path.abspath('..'), 'IDs', str(index)+'.txt'), 'r', encoding='UTF-8') as fread, open(os.path.join(os.path.abspath('..'), 'dat_1.0', str(index)+'.txt'), 'w', encoding='UTF-8') as fwrite:
            for line in fread.readlines():
                line = line.strip()
                for item in dict[line]:
                    temp = item.split('_')
                    fwrite.write(temp[0] + '|' + line + '|' + temp[1])


"""
读取节目ID的txt文件，通过ES提取节目信息，存储到本地
但是该函数只是针对某一个txt文件，要处理所有txt文件的话要进行一次遍历
该函数借助json对list进行存取，读取存储节目信息的txt文件的代码如下
b = open(r"D:\AllProject\PV\information\1.txt", "r",encoding='UTF-8')
out = b.read()
out =  json.loads(out)
"""
def read_IDs(num):
    print('file ' + str(num) + ' is processing')
    IDs_dir = os.path.join(os.path.abspath('..'), 'IDs')
    program_information_dir = os.path.join(os.path.abspath('..'), 'program_information')
    with open(os.path.join(IDs_dir, str(num) + '.txt'), 'r', encoding='UTF-8') as fread:
        count = 0
        ID_list = []
        res = []
        for line in fread.readlines():
            count = count + 1
            ID_list.append(line.strip())
            if count % 100 == 0:
                print(count)
                temp = es_search(ID_list)
                ID_list.clear()
                res = res + temp

        res_file = json.dumps(res)
        with open(os.path.join(program_information_dir, str(num) + '.txt'), 'w', encoding='UTF-8') as fwrite:
            fwrite.write(res_file)
            fwrite.flush()


"""
读取所有节目的信息
"""
def read_IDs_all():
    for i in range(1,22):
        read_IDs(i)


"""
得到所有节目的详细信息，测试调研用
"""
def get_all_information():
    res = {}
    program_information_dir = os.path.join(os.path.abspath('..'), 'feature')
    for index in range(1,11):
        print('file ' + str(index) + ' is being reading')
        with open(os.path.join(program_information_dir, str(index) + '.txt'), 'r', encoding='UTF-8') as fread:
            out = fread.read()
            out = json.loads(out)
            res.update(out)
    return res


"""
统计数据信息，测试调研用
"""
def statics():
    res = get_all_information()
    print('done')
    count_1000 = 0
    count_1001 = 0
    count_1000_yes = 0
    count_1001_6 = 0
    count_1001_7 = 0
    count_1001_6_yes = 0
    count_1001_7_yes = 0
    for i in res:
        if i[3] == '1000':
            count_1000 = count_1000 + 1
            if not i[9] or isinstance(i[9], dict):
                continue
            for j in i[9]:
                if j['propertyKey'] == '主演':
                    count_1000_yes = count_1000_yes + 1
                    break
        elif i[3] == '1001':
            count_1001 = count_1001 + 1
            if int(i[5]) == 6:
                count_1001_6 = count_1001_6 + 1
                if not i[9] or isinstance(i[9], dict):
                    continue
                flag = False
                for j in i[9]:
                    if j['propertyKey'] == '主演':
                        flag = True
                        count_1001_6_yes = count_1001_6_yes + 1
                        break
                # if flag == False:
                #    print(i[0])
            elif int(i[5]) == 7:
                count_1001_7 = count_1001_7 + 1
                if not i[9] or isinstance(i[9], dict):
                    continue
                flag = False
                for j in i[9]:
                    if j['propertyKey'] == '主演':
                        flag = True
                        count_1001_7_yes = count_1001_7_yes + 1
                        break
                if flag == False:
                    print(i[0])
    print(str(count_1000) + ' ' + str(count_1000_yes) + ' ' + str(count_1001) + ' ' + str(count_1001_6) + ' ' + str(
        count_1001_6_yes) + ' ' + str(count_1001_7) + ' ' + str(count_1001_7_yes))


"""
过滤垃圾数据，仍存到21个文件里边
"""
def get_clean_data():
    count = 0
    program_information_dir = os.path.join(os.path.abspath('..'), 'program_information')
    program_information_1_dir = os.path.join(os.path.abspath('..'), 'program_information_1.0')
    for index in range(1, 22):
        with open(os.path.join(program_information_dir, str(index) + '.txt'), 'r', encoding='UTF-8')    as fread:
            res = fread.read()
            res = json.loads(res)
            for i in range(len(res) - 1, -1, -1):
                if int(res[i][6]) == 0 or int(res[i][3]) == 0 or (not res[i][8]) or isinstance(res[i][9], dict) or \
                        res[i][7] == '':
                    res.remove(res[i])
                elif isinstance(res[i][8], list):
                    temp = ''
                    for j in range(len(res[i][8])):
                        if j != len(res[i][8]) - 1:
                            temp = temp + str(res[i][8][j]) + ','
                        else:
                            temp = temp + str(res[i][8][j])
                    res[i][8] = temp
            count += len(res)
            with open(os.path.join(program_information_1_dir, str(index) + '.txt'), 'w', encoding='UTF-8') as fwrite:
                res = json.dumps(res)
                fwrite.write(res)
                fwrite.flush()
        print('file ' + str(index) + ' has done')
    print(str(count))




if __name__ == '__main__':
    #process_dat()
    #process_csv()
    #write_IDs
    #split_result_merge_csv()
    #read_IDs_all()
    #get_clean_data()