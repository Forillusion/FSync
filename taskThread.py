import json
import multiprocessing
import threading
from time import sleep, time

import upThreads as up
from compare import compareData, generateQueue
from database import getCloudListToData
from scanLocalPath import scanLocalPath
from task import setNextRunTime
from upProcess import upProcess
from var import v


def startUp():
    preThread = threading.Thread(target=up.preThread)
    preThread.start()
    upThread = threading.Thread(target=up.upThread)
    upThread.start()
    checkThread = threading.Thread(target=up.checkThread)
    checkThread.start()

    p = multiprocessing.Process(target=upProcess, args=(v.upSteam, v.controlSteam, v.returnSteam,),
                                name='UI_Process')
    p.start()
    while not v.upThreadQuitFlag:
        # print(v.preThreadIdle, v.upThreadIdle, v.checkThreadIdle, v.upThreadQuitFlag)
        if (len(v.upQueue) == 0 and v.reUpQueue.empty() and v.sliceQueue.empty()
                and v.checkQueue.empty() and v.preThreadIdle and v.upThreadIdle and v.checkThreadIdle):
            v.upThreadQuitFlag = True
            v.controlSteam.put("quit")

            preThread.join()
            upThread.join()
            checkThread.join()
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
    while not v.taskThreadQuitFlag:
        for x in v.taskList:
            if x["status"] == "waiting":
                startTask(x)
        sleep(1)
