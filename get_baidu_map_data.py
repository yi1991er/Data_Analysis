import requests
import json
import math
import time
def get_store(bounds,query_word="便利店",tag="",page_size=20,page_num=0):
    url="http://api.map.baidu.com/place/v2/search"
    params={
        "query": query_word,
        "tag": tag,
        "bounds": bounds,
        "output": "json",
        "scope": "1",
        "ret_coordtype": "",
        "page_size": page_size,
        "page_num": page_num,
        "ak": "9vxMIuU4oYZbd3uGkrdhlq3FL15y0BlG",
    }
    r=requests.get(url,params=params)
    js=json.loads(r.text)
    status=js["status"]
    li=[]
    print(page_num,len(js["results"]))
    if status==0:
        total = js["total"]
        page_total = math.ceil(total / page_size)
        if page_num!=0:
            li += js["results"]
        else:
            li+=js["results"]
            for i in range(1,page_total):
                li+=get_store(bounds,page_num=i)
                time.sleep(0.5)

    return li



data=get_store("39.687672,116.015173,40.62728,117.069568")
print(data)
print(len(data))