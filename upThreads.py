import hashlib
import math
import multiprocessing
import os
import queue
from hashlib import md5
from time import sleep

from createFolder import createFolder
from database import updataBothData
from findID import getCloudFloderID, getCloudFileID, getParentID
from delete import deleteFile
from getToken import getToken
from tools import localPathToCloud
from upload import uploadComplete, uploadAsyncResult, createFile, getUploadUrl
from var import Singleton

def preThread():
    # upQueue, sliceQueue, reUpQueue, checkQueue, finishQueue, failQueue, localRoot, cloudRoot, localData, cloudData=
    v=Singleton()
    upQueue = v.upQueue
    sliceQueue = v.sliceQueue
    reUpQueue = v.reUpQueue
    checkQueue = v.checkQueue
    finishQueue = v.finishQueue
    failQueue = v.failQueue
    localRoot = v.localRoot
    cloudRoot = v.cloudRoot
    localData = v.localData
    cloudData = v.cloudData

    preThreadIdle = v.preThreadIdle
    quitFlag = v.quitFlag

    def preCreateFolder():
        code, dirID = getCloudFloderID(getToken(), current["path"],cloudData,localRoot, cloudRoot)
        if code != 0:
            console(1, f"{current['fillName']} 文件夹创建失败")
            reUpQueue.put(current)

        console(1, f"{current['fillName']} 文件夹创建成功")
        updataBothData(localData, cloudData, current["path"], localPathToCloud(current["path"],localRoot,cloudRoot), "create folder", 0,dirID)
        finishQueue.append(current)

    def preDeleteFolder():
        code, dirID = getCloudFloderID(getToken(), current["path"],cloudData,localRoot, cloudRoot)
        if code == 0:
            code = deleteFile(getToken(), dirID)

        if code != 0:
            console(1, f"{current['fillName']} 删除云盘文件夹失败")
            reUpQueue.put(current)
        console(1, f"{current['fillName']} 删除云盘文件夹成功")
        updataBothData(localData, cloudData, current["path"], localPathToCloud(current["path"],localRoot,cloudRoot), "delete folder")
        finishQueue.append(current)

    def preDeleteFile():
        code,fileID = getCloudFileID(getToken(), current["path"],cloudData,localRoot, cloudRoot)
        if code==0:
            code = deleteFile(getToken(), fileID)

        if code != 0:
            console(1, f"{current['fillName']} 删除云盘文件失败")
            reUpQueue.put(current)

        console(1, f"{current['fillName']} 删除云盘文件成功")
        updataBothData(localData, cloudData, current["path"], localPathToCloud(current["path"],localRoot,cloudRoot), "delete file")
        sleep(0.5)
        if current["status"] == "update file":
            current["status"] = "create file"
        else:
            finishQueue.append(current)

    while not v.quitFlag:
        while not reUpQueue.empty():
            v.preThreadIdle = False
            get = reUpQueue.get()
            console(1, f"重新上传队列获取到文件 {get['fillName']}")
            if get["tryTime"] < maxTryTime:
                console(1, f"{get['fillName']} 重试次数 {get['tryTime']}")
                upQueue.append(get)

        if len(upQueue) > 0 and sliceQueue.qsize() < 5:
            v.preThreadIdle = False

            current = upQueue[-1]
            upQueue.pop()
            current["fillName"] = os.path.basename(current["path"])
            console(1, f"获取到新文件 {current['fillName']} {current["status"]} ,剩余{len(upQueue)}个文件")

            current["tryTime"] += 1

            if current["status"] == "create folder":
                preCreateFolder()

            if current["status"] == "delete file" or current["status"] == "update file":
                preDeleteFile()

            if current["status"] == "delete folder":
                preDeleteFolder()

            if current["status"] == "create file":

                size = current["size"] = getSize(current["path"])
                md5 = getMD5(current["path"], 2 ** 22)  # 2**22 = 4MB
                fileName = os.path.basename(current["path"])

                code,parentFileId = getParentID(getToken(),current["path"],cloudData,localRoot, cloudRoot)
                if code==0:
                    current["parentFileId"]=parentFileId
                    code, preuploadID, reuse, sliceSize,fileID = createFile(getToken(), current["parentFileId"], fileName, md5,
                                                                 size)

                if code != 0:
                    console(1, f"{current['fillName']} 创建文件失败")
                    reUpQueue.put(current)
                    continue

                current["reuse"] = reuse
                if reuse:
                    updataBothData(localData, cloudData, current["path"], localPathToCloud(current["path"],localRoot,cloudRoot), "create file", current["time"], fileID)
                    console(1, f"\033[32m{current["fillName"]} 秒传成功\033[0m")
                    finishQueue.append(current)
                    sleep(0.5)
                else:
                    current["preuploadID"] = preuploadID
                    current["sliceSize"] = sliceSize
                    current["totalSlice"] = math.ceil(size // sliceSize) + 1
                    current["finishSlice"] = 0
                    for i in range(current["totalSlice"]):
                        slice = current.copy()
                        slice["currentSlice"] = i + 1
                        slice["sliceMD5"] = getSliceMD5(current["path"], sliceSize, i + 1)

                        code, slice["URL"] = getUploadUrl(getToken(), current["preuploadID"], i + 1)
                        if code != 0:
                            reUpQueue.put(current)
                            if i != 0:
                                sliceQueue.put({"path": current["path"], "clean": True})
                            break

                        console(1, f"{slice['fillName']} 分片 {slice["currentSlice"]} 发送到分片队列")
                        sliceQueue.put(slice)
                        sleep(1)

        else:
            v.preThreadIdle = True
            sleep(0.1)


def upThread():
    v=Singleton()
    upQueue = v.upQueue
    sliceQueue = v.sliceQueue
    reUpQueue = v.reUpQueue
    checkQueue = v.checkQueue
    finishQueue = v.finishQueue
    failQueue = v.failQueue
    localRoot = v.localRoot
    cloudRoot = v.cloudRoot
    localData = v.localData
    cloudData = v.cloudData

    upThreadIdle = v.upThreadIdle
    quitFlag = v.quitFlag
    global upSteam
    global returnSteam
    cleanFile = ""
    while not v.quitFlag:
        if not sliceQueue.empty():
            v.upThreadIdle = False
            current = sliceQueue.get()
            console(2, f"获取到分片 {current['fillName']} 分片 {current['currentSlice']}")

            if "clean" in current:
                cleanFile = current["path"]
            if current["path"] == cleanFile:
                console(2, f"{current['fillName']} 上传失败，已重新加入上传队列 upQueue")
                continue

            cleanFile = ""
            tryTime = 0
            while True:
                tryTime += 1

                upSteam.put(current)
                while returnSteam.empty():
                    sleep(0.1)
                status = returnSteam.get()

                if status == 200:
                    console(2, f"{current['fillName']} 分片 {current['currentSlice']} 上传完成")

                    if current["currentSlice"] == current["totalSlice"]:
                        console(2, f"{current['fillName']} 全部分片上传完成，加入校验队列")
                        checkQueue.put(current)
                    break
                else:
                    console(2, f"{current['fillName']} 分片 {current['currentSlice']} 上传失败")
                    if tryTime >= maxTryTime:
                        cleanFile = current["path"]
                        console(2, f"{current['fillName']} 上传失败次数超过 {maxTryTime} 次，加入重新上传队列")
                        reUpQueue.put(current)
                        break
        else:
            v.upThreadIdle = True
            sleep(0.1)


def checkThread():
    v=Singleton()
    upQueue = v.upQueue
    sliceQueue = v.sliceQueue
    reUpQueue = v.reUpQueue
    checkQueue = v.checkQueue
    finishQueue = v.finishQueue
    failQueue = v.failQueue
    localRoot = v.localRoot
    cloudRoot = v.cloudRoot
    localData = v.localData
    cloudData = v.cloudData

    checkThreadIdle = v.checkThreadIdle
    quitFlag = v.quitFlag
    while not v.quitFlag:
        if not checkQueue.empty():
            v.checkThreadIdle = False
            current = checkQueue.get()
            console(3, f"获取到校验文件 {current['fillName']}")

            code, completed, ifasync,fileID = uploadComplete(getToken(), current["preuploadID"])
            if completed:
                pass
            elif ifasync:
                while code == 0 and not completed:
                    code, completed,fileID = uploadAsyncResult(getToken(), current["preuploadID"])
                    sleep(1)

            if code == 0:
                updataBothData(localData, cloudData, current["path"], localPathToCloud(current["path"],localRoot,cloudRoot), "create file", current["time"],fileID)
                finishQueue.append(current)
                console(3, f"\033[32m{current["fillName"]}上传完成\033[0m")
            else:
                console(3, f"\033[31m{current["fillName"]}上传失败\033[0m")
                reUpQueue.put(current)
        else:
            # print("thread3: 上传队列为空或分片队列已满")
            v.checkThreadIdle = True
            sleep(0.1)


def getMD5(filePath, b):
    file = open(filePath, 'rb')
    h = md5()
    buf = bytearray(b)  # 1MB buffer

    view = memoryview(buf)
    while sz := file.readinto(buf):
        pass
        h.update(view[:sz])
    return h.hexdigest()


def getSize(filePath):
    return os.path.getsize(filePath)


def getSliceMD5(filePath, sliceSize, sliceNo=1):
    with open(filePath, 'rb') as f:
        f.seek((sliceNo - 1) * sliceSize)
        data = f.read(sliceSize)
        md5 = hashlib.md5(data).hexdigest()
        return md5


def console(index, msg):
    cols = 239
    l = int((index - 1) * cols * (1 / 3))
    print(" " * l, end="")
    print(msg)


maxTryTime = 3

upSteam = multiprocessing.Queue()
controlSteam = multiprocessing.Queue()
returnSteam = multiprocessing.Queue()

