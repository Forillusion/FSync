import os.path

from tools import splitPath
from var import v


def recursionCompareData(localData, scanData, path=''):
    createQueue = []
    updateQueue = []
    deleteQueue = []

    def recursionCreateFile(scanData, path):
        createQueue = []
        for key in scanData:  # 遍历扫描数据库，处理扫描数据库有而本地数据库没有的文件（创建）
            if v.timeKey in scanData[key]:  # 文件
                createQueue.append((path + '\\' + key, scanData[key][v.timeKey]))
                v.totalStatus["createFiles"] += 1
                v.totalStatus["uploadSize"] += os.path.getsize(path + '\\' + key)
            else:   # 文件夹
                createQueue.append((path + '\\' + key, 0))
                v.totalStatus["createFolder"] += 1
                subCreate = recursionCreateFile(scanData[key], path + '\\' + key) # 递归扫描子文件夹
                createQueue.extend(subCreate)
        return createQueue

    for key in localData:  # 遍历本地数据库，处理本地数据库有而扫描数据库没有的文件（删除），以及本地数据库和扫描数据库的文件时间戳不同的文件（更新）

        if key not in scanData:  # 如果本地数据库的key不在扫描数据库中（删除）
            if v.cTask["deleteCloudFile"]:  # 根据任务设置，是否删除云盘文件
                if v.timeKey in localData[key]:  # 文件
                    deleteQueue.append((path + '\\' + key, -1))
                    v.total["deleteFiles"] += 1
                else:  # 文件夹
                    deleteQueue.append((path + '\\' + key, 0))
                    v.total["deleteFolder"] += 1

        else:
            if v.timeKey in localData[key]:  # 文件
                if localData[key][v.timeKey] != scanData[key][v.timeKey]:  # 本地文件和扫描文件的时间戳不同（更新）
                    updateQueue.append((path + "\\" + key, scanData[key][v.timeKey]))
                    v.total["updateFiles"] += 1
                    v.total["uploadSize"] += os.path.getsize(path + '\\' + key)
            else:
                subCreat, subUpdate, subDelete = recursionCompareData(localData[key], scanData[key],
                                                                      path + '\\' + key)  # 递归扫描子文件夹
                createQueue.extend(subCreat)
                updateQueue.extend(subUpdate)
                deleteQueue.extend(subDelete)

    for key in scanData:  # 遍历扫描数据库，处理扫描数据库有而本地数据库没有的文件（创建）
        if key not in localData:
            if v.timeKey in scanData[key]:  # 文件
                createQueue.append((path + "\\" + key, scanData[key][v.timeKey]))
                v.total["createFiles"] += 1
                v.total["uploadSize"] += os.path.getsize(path + '\\' + key)
            else:   # 文件夹
                createQueue.append((path + "\\" + key, 0))
                v.total["createFolder"] += 1
                subCreat = recursionCreateFile(scanData[key], path + "\\" + key)  # 递归扫描子文件夹
                createQueue.extend(subCreat)

    return createQueue, updateQueue, deleteQueue


def compareData(localData, scanData, localRoot):
    folders = splitPath(localRoot)
    currentScan = scanData
    for folder in folders:
        if folder not in currentScan:
            currentScan[folder] = {}
        currentScan = currentScan[folder]

    currentLocal = localData
    for folder in folders:
        if folder not in currentLocal:
            currentLocal[folder] = {}
        currentLocal = currentLocal[folder]

    return recursionCompareData(currentLocal, currentScan, localRoot)


def generateQueue(createQueue, updateQueue, deleteQueue):
    upQueue = []
    for key in createQueue:
        if key[1] == 0:
            upQueue.append({"path": key[0], "tryTime": 0, "status": "create folder"})
        else:
            upQueue.append({"path": key[0], "tryTime": 0, "status": "create file", "time": key[1]})

    for key in updateQueue:
        if key[1] == 0:
            upQueue.append({"path": key[0], "tryTime": 0, "status": "update folder"})
        else:
            upQueue.append({"path": key[0], "tryTime": 0, "status": "update file", "time": key[1]})

    for key in deleteQueue:
        if key[1] == 0:
            upQueue.append({"path": key[0], "tryTime": 0, "status": "delete folder"})
        else:
            upQueue.append({"path": key[0], "tryTime": 0, "status": "delete file"})
    return upQueue

# upQueue.append({"path":r"E:\Python\ForillusionSync\0","tryTime":0,"status":"new file"})
