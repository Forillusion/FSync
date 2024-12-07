import json
import math
import requests
from time import sleep

from api.getToken import getToken
from tools import tryRequests

host = "https://open-api.123pan.com"
verify=True

def getFileList(parentFileId=0):
    url=host+"/api/v2/file/list"
    headers = {
        "Authorization": "Bearer "+getToken(),
        "Platform":"open_platform"
    }
    data = {
        "parentFileId": parentFileId,
        "limit": 100
    }
    response = requests.get(url, headers=headers, params=data)
    # print(response.text)
    return response.json()["data"]


def getFileListOld(parentFileId=0,page=1,limit=100):
    url=host+"/api/v1/file/list"
    headers = {
        "Authorization": "Bearer "+getToken(),
        "Platform":"open_platform"
    }
    data = {
        "parentFileId": parentFileId,
        "page": page,
        "limit": limit,
        "orderBy": "file_name",
        "orderDirection": "asc",
        "trashed": False
    }

    code,response = tryRequests(requests.get, url=url, headers=headers, params=data, verify=verify)
    # response = requests.get(url, headers=headers, params=data)

    if code != 0:
        print("getFileListOld",response.json())
        return code,{}
    return code,response.json()["data"]

def getAllFileListOld(parentFileId=0):
    list=[]
    code,data=getFileListOld(parentFileId)
    if code==0:
        total=data["total"]
        list=data["fileList"]

        for i in range(2,math.ceil(total/100)+1):
            sleep(0.8)
            code,data=getFileListOld(parentFileId,i)
            if code!=0:
                break
            list+=data["fileList"]

    if code!=0:
        return code,[]
    return code,list



if __name__ == "__main__":
    code,data=getAllFileListOld(0)
    with open("list.txt","w") as f:
        f.write(json.dumps(data))