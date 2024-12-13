# 1，请求【创建文件】接口创建文件，接口返回的reuse为true时，表示秒传成功，上传结束。非秒传的情况将会返回预上传ID preuploadID 与分片大小 sliceSize,请将文件根据分片大小切分。
# 2，非秒传时，携带步骤1返回的preuploadID 与分片序号sliceNo，请求【获取上传地址接口】获取上传地址。
# 3，用PUT请求步骤2中返回的地址，上传文件分片。
# 4，(推荐操作)文件分片上传完成后,调用【列举已上传分片】接口，在本地进行与云端的分片md5比对。注:如果您的文件小于 sliceSize ,该操作将会返回空值,可以不进行这步操作。
# 5，校验完成后，请求【上传完毕】接口，完成上传。
# 6，根据步骤5返回的结果，判断是否需要调用【异步轮询获取上传结果】接口，获取上传的最终结果。该时间需要等待，123云盘服务器会校验用户预上传时的MD5与实际上传成功的MD5是否一致。
import json
import queue
from time import sleep, time

from compare import compareData, generateQueue
from scanLocalPath import scanLocalPath
from database import loadDB, saveDB, loadCloudData, loadLocalData, getCloudListToData
from task import setNextRunTime, checkTaskRunTime, loadTask, checkStartSecheduled, savaTask
from upProcess import upProcess
import upThreads as up
import threading
import multiprocessing
from var import v


# 1.读取文件
# 2.获取文件大小
# 3.获取文件MD5
# 4.请求创建文件
# 5.获取分片上传地址

# 6.上传文件分片
# 7.校验文件分片

# 8.分片指针移动
# 9.上传完毕
# 10.异步轮询获取上传结果

# token= Token.getToken

def startUp():
    thread1 = threading.Thread(target=up.preThread)
    thread1.start()
    thread2 = threading.Thread(target=up.upThread)
    thread2.start()
    thread3 = threading.Thread(target=up.checkThread)
    thread3.start()

    p = multiprocessing.Process(target=upProcess, args=(v.upSteam, v.controlSteam, v.returnSteam,),
                                name='UI_Process')
    p.start()
    while not v.quitFlag:
        # print(v.preThreadIdle, v.upThreadIdle, v.checkThreadIdle, v.quitFlag)
        if (len(v.upQueue) == 0 and v.reUpQueue.empty() and v.sliceQueue.empty()
                and v.checkQueue.empty() and v.preThreadIdle and v.upThreadIdle and v.checkThreadIdle):
            v.quitFlag = True
            v.controlSteam.put("quit")

            thread1.join()
            thread2.join()
            thread3.join()
        sleep(1)


def createTestTask():
    v.taskList.append({
        "name": "E:",
        "localPath": r"E:\test",
        "cloudPath": r"\test",
        "deleteCloudFile": True,
        "realTimeStatus": {
            "total": {
                "createFolder": 0,
                "deleteFolder": 0,
                "createFiles": 0,
                "updateFiles": 0,
                "deleteFiles": 0,
                "uploadSize": 0,
            },
            "finish": {
                "createFolder": 0,
                "deleteFolder": 0,
                "createFiles": 0,
                "updateFiles": 0,
                "deleteFiles": 0,
                "uploadSize": 0,
            }
        },
        "currentStartTime": 0,
        "runCount": 0,
        "realTimeLogs": [],  # todo
        "scheduled": {  # todo
            # "type": "none| start|time|interval",  # todo
            "type": "time",
            "time": "12:00:00",
            "week": [1, 2, 3, 4, 5, 6, 7],
            "missed": True

        },
        # "status": "none|waiting|running|finished|failed",
        "status": "none",
        "lastRunTime": 0,
        "nextRunTime": 0,  # todo
        "logs": []
    })
    v.cTask = v.taskList[0]


