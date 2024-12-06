import requests
import time
import getToken as Token
import hashlib
import math
import os
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

def createFile(token, parentFileId, filename, etag, size):
    url=host+"/upload/v1/file/create"
    headers = {
        "Authorization": "Bearer "+token,
        "Platform":"open_platform"
    }
    data = {
        "parentFileId": parentFileId,
        "filename": filename,
        "etag": etag,
        "size": size
    }
    code,response= tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)

    if code != 0:
        print("getFileCreate",response.json())
        return code,"",False,0,0
    return code,response.json()["data"]["preuploadID"],response.json()["data"]["reuse"],response.json()["data"]["sliceSize"],response.json()["data"]["fileID"] if response.json()["data"]["fileID"] else 0

#列举已上传分片
def getListUploadParts(token, preuploadID):
    url=host+"/upload/v1/file/list_upload_parts"
    headers = {
        "Authorization": "Bearer "+token,
        "Platform":"open_platform"
    }
    data = {
        "preuploadID": preuploadID
    }
    code,response= tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)

    if code != 0:
        print("getListUploadParts",response.json())
        return code,""
    return code,response.json()["data"]["parts"]

#获取上传地址
def getUploadUrl(token, preuploadID,sliceNo=1):
    url=host+"/upload/v1/file/get_upload_url"
    headers = {
        "Authorization": "Bearer "+token,
        "Platform":"open_platform"
    }
    data = {
        "preuploadID": preuploadID,
        "sliceNo": sliceNo
    }
    code,response= tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)

    if code != 0:
        print("getUploadUrl",response.json())
        return code,""
    return code,response.json()["data"]["presignedURL"]

#上传文件分片
def uploadFileSlice(url,filePath,sliceSize,sliceNo=1):
    data=None
    with open(filePath, 'rb') as f:
        f.seek((sliceNo-1)*sliceSize)
        x = f.read(sliceSize)
        data = DataWithCallback(x)

    # L=time.perf_counter()
    # x=file[(sliceNo-1)*sliceSize:min(sliceNo*sliceSize,len(file))]
    # print("分片加载用时(ms):",(time.perf_counter()-L)*1000)

    header = {
        "Content-Length": str(data.len),
    }

    MB=data.len/1024/1024
    print(f"上传分片{sliceNo}  {MB:.2f}MB",end="  \n")
    startTime=time.time()

    # code,response=tryRequests(requests.put,url=url, headers=header,data=data,verify=verify)
    response = requests.put(url, headers=header,data=data,verify=verify)
    print()

    if response.status_code == 200:
        print(f"\033[32m分片{sliceNo}上传成功\033[0m",end="  \t")
        endTime=time.time()
        print(f"用时：{(endTime-startTime):.2f}s  \t速度：{MB/(endTime-startTime):.2f} MB/S",end="  \t")
        md5=data.getMD5()
        if (response.headers["ETag"].replace('"','')==md5):
            print(f"MD5验证：\033[32mTrue\033[0m")
            return 200
        else:
            print(f"MD5验证：\033[31mTrue\033[0m")
            return -1
    else:
        print(f"\033[31m上传失败\033[0m")
        return response.status_code

#上传完毕
def uploadComplete(token, preuploadID):
    url=host+"/upload/v1/file/upload_complete"
    headers = {
        "Authorization": "Bearer "+token,
        "Platform":"open_platform"
    }
    data = {
        "preuploadID": preuploadID
    }
    code,response= tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)

    if code != 0:
        print("uploadComplete",response.json())
        return code,True,False,0
    return code,response.json()["data"]["completed"],response.json()["data"]["async"],response.json()["data"]["fileID"]


#异步轮询获取上传结果
def uploadAsyncResult(token, preuploadID):
    url=host+"/upload/v1/file/upload_async_result"
    headers = {
        "Authorization": "Bearer "+token,
        "Platform":"open_platform"
    }
    data = {
        "preuploadID": preuploadID
    }
    code,response= tryRequests(requests.post, url=url, headers=headers, data=data, verify=verify)
    # response = requests.post(url, headers=headers, data=data,verify=verify)
    if code!=0:
        print("uploadAsyncResult",response.json())
        return code,True,0
    return code,response.json()["data"]["completed"],response.json()["data"]["fileID"]

#计算文件md5
def getMD5(file):
    L=time.perf_counter()
    md5 = hashlib.md5(file).hexdigest()
    print("文件总MD5计算用时(ms):",(time.perf_counter()-L)*1000)
    return md5

#计算分片md5
def getSliceMD5(filePath,sliceSize,sliceNo=1):
    L=time.perf_counter()
    with open(filePath, 'rb') as f:
        f.seek((sliceNo-1)*sliceSize)
        data = f.read(sliceSize)
        md5 = hashlib.md5(data).hexdigest()
        print("分片MD5计算用时(ms):",(time.perf_counter()-L)*1000)
        return md5

#计算文件大小，单位为 byte 字节
def getSize(filePath):
    return os.path.getsize(filePath)

def upload(path,parentFileId):
    with open(path, 'rb') as f:
        L=time.perf_counter()
        file=f.read()
        print("文件加载用时(ms):",(time.perf_counter()-L)*1000)

        token=Token.getToken()
        fileName=os.path.basename(path)
        MD5=getMD5(file)

        size=len(file)

        if (size/1024/1024>=1024):
            print(f"文件大小{size/1024/1024/1024:.2f}GB")
        else:
            print(f"文件大小{size/1024/1024:.2f}MB")

        preuploadID,reuse,sliceSize=createFile(token, parentFileId, fileName, MD5, size)
        print("分片大小：",sliceSize/1024/1024,"MB")

        if reuse:
            print("秒传成功")

        elif size<=sliceSize:
            upurl=getUploadUrl(token,preuploadID)
            uploadFileSlice(upurl,file,sliceSize)
            uploadComplete(token,preuploadID)

        else:
            totalSlice=math.ceil(size/sliceSize)
            print("分片总数：",totalSlice)

            currentSlice=1
            while currentSlice<=totalSlice:
                upurl=getUploadUrl(token,preuploadID,currentSlice)
                status=uploadFileSlice(upurl,file,sliceSize,currentSlice)
                if status==200:
                    currentSlice+=1

            completed,ifasync=uploadComplete(token,preuploadID)
            if completed:
                print("\033[32m上传完成\033[0m")
            elif ifasync:
                while not completed:
                    time.sleep(2)
                    completed=uploadAsyncResult(token,preuploadID)
                print("\033[32m上传完成\033[0m")