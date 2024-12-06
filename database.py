import json
import os

from tools import splitPath


def load(path):
    if not os.path.exists(path):
        save(path,"")

    with open(path,"r") as f:
        return f.read()


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
        save("cloudData.json",data)

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
            current[":time"] = time

    if status == "delete folder" or status == "delete file":
        for folder in folders:
            i+=1
            if folder not in current:
                raise Exception(f"local database error: folder {folder} not found,path:{path}")
            if i<lens:
                current = current[folder]
        del current[folders[-1]]

    if autoSave:
        save("localData.json",data)

def updataBothData(localData, cloudData,localPath,cloudPath,status,time=0,id=0,autoSave=True):
    updataLocalData(localData,localPath,status,time,autoSave)
    updateCloudData(cloudData,cloudPath,status,id,autoSave)

# testData =  {'E:': {'test': {'d1': {'d1t1.txt': {':time': 1733388906}}, 'd2': {'d2t1.txt': {':time': 1733388906}}, 't1': {}, 't1.txt': {':time': 1733388906}, 't2.txt': {':time': 1733388906}}}}
# updataLocalData(testData,r"E:\test\d1\d1t1.txt","delete file",133)
# print(testData)


