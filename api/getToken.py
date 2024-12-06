import requests
import json
import time

from tools import tryRequests

host = "https://open-api.123pan.com"
AKSKPath=r"E:\123panAKSK.txt"
tokenPath = r"E:\123panToken.txt"
def readAKSK():
    with open(AKSKPath, 'r') as f:
        data = f.read()
    return json.loads(data)

def requestToken():

    url=host+"/api/v1/access_token"
    headers = {
        "Platform":"open_platform"
    }
    data = readAKSK()
    code,response = tryRequests(requests.post,url=url, headers=headers, data=data)
    # print(response.json())
    return response.json()["data"]

def saveToken(data):
    with open(tokenPath, 'w') as f:
        json.dump(data, f)

def readToken():
    data =  ""
    token = ""
    expiredAt = ""  # 2025-01-02T10:11:02+08:00
    with open(tokenPath, 'r') as f:
        data = f.read()
    token = json.loads(data)["accessToken"]
    expiredAt = json.loads(data)["expiredAt"]
    return token, expiredAt

def checkToken(token, expiredAt):
    if expiredAt < time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()):
        return False
    return True

def getToken():
    token, expiredAt = readToken()
    if not checkToken(token, expiredAt):
        print("token无效，重新获取")
        data=requestToken()
        saveToken(data)
        return data["accessToken"]
    return token

