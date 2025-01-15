from api.createFolder import createFolder
from database import saveDB, saveCloudData, getCloudListToData
from tools import localPathToCloud, splitPath
from time import sleep

from var import v


def findFloaderID(path):
    cloudPath = localPathToCloud(path)
    # 给出一个本地文件夹路径，转换为云盘文件夹路径，然后返回文件夹的id，如果不存在则创建,并写入数据库
    folders = splitPath(cloudPath)
    current = v.cloudData
    code = 0
    for folder in folders:
        # print("folder",folder)
        if folder not in current:
            code, dirID = createFolder(current[v.idKey], folder)
            if code != 0:
                return code, 0
            current[folder] = {v.idKey: dirID}
            sleep(0.5)
            saveCloudData()
        current = current[folder]

    return code, current[v.idKey]


# def getCloudFloderID(path):
#
#     path= localPathToCloud(path)
#     return findFloaderID(path)


def findFileID(path):
    # 给出一个文件路径，返回文件的id，会创建文件夹并写入数据库，但不会创建文件，如果不存在则返回-2
    cloudPath = localPathToCloud(path)
    folders = splitPath(cloudPath)
    folders = folders

    # print(folders)
    current = v.cloudData
    code = 0
    for folder in folders:
        # print("folder",folder)
        if folder not in current:
            print("id获取失败，尝试重新获取文件夹列表：",cloudPath)
            getCloudListToData(cloudPath[:-len(folder)])
        if folder not in current:
            print("id获取失败，重新获取文件夹失败：",cloudPath)
            return -2, 0
        current = current[folder]

    return code, current[v.idKey]


# def findFileID(path):
#     # 给出一个文件路径，返回文件的id，会创建文件夹并写入数据库，但不会创建文件，如果不存在则返回-2
#     cloudPath= localPathToCloud(path)
#     folders=splitPath(cloudPath)
#     filename=folders[-1]
#     folders=folders[:-1]
#
#     # print(folders)
#     current=v.cloudData
#     code=0
#     for folder in folders:
#         # print("folder",folder)
#         if folder not in current:
#             code,dirID= createFolder(current[":id"], folder)
#             if code!=0:
#                 return code,0
#             current[folder]={":id":dirID}
#             sleep(0.5)
#         current=current[folder]
#
#     if filename not in current:
#         return -2,0
#
#     return code,current[filename][":id"]


# def getCloudFileID(path):
#     path= localPathToCloud(path)
#     return findFileID(path)

def findParentID(path):
    # 给出一个文件路径，返回文件的父文件夹的id，会创建文件夹并写入数据库
    # print("path:",path)
    cloudPath = localPathToCloud(path)
    folders = splitPath(cloudPath)

    filename = folders[-1]
    folders = folders[:-1]

    current = v.cloudData
    code = 0
    for folder in folders:
        if folder not in current:
            code, dirID = createFolder(current[v.idKey], folder)
            if code != 0:
                return code, 0
            current[folder] = {v.idKey: dirID}
            sleep(0.5)
            saveCloudData()
        current = current[folder]

    # print("current:",current)
    try:
        return code, current[v.idKey]
    except Exception as e:
        print(path)
        print(current)
        print("findParentID error:", e)
        exit(0)

# def getParentID(path):
#     path= localPathToCloud(path)
#     return findParentID(path)
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
