import requests
import json
import math
import time
import numpy as np
from pymysql import connect
conn = connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='my_python', charset='utf8')
cur=conn.cursor()
#写日志
def write_log(str):
    with open("log.txt","a")as f:
        f.write(str+"\r")
    f.close()
#分割地图
def split_lat_lng(max_lat=40.179831,max_lng=116.672179,min_lat=39.707645,min_lng=116.111062,n=16):
    n=int(n**0.5)
    lat_li=[i for i in np.linspace(min_lat,max_lat,n+1)]
    lng_li=[i for i in np.linspace(min_lng,max_lng,n+1)]
    one_lat_lng=[]
    for i in lat_li[:-1]:
        for j in lng_li[:-1]:
            one_lat_lng.append((i,j))
    two_lat_lng=[]
    for i in lat_li[1:]:
        for j in lng_li[1:]:
            two_lat_lng.append((i,j))
    lat_lng=[]
    for i in range(n**2):
        lat_lng.append(one_lat_lng[i]+two_lat_lng[i])
    return lat_lng

#获得百度地图poi
def get_store(bounds,query_word,tag="",page_size=20,page_num=0):
    url="http://api.map.baidu.com/place/v2/search"
    params={
        "query": query_word,
        "tag": tag,
        "bounds": "{},{},{},{}".format(*bounds),
        "output": "json",
        "scope": "1",
        "ret_coordtype": "",
        "page_size": page_size,
        "page_num": page_num,
        "ak": "9vxMIuU4oYZbd3uGkrdhlq3FL15y0BlG",
    }
    r=requests.get(url,params=params)
    print(bounds, query_word)
    js=json.loads(r.text)
    status=js["status"]
    li=[]
    if status==0:
        total = js["total"]
        if total>=400:
            min_lat, min_lng,max_lat , max_lng =bounds
            log_str="{},{}".format(bounds,query_word)
            write_log(log_str)
            for lat_lng_lis in split_lat_lng(max_lat , max_lng,min_lat, min_lng):
                li+=get_store(lat_lng_lis,query_word)
        else:
            page_total = math.ceil(total / page_size)
            if page_num!=0:
                li += js["results"]
            else:
                li+=js["results"]
                for i in range(page_total):
                    if i>0:
                        li+=get_store(bounds,query_word,page_num=i)
                    time.sleep(0.1)
    return li

li=[(39.707644999999999, 116.111062, 39.825691499999998, 116.25134125), (39.707644999999999, 116.25134125, 39.825691499999998, 116.3916205), (39.707644999999999, 116.3916205, 39.825691499999998, 116.53189975000001), (39.707644999999999, 116.53189975000001, 39.825691499999998, 116.672179), (39.825691499999998, 116.111062, 39.943737999999996, 116.25134125), (39.825691499999998, 116.25134125, 39.943737999999996, 116.3916205), (39.825691499999998, 116.3916205, 39.943737999999996, 116.53189975000001), (39.825691499999998, 116.53189975000001, 39.943737999999996, 116.672179), (39.943737999999996, 116.111062, 40.061784500000002, 116.25134125), (39.943737999999996, 116.25134125, 40.061784500000002, 116.3916205), (39.943737999999996, 116.3916205, 40.061784500000002, 116.53189975000001), (39.943737999999996, 116.53189975000001, 40.061784500000002, 116.672179), (40.061784500000002, 116.111062, 40.179831, 116.25134125), (40.061784500000002, 116.25134125, 40.179831, 116.3916205), (40.061784500000002, 116.3916205, 40.179831, 116.53189975000001), (40.061784500000002, 116.53189975000001, 40.179831, 116.672179)]

query_words="便利店,超市,日用,百货,商店,杂货店,食品店,小卖部"
for query_word in query_words.split(","):
    for data in get_store((39.707645,116.111062,40.179831,116.672179),query_word):
        sql="INSERT INTO `store_location`(store_name,lat,lng,uid,datas,tag) VALUES (%s,%s,%s,%s,%s,%s)"
        store_name=data["name"]
        lat=data["location"]["lat"]
        lng=data["location"]["lng"]
        uid=data["uid"]
        datas=str(data)
        tag=query_word
        cur.execute(sql,(store_name,lat,lng,uid,datas,tag))
    conn.commit()


