import json
from datetime import datetime as dt
import os
import time
from es_search import es_search

"""
记录函数运行的时间
"""
def log_time(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args,**kw)
        end = time.time()
        print(str(func.__name__) + ' running time:' + str(end-start) + 's')
        return
    return wrapper

"""
处理dat文件，生成csv文件，每一行都是"时间|comp id|节目ID|节目PV"的格式
"""
def process_dat():
    count = 0
    rootdir = r'D:\AllProject\PV\dat'
    with open(os.path.join(rootdir,'result.csv'),'w', encoding='UTF-8') as fwrite:
        for file in os.listdir(rootdir):
            if file.endswith('.csv'):
                continue
            
            with open(os.path.join(rootdir,file), 'r', encoding='UTF-8') as fread:
                for line in fread.readlines():
                    #print(str(line))
                    temp = line.split('|')
                    if temp[1] == '' or temp[1] == 'LIST' or temp[5]=='-998' or temp[5] == '':
                        continue
                    fwrite.write(temp[0] + '|' + temp[1] + '|' + temp[5][0:9] + '|' + temp[6] + '\r')
                    fwrite.flush()
            count = count + 1
            print('file' + str(count) + ' : ' + str(file) + ' has done')

"""
读取csv文件，生成节目ID的集合
"""
def get_IDs():
    filePath = r'D:\AllProject\PV\dat\result.csv'
    count = 0
    Idset = set()
    with open(filePath, 'r', encoding='UTF-8') as fread:
        for line in fread.readlines():
            count = count + 1			
            temp = line.split('|')
            Idset.add(temp[2])
            #if len(Idset) >= 25000:
            #    break
    print(str(count) + ' ' + str(len(Idset)))
    return Idset

"""
将节目ID的集合以单位为10000划分到21个txt文件中去
"""
def write_IDs():
    IDs = get_IDs()
    count = 0
    ids_temp = []
    for id in IDs:
        count = count + 1
        ids_temp.append(id)
        if count%10000==0:
            with open(os.path.join(r'D:\AllProject\PV\IDs',str(int(count/10000))+'.txt'), 'w', encoding='UTF-8') as fwrite:
                for ID in ids_temp:
                    fwrite.write(str(ID) + '\r')
            ids_temp.clear()
    with open(os.path.join(r'D:\AllProject\PV\IDs',str(int(1 + count/10000))+'.txt'), 'w', encoding='UTF-8') as fwrite:
        for ID in ids_temp:
            fwrite.write(str(ID) + '\r')

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
    with open(os.path.join(r'D:\AllProject\PV\IDs',str(num)+'.txt'), 'r', encoding='UTF-8') as fread:
        count = 0
        ID_list = []
        res = []
        for line in fread.readlines():
            count = count + 1
            ID_list.append(line.strip())
            if count%100==0:
                print(count)
                temp = es_search(ID_list)
                ID_list.clear()
                res = res + temp

        res_file = json.dumps(res)
        with open(os.path.join('D:\AllProject\PV\information',str(num)+'.txt'),'w',encoding='UTF-8') as fwrite:
            fwrite.write(res_file)
            fwrite.flush()

"""
读取所有的节目ID，通过ES提取节目信息，存储到本地
目前该函数未被启用，采用的是上述read_ID函数来进行信息的抓取
"""
def get_information():
    IDset = get_IDs()
    count = 0
    file_index = 0
    ID_list = []
    res = []
    for ID in IDset:
        count = count + 1
        ID_list.append(ID)
        if count%100 == 0 or count==len(IDset):
            print(str(count) + ' has done')
            temp = es_search(ID_list)
            ID_list.clear()
            res = res + temp
            if len(res) >= 10000 or count==len(IDset):
                file_index = file_index + 1
                res_file = json.dumps(res)
                print('start writing file:' + str(file_index))
                with open(os.path.join('D:\AllProject\PV\information',str(file_index)+'.txt'),'w') as fwrite:
                    fwrite.write(res_file)
                    fwrite.flush()
                res.clear()

"""
得到所有节目的详细信息list
"""
def get_all_information():
    res = []
    for index in range(1,22):
        with open(os.path.join(r'D:/VVPrediction/output',str(index)+'.txt'),'r',encoding='UTF-8')	as fread:
            out = fread.read()
            out = json.loads(out)
            res = res + out
    return res

