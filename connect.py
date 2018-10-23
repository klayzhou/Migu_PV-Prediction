# -*- encoding: utf-8 -*-
from urllib import request
import json

def query(list):
    query_data = {
        "size":100,
        "query":{
            'constant_score':{
                 'filter':{
                     'terms':{
                         'contid': list
                     }
                 }
            }
        }
    }
    return query_data

def es_search(list):

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

if __name__ == "__main__":
    es_search([647206502])