import json
import multiprocessing
import threading
import time

import upThreads as up
from compare import compareData, generateQueue
from database import getCloudListToData
from scanLocalPath import scanLocalPath
from task import setNextRunTime, savaTask
from upProcess import upProcess
from var import v


def startUp():
    v.preThreadIdle = False
    v.upThreadIdle = False
    v.checkThreadIdle = False
    v.upThreadQuitFlag = False

    # preThread = threading.Thread(target=up.preThread, args=(v.preThreadIdle,v.currentHandle,))
    # preThread.start()
    # upThread = threading.Thread(target=up.upThread, args=(v.upThreadIdle,v.currentUpLoad,))
    # upThread.start()
    # checkThread = threading.Thread(target=up.checkThread, args=(v.checkThreadIdle,))
    # checkThread.start()

    # preThread2 = threading.Thread(target=up.preThread, args=(v.preThreadIdle2,v.currentHandle2,))
    # preThread2.start()
    # upThread2 = threading.Thread(target=up.upThread, args=(v.upThreadIdle2,v.currentUpLoad2,))
    # upThread2.start()
    # checkThread2 = threading.Thread(target=up.checkThread, args=(v.checkThreadIdle2,))
    # checkThread2.start()

    preThread = threading.Thread(target=up.preThread)
    preThread.start()
    upThread = threading.Thread(target=up.upThread)
    upThread.start()
    checkThread = threading.Thread(target=up.checkThread)
    checkThread.start()

    # preThread2 = threading.Thread(target=up.preThread)
    # preThread2.start()
    # upThread2 = threading.Thread(target=up.upThread)
    # upThread2.start()
    # checkThread2 = threading.Thread(target=up.checkThread)
    # checkThread2.start()

    p = multiprocessing.Process(target=upProcess, args=(v.upSteam, v.controlSteam, v.returnSteam,),
                                name='UI_Process')
    p.start()
    mainThread = threading.main_thread()
    while not v.upThreadQuitFlag and mainThread.is_alive() and preThread.is_alive() and upThread.is_alive() and checkThread.is_alive():

        if (len(v.upQueue) == 0 and v.reUpQueue.empty() and len(v.sliceQueue) == 0
                and v.checkQueue.empty() and v.preThreadIdle and v.upThreadIdle and v.checkThreadIdle):
            # if (len(v.upQueue) == 0 and v.reUpQueue.empty() and len(v.sliceQueue) == 0
            #         and v.checkQueue.empty() and v.preThreadIdle and v.upThreadIdle and v.checkThreadIdle
            #         and v.preThreadIdle2 and v.upThreadIdle2 and v.checkThreadIdle2):

            v.upThreadQuitFlag = True
            v.controlSteam.put("quit")

        time.sleep(1)

    preThread.join()
    upThread.join()
    checkThread.join()


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
    v.cTask["currentStartTime"] = int(time.time())
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
    v.cTask["lastRunTime"] = int(time.time())
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

    # print("云盘数据库：", json.dumps(v.cloudData))
    # print("本地数据库：", json.dumps(v.localData))
    # print("扫描数据库：", json.dumps(v.scanData))

    # with open("list.json","w") as f:
    #     f.write(json.dumps(v.scanData))

    A, B, C = compareData(v.localData, v.scanData, v.localRoot)
    v.upQueue = generateQueue(A, B, C)
    v.upQueue.reverse()

    print("需要创建的文件:")
    print(A)
    print("需要更新的文件:")
    print(B)
    print("需要删除的文件:")
    print(C)

    # print("任务队列:")
    # for i in range(min(len(v.upQueue),v.maxListCount)):
    #     print(json.dumps(v.upQueue[i]))

    startUp()

    afterRunTask()
    savaTask()
    v.upQueueChangeFlag = True
    v.finishQueueChangeFlag = True
    v.failQueueChangeFlag = True
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), v.cTask["name"], "任务结束")
    v.cTask = None


def taskThread():
    mainThread = threading.main_thread()
    while not v.taskThreadQuitFlag and mainThread.is_alive():
        time.sleep(1)
        for x in v.taskList:
            if x["status"] == "waiting" or x["status"] == "interrupt":
                startTask(x)
