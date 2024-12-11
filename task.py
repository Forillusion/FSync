import json
import os

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
        savaTask(v.taskDataPath,{})

    with open(v.taskDataPath, "r", encoding="utf-8") as f:
        return f.read()

def savaTask():
    with open(v.taskDataPath, "w", encoding="utf-8") as f:
        f.write(json.dumps(v.taskList, ensure_ascii=False))

def newTask(path):
    defalutTask={
            "name": "E:",
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
                "type": "",
            },
            "status": "none",
            "lastRunTime": 0,
            "nextRunTime": 0,
            "logs": []
        }
    v.taskList.append(defalutTask)

def deleteTask(subTask):
    v.taskList.remove(subTask)