"""
统计一些信息，测试调研用
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
            if not i[9] or isinstance(i[9],dict):
                continue
            for j in i[9]:
                if j['propertyKey'] == '主演':
                    count_1000_yes = count_1000_yes + 1
                    break
        elif i[3] == '1001':
            count_1001 = count_1001 +1
            if int(i[5]) == 6:
                count_1001_6 = count_1001_6 +1
                if not i[9] or isinstance(i[9],dict):
                    continue
                flag = False
                for j in i[9]:
                    if j['propertyKey'] == '主演':
                        flag =True
                        count_1001_6_yes = count_1001_6_yes + 1
                        break
                #if flag == False:
                #    print(i[0])
            elif int(i[5]) == 7:
                count_1001_7 = count_1001_7 + 1
                if not i[9] or isinstance(i[9],dict):
                    continue
                flag = False
                for j in i[9]:
                    if j['propertyKey'] == '主演':
                        flag = True
                        count_1001_7_yes = count_1001_7_yes + 1
                        break
                if flag == False:
                    print(i[0])
    print(str(count_1000) + ' ' + str(count_1000_yes) + ' ' + str(count_1001) + ' ' + str(count_1001_6) + ' ' + str(count_1001_6_yes) + ' ' + str(count_1001_7) + ' ' + str(count_1001_7_yes))

"""
过滤垃圾数据，仍存到21个文件里边
"""
def get_clean_data():
    count = 0
    for index in range(1,22):
        with open(os.path.join(r'D:\AllProject\PV\information',str(index)+'.txt'),'r',encoding='UTF-8')	as fread:
            res = fread.read()
            res = json.loads(res)
            for i in range(len(res)-1,-1,-1):
                if int(res[i][6]) == 0 or int(res[i][3]) == 0 or (not res[i][8]) or isinstance(res[i][9],dict) or res[i][7] == '':
                    res.remove(res[i])
                elif isinstance(res[i][8],list):
                    temp = ''
                    for j in range(len(res[i][8])):
                        if j != len(res[i][8])-1:
                            temp = temp + str(res[i][8][j]) + ','
                        else:
                            temp = temp + str(res[i][8][j])
                    res[i][8] = temp
            count += len(res)
            with open(os.path.join(r'D:\AllProject\PV\information_1.0',str(index)+'.txt'),'w',encoding='UTF-8') as fwrite:
                res = json.dumps(res)
                fwrite.write(res)
                fwrite.flush()
        print('file ' + str(index) + ' has done')
    print(str(count))

def process_date(date_str):
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
'''
	  节目ID	 标题  创建时间	一级分类编号	一级分类名称	剧集类型	剧集时长	节目介绍	关键词	各大属性！															
旧版     0	  1	     2	       3	        4	        5	     6	  7	      8	       9													
新版 	id	title	createtime	displaytype	      formtype  duration detail	keywords  上映时间	主题	 正片/花絮	演员名	演员id
														
'''

def extra_feature():
    res = get_all_information()


    feature = []

    for item in res:

        release_time = ''
        topic = []
        formtype = ''
        peoples = []
        peoples_ID = []

        time_flag = False

        if item[9] and isinstance(item[9],dict):
            for iter in item[9]:
                if iter['propertyKey'] in ['主演','演员','男主角','嘉宾','主持人','导演','编剧','人物','演出人员','报道人物','歌手姓名','解说员','明星','原著作者']:
                    if 'propertyValue' in iter.keys():
                        peoples.append(iter['propertyValue'])
                    if 'propertyItem' in iter.keys():
                        peoples_ID.append(iter['propertyItem'])

                elif time_flag== False and iter['propertyKey'] in ['国内首映时间','首播时间','上映时间','播出时间','待映日期','发行年份','事件发生时间','播出年代']:
                    time = process_date(iter['propertyValue'])
                    if time:
                        release_time = time
                        time_flag = True

                elif iter['propertyKey'] in ['内容形态','节目形态']:
                    formtype = iter['propertyValue']

                elif iter['propertyKey'] in ['内容类型','内容分类','主题','描述年代']:
                    topic.append(iter['propertyValue'])

        if time_flag==False:
            release_time = dt.strftime(dt.strptime(item[2],'%Y-%m-%d %H:%M:%S'),'%Y-%m')





if __name__ == '__main__':
    extra_feature()
    