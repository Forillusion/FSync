import json
import os

from api.fileList import getAllFileListOld
from tools import splitPath
from var import v


def load(path):
    # 如果文件夹不存在，创建文件夹
    folders=splitPath(path)
    current=""
    for folder in folders[:-1]:
        current+=folder+"\\"
        if not os.path.exists(current):
            os.mkdir(current)

    if not os.path.exists(path):
        save(path)

    with open(path,"r") as f:
        return f.read()

def loadCloudData():
    data=load(r"db\cloudData.json")
    if data == "":
        data = '{":id":0}'
    v.cloudData=json.loads(data)
    getCloudListToData(v.cloudRoot)

# def loadLocalData():
#     data=load(r"db\localData.json")
#     if data == "":
#         data = '{"E:":{}}'
#     v.localData=json.dumps(data)

def save(path,data):
    with open(path,"w") as f:
        f.write(json.dumps(data))

def updateCloudData(data, path, status, id=0, autoSave=True):
    folders=splitPath(path)
    lens=len(folders)
    i=0
    current = data
    if status == "create folder" or status == "create file":
        for folder in folders:
            i+=1
            if folder not in current:
                current[folder] = {}
            current = current[folder]
        current[":id"] = id

    if status == "delete folder" or status == "delete file":
        for folder in folders:
            i+=1
            if folder not in current:
                raise Exception(f"Cloud database error: folder {folder} not found,path:{path}")
            if i<lens:
                current = current[folder]
        del current[folders[-1]]

    if autoSave:
        save("db/cloudData.json", data)

def updataLocalData(data, path, status, time=0, autoSave=True):
    folders=splitPath(path)
    lens=len(folders)
    i=0
    current = data
    if status == "create folder" or status == "create file":
        for folder in folders:
            i+=1
            if folder not in current:
                current[folder] = {}
            current = current[folder]
        if status == "create file":
            current[v.timeKey] = time

    if status == "delete folder" or status == "delete file":
        for folder in folders:
            i+=1
            if folder not in current:
                raise Exception(f"local database error: folder {folder} not found,path:{path}")
            if i<lens:
                current = current[folder]
        del current[folders[-1]]

    if autoSave:
        save("db/localData.json", data)

def updataBothData(localData, cloudData,localPath,cloudPath,status,time=0,id=0,autoSave=True):
    updataLocalData(localData,localPath,status,time,autoSave)
    updateCloudData(cloudData,cloudPath,status,id,autoSave)

# testData =  {'E:': {'test': {'d1': {'d1t1.txt': {':time': 1733388906}}, 'd2': {'d2t1.txt': {':time': 1733388906}}, 't1': {}, 't1.txt': {':time': 1733388906}, 't2.txt': {':time': 1733388906}}}}
# updataLocalData(testData,r"E:\test\d1\d1t1.txt","delete file",133)
# print(testData)

# {
#     "fileID": 7007012,
#     "filename": "IMG_20240713_202200.jpg",
#     "parentFileId": 7006953,
#     "parentName": "",
#     "type": 0,
#     "etag": "394effbcf7a1cc35e9f5d797d103ef26",
#     "size": 3270406,
#     "contentType": "0",
#     "category": 3,
#     "hidden": false,
#     "status": 0,
#     "punishFlag": 0,
#     "s3KeyFlag": "1828275253-0",
#     "storageNode": "m44",
#     "createAt": "2024-07-16 00:04:46 +0800 CST",
#     "updateAt": "2024-07-17 19:41:19 +0800 CST",
#     "thumbnail": "",
#     "downloadUrl": ""
# }

def getCloudListToData(path):
    folders=splitPath(path)
    current = v.cloudData
    for folder in folders:
        if folder not in current:
            code, data = getAllFileListOld(current[":id"])
            if code==0:
                for x in data:
                    if x["filename"] not in current:
                        current[x["filename"]] = {":id":x["fileID"]}
                        # print(x["filename"])
            else:
                return code
        current = current[folder]

    return 0


def getLocalListToData(path):
    folders=splitPath(path)
    current = v.localData
    for folder in folders:
        if folder not in current:
            # data=scanLocalPath
            pass

if __name__=="__main__":
    loadCloudData()
    print(v.cloudData)

#
# def checkCloudRoot():
#     folders=splitPath(v.cloudRoot)
#     current = v.cloudData
#     for folder in folders:
#         if folder not in current:
#             current[folder] = {}
#         current = current[folder]