def beforeRunTask():
    v.cTask["currentStartTime"] = int(time())
    v.cTask["runCount"] += 1
    v.cTask["status"] = "running"
    v.total = {
        "createFolder": 0,
        "deleteFolder": 0,
        "createFiles": 0,
        "updateFiles": 0,
        "deleteFiles": 0,
        "uploadSize": 0,
    }
    v.finish = {
        "createFolder": 0,
        "deleteFolder": 0,
        "createFiles": 0,
        "updateFiles": 0,
        "deleteFiles": 0,
        "uploadSize": 0,
    }
    v.cTask["lastRunTime"] = int(time())
    # todo: v.cTask["nextRunTime"]


def afterRunTask():
    fail = {
        "createFolder": v.total["createFolder"] - v.finish["createFolder"],
        "deleteFolder": v.total["deleteFolder"] - v.finish["deleteFolder"],
        "createFiles": v.total["createFiles"] - v.finish["createFiles"],
        "updateFiles": v.total["updateFiles"] - v.finish["updateFiles"],
        "deleteFiles": v.total["deleteFiles"] - v.finish["deleteFiles"],
        "uploadSize": v.total["uploadSize"] - v.finish["uploadSize"],
    }

    if (fail["createFolder"] + fail["deleteFolder"] + fail["createFiles"] + fail["updateFiles"] + fail[
        "deleteFiles"]) > 0:
        v.cTask["status"] = "failed"
    else:
        v.cTask["status"] = "finished"

    log = {
        "startTime": v.cTask["currentStartTime"],
        "realTimeStatus": {
            "total": v.total,
            "finish": v.finish,
            "fail": fail,
        },
        "status": v.cTask["status"],
    }

    v.cTask["logs"].append(log)


def startTask(task):
    v.cTask = task
    beforeRunTask()
    setNextRunTime(v.cTask)
    getCloudListToData(v.cloudRoot)

    v.scanData = scanLocalPath(v.localRoot)

    print("云盘数据库：", json.dumps(v.cloudData))
    print("本地数据库：", json.dumps(v.localData))
    print("扫描数据库：", json.dumps(v.scanData))

    A, B, C = compareData(v.localData, v.scanData, v.localRoot)
    v.upQueue = generateQueue(A, B, C)
    v.upQueue.reverse()

    print("需要创建的文件:")
    print(A)
    print("需要更新的文件:")
    print(B)
    print("需要删除的文件:")
    print(C)
    print("任务队列:")

    for x in v.upQueue:
        print(json.dumps(x))

    startUp()
    afterRunTask()
    print(v.cTask["name"], "任务结束")
    v.cTask = None


def taskThread():
    while True:
        for x in v.taskList:
            if x["status"] == "waiting":
                startTask(x)
        sleep(5)


def checkTask(start=0):
    if start == 1:
        for x in v.taskList:
            if checkStartSecheduled(x):
                x["status"] = "waiting"
    else:
        for x in v.taskList:
            print(x["name"], checkTaskRunTime(x))
            if checkTaskRunTime(x):
                x["status"] = "waiting"


def startTaskThread():
    thread1 = threading.Thread(target=taskThread)
    thread1.start()


def checkNoneNextRunTime():
    for x in v.taskList:
        if x["nextRunTime"] == 0:
            setNextRunTime(x)


def init():
    loadCloudData()
    loadLocalData()
    loadTask()
    # createTestTask()


if __name__ == '__main__':
    multiprocessing.freeze_support()

    init()
    checkNoneNextRunTime()
    checkTask(1)
    startTaskThread()
    while True:
        checkTask()
        savaTask()
        sleep(5)
    # taskThread()
    # startTask()

    # print(v.total)
    # print(v.finish)

# 线程1 ： 从队列中取出文件，请求创建文件，获取分片上传地址
# 线程3 ： 发送文件分片，等待上传完成，记录成功或失败次数
# 线程4 ： 上传完毕，异步轮询获取上传结果，上传失败后添加队列到线程1
