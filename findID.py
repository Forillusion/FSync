from api.createFolder import createFolder
from tools import localPathToCloud, splitPath
from time import sleep

def findFloaderID(token,cloudPath, data):
    # 给出一个文件夹路径，返回文件夹的id，如果不存在则创建
    folders=splitPath(cloudPath)
    # print(folders)
    current=data
    code=0
    for folder in folders:
        # print("folder",folder)
        if folder not in current:
            code,dirID= createFolder(current[":id"], folder)
            if code!=0:
                return code,0
            current[folder]={":id":dirID}
            sleep(0.5)
        current=current[folder]

    return code,current[":id"]


def getCloudFloderID(token, path, cloudData, localRoot, cloudRoot):
    # 给出一个本地文件夹路径，转换为云盘文件夹路径，然后返回文件夹的id，如果不存在则创建
    path=localPathToCloud(path,localRoot,cloudRoot)
    return findFloaderID(token,path, cloudData)


def findFileID(token, cloudPath, data):
    # 给出一个文件路径，返回文件的id
    folders=splitPath(cloudPath)
    filename=folders[-1]
    folders=folders[:-1]

    # print(folders)
    current=data
    code=0
    for folder in folders:
        # print("folder",folder)
        if folder not in current:
            code,dirID= createFolder(current[":id"], folder)
            if code!=0:
                return code,0
            current[folder]={":id":dirID}
            sleep(0.5)
        current=current[folder]

    if filename not in current:
        return -2,0

    return code,current[filename][":id"]


def getCloudFileID(token, path, cloudData, localRoot, cloudRoot):
    path=localPathToCloud(path,localRoot,cloudRoot)
    return findFileID(token,path, cloudData)

def findParentID(token, cloudPath, data):
    folders=splitPath(cloudPath)
    filename=folders[-1]
    folders=folders[:-1]

    current=data
    code=0
    for folder in folders:
        if folder not in current:
            code,dirID= createFolder(current[":id"], folder)
            if code!=0:
                return code,0
            current[folder]={":id":dirID}
            sleep(0.5)
        current=current[folder]

    return code,current[":id"]

def getParentID(token, path, cloudData, localRoot, cloudRoot):
    path=localPathToCloud(path,localRoot,cloudRoot)
    return findParentID(token,path, cloudData)
#
# testData={
#     ":id": 0,
#     "testdd": {
#         ":id": 10760869,
#         "1.txt": {
#             ":id": 10765577
#         },
#         "2.txt": {
#             ":id": 10765573
#         }
#     }
# }
# print(getParentID("123",r"E:\testdd\11\3.txt",{},testData,r"E:\testdd",r"\testdd"))