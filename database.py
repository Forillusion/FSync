import json
import os

from api.fileList import getAllFileListOld
from tools import splitPath, localPathToCloud
from var import v


def loadDB(path):
    # 如果文件夹不存在，创建文件夹
    folders = splitPath(path)
    current = ""
    for folder in folders[:-1]:
        current += folder + "\\"
        if not os.path.exists(current):
            os.mkdir(current)

    if not os.path.exists(path):
        saveDB(path)

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def loadCloudData():
    data = loadDB(v.cloudDataPath)
    if data == "":
        data = '{"' + v.idKey + '":0}'
    v.cloudData = json.loads(data)
    getCloudListToData(v.cloudRoot)


def loadLocalData():
    data = loadDB(v.localDataPath)
    if data == "":
        data = '{}'
    v.localData = json.loads(data)


def saveDB(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))


def updateCloudData(path, status, id=0, autoSave=True):
    folders = splitPath(path)
    lens = len(folders)
    i = 0
    current = v.cloudData
    if status == "create folder" or status == "create file":
        for folder in folders:
            i += 1
            if folder not in current:
                current[folder] = {}
            current = current[folder]
        current[v.idKey] = id

    if status == "delete folder" or status == "delete file":
        for folder in folders:
            i += 1
            if folder not in current:
                raise Exception(f"Cloud database error: folder {folder} not found,path:{path}")
            if i < lens:
                current = current[folder]
        del current[folders[-1]]

    if autoSave:
        saveDB("db/cloudData.json", v.cloudData)


def updataLocalData(path, status, time=0, autoSave=True):
    folders = splitPath(path)
    lens = len(folders)
    i = 0
    current = v.localData
    if status == "create folder" or status == "create file":
        for folder in folders:
            i += 1
            if folder not in current:
                current[folder] = {}
            current = current[folder]
        if status == "create file":
            current[v.timeKey] = time

    if status == "delete folder" or status == "delete file":
        for folder in folders:
            i += 1
            if folder not in current:
                raise Exception(f"local database error: folder {folder} not found,path:{path}")
            if i < lens:
                current = current[folder]
        del current[folders[-1]]

    if autoSave:
        saveDB("db/localData.json", v.localData)


def updataBothData(localPath, status, time=0, id=0, autoSave=True):
    updataLocalData(localPath, status, time, autoSave)
    updateCloudData(localPathToCloud(localPath), status, id, autoSave)


def getCloudListToData(path):
    folders = splitPath(path)
    current = v.cloudData
    for folder in folders:
        if folder not in current:
            code, data = getAllFileListOld(current[v.idKey])
            if code == 0:
                for x in data:
                    if x["filename"] not in current:
                        current[x["filename"]] = {v.idKey: x["fileID"]}
                        # print(x["filename"])
            else:
                return code
        current = current[folder]

    return 0


def getLocalListToData(path):
    folders = splitPath(path)
    current = v.localData
    for folder in folders:
        if folder not in current:
            # data=scanLocalPath
            pass


if __name__ == "__main__":
    loadCloudData()
    print(v.cloudData)
