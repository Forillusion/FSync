import hashlib
import math
import multiprocessing
import os
from hashlib import md5
from time import sleep

from database import updataBothData
from findID import findFloaderID, findFileID, findParentID
from api.delete import deleteFile
from tools import localPathToCloud
from api.upload import uploadComplete, uploadAsyncResult, createFile, getUploadUrl, getListUploadParts
from var import v


def preThread():
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
    finish = v.finish

    upSteam = v.upSteam
    controlSteam = v.controlSteam
    returnSteam = v.returnSteam

    def preCreateFolder():  # 创建文件夹
        code, dirID = findFloaderID(current["path"])
        if code != 0:
            console(1, f"\033[31m{current['fileName']} 文件夹创建失败\033[0m")
            reUpQueue.put(current)
            return

        console(1, f"\033[32m{current['fileName']} 文件夹创建成功\033[0m")
        updataBothData(current["path"], "create folder", 0, dirID)
        finishQueue.append(current)
        v.finishQueueChangeFlag = True
        finish["createFolder"] += 1

    def preDeleteFolder():  # 删除文件夹
        code, dirID = findFloaderID(current["path"])
        if code == 0:
            code = deleteFile(dirID)

        if code != 0:
            console(1, f"\033[31m{current['fileName']} 删除云盘文件夹失败\033[0m")
            reUpQueue.put(current)
            return

        console(1, f"\033[32m{current['fileName']} 删除云盘文件夹成功\033[0m")
        updataBothData(current["path"], "delete folder")
        finishQueue.append(current)
        v.finishQueueChangeFlag = True
        finish["deleteFolder"] += 1

    def preDeleteFile():  # 删除文件
        code, fileID = findFileID(current["path"])
        if code == 0:
            code = deleteFile(fileID)

        if code != 0:
            console(1, f"\033[31m{current['fileName']} 删除云盘文件失败\033[0m")
            reUpQueue.put(current)
            return

        console(1, f"\033[32m{current['fileName']} 删除云盘文件成功\033[0m")
        updataBothData(current["path"], "delete file")
        # sleep(0.5)
        if current["status"] == "update file":
            current["status"] = "update file+"
        else:
            finishQueue.append(current)
            v.finishQueueChangeFlag = True
            finish["deleteFiles"] += 1

    def preCreateFile():  # 创建文件
        size = current["size"] = getSize(current["path"])
        md5 = getMD5(current["path"], 2 ** 22)  # 2**22 = 4MB
        fileName = os.path.basename(current["path"])

        code, parentFileId = findParentID(current["path"])
        if code == 0:
            current["parentFileId"] = parentFileId
            code, preuploadID, reuse, sliceSize, fileID = createFile(current["parentFileId"], fileName, md5, size)

        if code != 0:
            console(1, f"\033[31m{current['fileName']} 创建文件失败\033[0m")
            reUpQueue.put(current)
            if code == 1:
                console(1, f"\033[31m{current['fileName']} 文件已存在\033[0m")
                preDeleteFile()
            return

        current["reuse"] = reuse
        if reuse:
            updataBothData(current["path"], "create file", current["time"], fileID)
            console(1, f"\033[32m{current['fileName']} 秒传成功\033[0m")
            finishQueue.append(current)
            v.finishQueueChangeFlag = True
            finish["uploadSize"] += current["size"]
            if current["status"] == "create file":
                finish["createFiles"] += 1
            else:
                finish["updateFiles"] += 1
            # sleep(0.5)
        else:
            current["preuploadID"] = preuploadID
            current["sliceSize"] = sliceSize
            current["totalSlice"] = math.ceil(size // sliceSize) + 1
            current["finishSlice"] = 0


            sliceList = []
            for i in range(current["totalSlice"]):
                sliceList.append(i + 1)
            code, parts = getListUploadParts(preuploadID)
            print(parts)

            for part in parts:
                num = int(part["partNumber"])
                etag = part["etag"]
                size = part["size"]
                md5 = getSliceMD5(current["path"], sliceSize, num)
                if etag == md5:
                    console(1, f"\033[34m{current['fileName']} 分片 {num} 跳过\033[0m")
                    sliceList.remove(num)
                    current["finishSlice"] += 1
                    finish["uploadSize"] += size

            for i in range(len(sliceList)):
                slice = current.copy()
                slice["currentSlice"] = sliceList[i]
                slice["sliceMD5"] = getSliceMD5(current["path"], sliceSize, sliceList[i])

                code, slice["URL"] = getUploadUrl(current["preuploadID"], sliceList[i])
                if code != 0:
                    reUpQueue.put(current)
                    if i != 0:
                        sliceQueue.append({"path": current["path"], "clean": True})
                    break

                console(1, f"{slice['fileName']} 分片 {slice['currentSlice']} 发送到分片队列")
                sliceQueue.append(slice)
                sleep(1)

    while not v.upThreadQuitFlag:
        while not reUpQueue.empty():
            v.preThreadIdle = False
            get = reUpQueue.get()
            console(1, f"重新上传队列获取到文件 {get['fileName']}")
            if get["tryTime"] < v.maxTryTime:
                console(1, f"{get['fileName']} 重试次数 {get['tryTime']}")
                upQueue.append(get)
                v.upQueueChangeFlag = True
            else:
                console(1, f"{get['fileName']} 重试次数超过 {v.maxTryTime} 次，加入失败队列")
                failQueue.append(get)
                v.failQueueChangeFlag = True

        if len(upQueue) > 0 and len(sliceQueue) < 1:
            v.preThreadIdle = False

            v.currentHandle = current = upQueue[0]
            upQueue.pop(0)
            v.upQueueChangeFlag = True
            console(1, f"获取到新文件 {current['fileName']} {current['status']} ,剩余{len(upQueue)}个文件")
            current["tryTime"] += 1

            try:
                if current["status"] == "create folder":
                    preCreateFolder()

                if current["status"] == "delete file" or current["status"] == "update file":
                    preDeleteFile()

                if current["status"] == "delete folder":
                    preDeleteFolder()

                if current["status"] == "create file" or current["status"] == "update file+":
                    preCreateFile()
            except Exception as e:
                console(1, f"\033[31m发生错误：{e}\033[0m")
                reUpQueue.put(current)

            v.currentHandle = None


        else:
            v.preThreadIdle = True
            sleep(0.1)


def upThread():
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

    upSteam = v.upSteam
    controlSteam = v.controlSteam
    returnSteam = v.returnSteam
    finish = v.finish

    cleanFile = ""
    while not v.upThreadQuitFlag:
        if len(sliceQueue)>0:
            v.upThreadIdle = False
            v.currentUpLoad = current = sliceQueue[0]
            sliceQueue.pop(0)
            console(2, f"获取到分片 {current['fileName']} 分片 {current['currentSlice']}")

            if "clean" in current:
                cleanFile = current["path"]
            if current["path"] == cleanFile:
                console(2, f"{current['fileName']} 上传失败，已重新加入上传队列 upQueue")
                continue

            cleanFile = ""
            tryTime = 0
            while not v.upThreadQuitFlag:
                tryTime += 1

                upSteam.put(current)
                status=0
                while not v.upThreadQuitFlag:
                    while returnSteam.empty() and not v.upThreadQuitFlag:
                        sleep(0.1)
                    sleep(0.1)
                    status = returnSteam.get()
                    if "totalProgress" in status:
                        current["totalProgress"] = status["totalProgress"]
                        print(status)
                    else:
                        status=status["code"]
                        break

                if status == 200:
                    console(2, f"{current['fileName']} 分片 {current['currentSlice']} 上传完成")

                    if current["currentSlice"] == current["totalSlice"]:
                        finish["uploadSize"] += current["size"]-current["sliceSize"]*(current["totalSlice"]-1)
                        console(2, f"{current['fileName']} 全部分片上传完成，加入校验队列")
                        checkQueue.put(current)
                    else:
                        finish["uploadSize"] += current["sliceSize"]
                    break
                else:
                    console(2, f"{current['fileName']} 分片 {current['currentSlice']} 上传失败")
                    if tryTime >= v.maxTryTime:
                        cleanFile = current["path"]
                        console(2, f"{current['fileName']} 上传失败次数超过 {v.maxTryTime} 次，加入重新上传队列")
                        reUpQueue.put(current)
                        break

            v.currentUpLoad = None

        else:
            v.upThreadIdle = True
            sleep(0.1)


def checkThread():
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

    upSteam = v.upSteam
    controlSteam = v.controlSteam
    returnSteam = v.returnSteam

    finish = v.finish

    while not v.upThreadQuitFlag:
        if not checkQueue.empty():
            v.checkThreadIdle = False
            current = checkQueue.get()
            console(3, f"获取到校验文件 {current['fileName']}")

            code, completed, ifasync, fileID = uploadComplete(current["preuploadID"])
            if completed:
                pass
            elif ifasync:
                while code == 0 and not completed:
                    code, completed, fileID = uploadAsyncResult(current["preuploadID"])
                    sleep(0.5)

            if code == 0:
                updataBothData(current["path"], "create file", current["time"], fileID)
                finishQueue.append(current)
                v.finishQueueChangeFlag = True
                # finish["uploadSize"] += current["size"]
                if current["status"] == "create file":
                    finish["createFiles"] += 1
                else:
                    finish["updateFiles"] += 1
                console(3, f"\033[32m{current['fileName']}上传完成\033[0m")
            else:
                console(3, f"\033[31m{current['fileName']}上传失败\033[0m")
                finish["uploadSize"] -= current["size"]
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
