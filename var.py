import multiprocessing
import queue


class VarMeta(type):  # 定义一个元类 SingletonMeta，它继承自 type
    def __call__(cls, *args, **kwargs):  # 重写 __call__ 方法，这是当实例被创建时调用的方法
        if not hasattr(cls, '_instance'):  # 如果类属性 `_instance` 不存在，则创建一个新的实例
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance  # 返回已有的实例


class Var(metaclass=VarMeta):  # 使用 SingletonMeta 作为元类来定义一个类
    # localRoot = r"E:\test"
    # cloudRoot = r"\test"
    cloudDataPath=r"db\cloudData.json"
    localDataPath=r"db\localData.json"
    taskDataPath=r"db\taskData.json"
    cloudData = {}
    localData = {}
    upQueue = []

    reUpQueue = queue.Queue()
    checkQueue = queue.Queue()
    failQueue = []
    finishQueue = []
    # sliceQueue = queue.Queue()
    sliceQueue=[]

    currentHandle = None
    currentUpLoad = None

    maxTryTime = 3
    preThreadIdle = False
    upThreadIdle = False
    checkThreadIdle = False
    upThreadQuitFlag = False
    mainQuitFlag = False

    upSteam = multiprocessing.Queue()
    controlSteam = multiprocessing.Queue()
    returnSteam = multiprocessing.Queue()

    idKey = ":id"
    timeKey = ":mt"

    taskThreadQuitFlag = False

    taskList = []
    cTask=None # current task

    def __init__(self):
        pass

    @property
    def localRoot(self):
        return self.cTask["localPath"]

    @property
    def cloudRoot(self):
        return self.cTask["cloudPath"]

    @property
    def total(self):
        return self.cTask["realTimeStatus"]["total"]

    @total.setter
    def total(self, value):
        self.cTask["realTimeStatus"]["total"]=value

    @property
    def finish(self):
        return self.cTask["realTimeStatus"]["finish"]

    @finish.setter
    def finish(self, value):
        self.cTask["realTimeStatus"]["finish"]=value


# task = {
#     "name": "E:",
#     "localPath": "E:\\test",
#     "cloudPath": "\\test",
#     "deleteCloudFile": True,
#     "realTimeStatus": {
#         "total": {
#             "createFolder": 0,
#             "deleteFolder": 0,
#             "createFiles": 0,
#             "updateFiles": 0,
#             "deleteFiles": 0,
#             "uploadSize": 0,
#         },
#         "finish": {
#             "createFolder": 0,
#             "deleteFolder": 0,
#             "createFiles": 0,
#             "updateFiles": 0,
#             "deleteFiles": 0,
#             "uploadSize": 0,
#         }
#     },
#     "currentStartTime": 0
#     "runCount": 0,
#     "realTimeLogs": [],
#     "scheduled": {
#       "type":"none|start|time|interval",
#         ...
#     },
#     "status": "none|waiting|running|finished|failed",
#     "lastRunTime": 0,
#     "nextRunTime": 0,
#     "logs": []
# }

v = Var()
