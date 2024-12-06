import requests
import time
import hashlib
import math
import os

from api.getToken import getToken
from dataWithCallback import DataWithCallback
from tools import tryRequests

host = "https://open-api.123pan.com"
verify=True
#创建文件
# Body 参数
# 名称	类型	是否必填	说明
# parentFileID	number	必填	父目录id，上传到根目录时填写 0
# filename	string	必填	文件名要小于255个字符且不能包含以下任何字符："\/:*?|><。（注：不能重名）
# etag	string	必填	文件md5
# size	number	必填	文件大小，单位为 byte 字节

def deleteFile(token, fileIDs):
    url=host+"/api/v1/file/trash"
    headers = {
        "Authorization": "Bearer "+getToken(),
        "Platform":"open_platform"
    }
    data = {
        "FileIDs": fileIDs
    }
    code,response = tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)

    if code != 0:
        print("deleteFile",response.json())
        return code
    return code
