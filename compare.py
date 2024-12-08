from tools import splitPath
from var import v


def recursionCompareData(localData, scanData, path=''):
    def recursionCreateFile(scanData, path):
        createQueue = []
        for key in scanData:
            if v.timeKey in scanData[key]:
                createQueue.append((path + '\\' + key, scanData[key][v.timeKey]))
            else:
                createQueue.append((path + '\\' + key, 0))
                subCreate = recursionCreateFile(scanData[key], path + '\\' + key)
                createQueue.extend(subCreate)
        return createQueue

    createQueue = []
    updateQueue = []
    deleteQueue = []
    for key in localData:
        if key not in scanData:
            if v.timeKey in localData[key]:
                deleteQueue.append((path + '\\' + key, -1))
            else:
                deleteQueue.append((path + '\\' + key, 0))

        else:
            if v.timeKey in localData[key]:
                if localData[key][v.timeKey] != scanData[key][v.timeKey]:
                    updateQueue.append((path + "\\" + key, scanData[key][v.timeKey]))
            else:
                subCreat, subUpdate, subDelete = recursionCompareData(localData[key], scanData[key], path + '\\' + key)
                createQueue.extend(subCreat)
                updateQueue.extend(subUpdate)
                deleteQueue.extend(subDelete)

    for key in scanData:
        if key not in localData:
            if v.timeKey not in scanData[key]:
                createQueue.append((path + "\\" + key, 0))
                subCreat = recursionCreateFile(scanData[key], path + "\\" + key)
                createQueue.extend(subCreat)
            else:
                createQueue.append((path + "\\" + key, scanData[key][v.timeKey]))
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
