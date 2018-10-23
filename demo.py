# -*- encoding: utf-8 -*-
import json
from elasticsearch import Urllib3HttpConnection, Elasticsearch

class MyConnection(Urllib3HttpConnection):
    def __init__(self, *args, **kwargs):
        extra_headers = kwargs.pop('extra_headers', {})
        super(MyConnection, self).__init__(*args, **kwargs)
        self.headers.update(extra_headers)

def query_data(list):
    query_data = {
        "query":{
            "bool":{
                "must":[
                    {
                        "query_string":{
                            "query": list
                        }
                    }
                ]
            }
        }
    }
    return query_data

def es_search(list):
    es = Elasticsearch("http://183.192.162.101:8080", send_get_body_as='POST',connection_class=MyConnection,extra_headers={'kbn-version':'6.1.1'})
    data = '{"index":["poms"]}\n' + json.dumps(query_data(list))
    res = es.msearch(index='elasticsearch',body = data)

    f = open('result.txt', 'w')
    f.write(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    # 测试单例
    es_search(503001675)
