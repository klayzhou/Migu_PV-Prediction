import jieba
import json
import os
import time
from datetime import datetime as dt
from es_search import es_search

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

def process_content_type(content_str):
    if content_str.isdigit():
        return []
    elif content_str.find('|') >= 0:
        return content_str.split('|')
    else:
        return [content_str]


'''
	  节目ID	 标题  创建时间	一级分类编号	一级分类名称	剧集类型	剧集时长	节目介绍	关键词	各大属性！															
旧版     0	  1	     2	       3	        4	        5	     6	  7	      8	       9													
新版 	id	标题的分词	createtime	displaytype	      formtype  duration detail	keywords  上映时间	主题	 正片/花絮	演员名	演员id
														
'''
def extra_feature():

    program_information_dir = os.path.join(os.path.abspath('..'), 'program_information_1.0')
    feature_dir = os.path.join(os.path.abspath('..'), 'feature')

    for index in range(1,22):
        print('file ' + str(index) + ' is processing')
        feature = []
        with open(os.path.join(program_information_dir,str(index)+'.txt'),'r',encoding='UTF-8')	as fread:
            res = fread.read()
            res = json.loads(res)

            for item in res:
                
                name_list = None
                release_time = ''
                topic = []
                formtype = ''
                peoples = []
                peoples_ID = []
                keywords = []

                name_list = list(jieba.cut(item[1],cut_all = False))
                time_flag = False
                if item[9] and isinstance(item[9],list):
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
                            temp = process_content_type(iter['propertyValue'])
                            if not temp:
                                pass
                            elif len(temp) == 1:
                                topic.append(temp[0])
                            else:
                                for j in temp:
                                    topic.append(j)

                if time_flag==False:
                    release_time = dt.strftime(dt.strptime(item[2],'%Y-%m-%d %H:%M:%S'),'%Y-%m')

                keywords = item[8].split(',')

                feature.append([item[0],name_list,item[2],item[3],item[5],item[6],item[7],keywords,release_time,topic,formtype,peoples,peoples_ID])

            res_file = json.dumps(feature, ensure_ascii=False)
            with open(os.path.join(feature_dir, str(index)+'.txt'),'w',encoding='UTF-8') as fwrite:
                fwrite.write(res_file)
                fwrite.flush()





if __name__ == '__main__':
    extra_feature()
    #get_all_information()