import urllib2

url = "http://183./web"
postdata = dict(d=2, p=10)
post = []
post.append(postdata)
req = urllib2.Request(url, json.dumps(post)) #需要是json格式的参数
req.add_header('Content-Type', 'application/json') #要非常注意这行代码的写法
response = urllib2.urlopen(req)
result = json.loads(response.read())
print(result)
