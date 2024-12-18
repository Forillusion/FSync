import json
import os
import time

from tools import splitPath
from var import v


def loadTask():
    # 如果文件夹不存在，创建文件夹
    folders = splitPath(v.taskDataPath)
    current = ""
    for folder in folders[:-1]:
        current += folder + "\\"
        if not os.path.exists(current):
            os.mkdir(current)

    if not os.path.exists(v.taskDataPath):
        savaTask()

    with open(v.taskDataPath, "r", encoding="utf-8") as f:
        x = f.read()
        if x == "":
            v.taskList = []
        else:
            v.taskList = json.loads(x)


def savaTask():
    with open(v.taskDataPath, "w", encoding="utf-8") as f:
        f.write(json.dumps(v.taskList, ensure_ascii=False))


def newTask():
    defalutTask = {
        "name": "",
        "enabled": True,
        "localPath": r"",
        "cloudPath": r"",
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
        "realTimeLogs": [],
        "scheduled": {
            "type": "none",
        },
        "status": "none",
        "lastRunTime": 0,
        "nextRunTime": 0,
        "logs": []
    }
    # v.taskList.append(defalutTask)
    return defalutTask

def addTask(task):
    v.taskList.append(task)

def updateTask(task):
    setNextRunTime(task)

def deleteTask(task):
    v.taskList.remove(task)


def checkTaskScheduled(task, start=0):
    # if task["scheduled"]["type"]=="none":
    #     return False
    # if task["scheduled"]["type"]=="start":
    #     return start==1
    # if task["scheduled"]["type"]=="time":
    #     week=time.localtime().tm_wday+1
    #     t=time.strftime("%H:%M:%S",time.localtime())
    #     if t==task["scheduled"]["setTime"] and week in task["scheduled"]["week"]:
    #         return True
    pass


def checkStartSecheduled(task):
    if task["scheduled"]["type"] == "start":
        return True

    # "none|waiting|running|finished|failed",


def checkTaskRunTime(task):
    t = time.time()
    if task["status"] == "waiting" or task["status"] == "running":
        return False
    if task["scheduled"]["type"] == "time" or task["scheduled"]["type"] == "interval":
        if t - task["nextRunTime"] > 0:
            if task["scheduled"]["missed"]:
                return True
            elif t - task["nextRunTime"] < 10:
                return True
    return False


def setNextRunTime(task):
    if task["scheduled"]["type"] == "time":
        nowWeek = time.localtime().tm_wday + 1
        nowTime = time.strftime("%H:%M:%S", time.localtime())
        setTime = task["scheduled"]["time"]
        nextTime = 0

        n = time.localtime()
        n = time.strptime(f"{n.tm_year} {n.tm_yday}", "%Y %j")
        n = time.mktime(n)
        s = setTime.split(":")
        n += int(s[0]) * 3600 + int(s[1]) * 60 + int(s[2])

        for x in task["scheduled"]["week"]:
            if x == nowWeek:
                if nowTime < setTime:
                    nextTime = n
                    break
            if x > nowWeek:
                nextTime = n + (x - nowWeek) * 24 * 3600
                break
        if nextTime == 0:
            nextTime = n + (task["scheduled"]["week"][0] + 7 - nowWeek) * 24 * 3600
        task["nextRunTime"] = int(nextTime)

    if task["scheduled"]["type"] == "interval":
        task["nextRunTime"] = int(time.time() + task["scheduled"]["interval"])


# "none":
# "start": 当程序启动时运行
# "time":  在指定时间运行
#      "time": "12:00:00"  具体时间
#      "week": [1,2,3,4,5,6,7]  重复星期
#      "missed": True  是否补充未运行的任务
# "interval":  间隔运行
#      "interval": 3600  间隔时间
#      "missed": True  是否补充未运行的任务

def checkNoneNextRunTime():
    for x in v.taskList:
        if x["nextRunTime"] == 0:
            setNextRunTime(x)


def checkTask(start=0):
    if start == 1:
        for x in v.taskList:
            if x["enabled"]:
                if checkStartSecheduled(x):
                    x["status"] = "waiting"
    else:
        for x in v.taskList:
            if x["enabled"]:
                print(x["name"], checkTaskRunTime(x))
                if checkTaskRunTime(x):
                    x["status"] = "waiting"

def checkInterruptTask():
    for x in v.taskList:
        if x["status"] == "running":
            x["status"] = "interrupt"
            # x["logs"].append("任务被中断")
            # x["nextRunTime"] = int(time.time() + 60)