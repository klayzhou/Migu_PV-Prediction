# -*- encoding: utf-8 -*-
# call the es_search function for the property
# 返回顺序：节目ID, 标题，创建时间，一级分类编号，一级分类名称，剧集类型，剧集时长，节目介绍，关键词，各大属性！
# 剧集类型只有6-9这4种，其中，所有的7和8都有duration，所有9都没有duration，大部分6都有duration --> 过滤掉duration为0的，可以解决没有duration的问题
# 一级分类编号缺失的有3个，其中有两个是一级分类名称缺失，但是这两个的duration都为0，所以实际上只有一条数据有bug --> 过滤掉一级分类编号缺失的3条数据

from urllib import request
import json


def query(lst) :
    query_data = {
        "size":100,
        "query":{
            'constant_score':{
                 'filter':{
                     'terms':{
                         'contid': lst
                     }
                 }
            }
        }
    }
    #print(str(query_data))
    return query_data

def es_search_full(list):

    data = '{"index":["poms"]}\n' + json.dumps(query(list)) +'\n'

    headers = {
        'content-type': 'application/x-ndjson',
        "kbn-version": "6.1.1"
    }

    req = request.Request("http://183.192.162.101:8080/elasticsearch/_msearch", data=bytes(data, 'utf-8'), headers=headers, method='POST')

    f = open('result.txt','w')

    with request.urlopen(req) as response:
        if response.status==200:
            print('Status:',response.status,response.reason)
            data = json.loads(response.read())
            #print(data['responses'])
            #f.write(response.read().decode('utf-8'))
            f.write(str(data['responses']))
        else:
            raise Exception

def es_search(lst):

    data = '{"index":["poms"]}\n' + json.dumps(query(lst)) +'\n'

    headers = {
        'content-type': 'application/x-ndjson',
        "kbn-version": "6.1.1"
    }

    req = request.Request("http://183.192.162.101:8080/elasticsearch/_msearch", data=bytes(data, 'utf-8'), headers=headers, method='POST')

    result = []

    with request.urlopen(req) as response:
        if response.status == 200:
            # not sure the response of elasticsearch only one element [0]?
            data = json.loads(response.read())['responses'][0]['hits']['hits'] #the useful response, delete useless headers

            for item in data:
                source = item['_source']
                fields = source['fields']

                # fix the missed CDuration value
                if 'CDuration' not in fields.keys():
                    fields['CDuration']=0

                if 'propertyFileLists' not in fields.keys():
                    fields['propertyFileLists'] = {'propertyFile':{}}

                if 'Detail' not in fields.keys():
                    fields['Detail'] = ''
					
                if 'KEYWORDS' not in fields.keys():
                    fields['KEYWORDS'] = {'keyword':{}}
					
                if 'DISPLAYTYPE' not in fields.keys():
                    fields['DISPLAYTYPE'] = 0
					
                if 'DisplayName' not in fields.keys():
                    fields['DisplayName'] = ''

                
                # fix the keyword
                if isinstance(fields['KEYWORDS']['keyword'], dict):
                    if 'keywordName' not in fields['KEYWORDS']['keyword'].keys():
                        fields['KEYWORDS']['keyword']['keywordName'] = ''
                    result.append([source['contid'], source['name'], source['createtime'], fields['DISPLAYTYPE'],fields['DisplayName'],fields['FORMTYPE'],
                                   fields['CDuration'], fields['Detail'],fields['KEYWORDS']['keyword']['keywordName'],fields['propertyFileLists']['propertyFile']])
                elif isinstance(fields['KEYWORDS']['keyword'], list):
                    keyword = []
                    for iter in fields['KEYWORDS']['keyword']:
                        if 'keywordName' in iter.keys():
                            keyword.append(iter['keywordName'])
                    result.append([source['contid'], source['name'], source['createtime'], fields['DISPLAYTYPE'],fields['DisplayName'],
                                   fields['FORMTYPE'], fields['CDuration'], fields['Detail'],keyword, fields['propertyFileLists']['propertyFile']])
                else:
                    raise Exception

        else:
            raise Exception

    #print(result)
    return result


if __name__ == '__main__':
    es_search(['643915567', '', '642841518', '643873477', '645764898', '646207801', '639293669', '642979685', '642738197', '639083484', '625450413', '622077530',
	'646002875','645081536', '644196554', '642080857', '632173109', '644184159', '645834542', '646118168', '624310085', '646496784', '646318479', '646339315', '623880296',
	'646105897', '623812166', '636172578', '646210405', '646358954', '628026703', '646158246', '638656656', '646121355', '640311739', '646290736', '646238591',
	'646256224', '646344501', '642946667', '645792907', '644418524', '638228484', '643845109', '646182666', '645942398', '645991037', '646285552', '646171085', '644100456',
	'645424190', '616047437', '642861610', '645395526', '645412703', '645456154', '646319791', '646192052', '645842804', '637402589', '630669153', '627142725', '638414285',
	'645336438', '646126911', '644456044', '645951007', '643338956', '614930298', '645387506', '646391731', '622604374', '639277280', '645214906', '636527813', '644358497',
	'646458023', '645629586', '644668658', '634030254', '646482627', '623531415', '630977898', '637605366', '641885820', '640280973', '644433036', '644927192', '628766425',
	'632337601', '646008026', '645813699', '631223828', '636136146', '645213066', '646010716', '646041544', '627036451', '646201684', '646123891'])