import requests
import getToken as Token
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

def createFolder(token, parentID, folderName):
    url=host+"/upload/v1/file/mkdir"
    headers = {
        "Authorization": "Bearer "+token,
        "Platform":"open_platform"
    }
    data = {
        "name": folderName,
        "parentID": parentID
    }
    code,response = tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)

    if code != 0:
        print("createFolder",response.json())
        return code,0
    return code,response.json()["data"]["dirID"]


# findFloader(Token.getToken(), r"\testd22d\d2\d1d4", {":id":0})


