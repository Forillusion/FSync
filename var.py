import multiprocessing
import queue


class SingletonMeta(type):  # 定义一个元类 SingletonMeta，它继承自 type
    def __call__(cls, *args, **kwargs):  # 重写 __call__ 方法，这是当实例被创建时调用的方法
        if not hasattr(cls, '_instance'):  # 如果类属性 `_instance` 不存在，则创建一个新的实例
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance  # 返回已有的实例


class Singleton(metaclass=SingletonMeta):  # 使用 SingletonMeta 作为元类来定义一个类
    localRoot = r"E:\test"
    cloudRoot = r"\test"
    cloudData = {}
    localData = {}
    upQueue = []

    reUpQueue = queue.Queue()
    checkQueue = queue.Queue()
    failQueue = []
    finishQueue = []
    sliceQueue = queue.Queue()

    maxTryTime = 3
    preThreadIdle = False
    upThreadIdle = False
    checkThreadIdle = False
    quitFlag = False

    upSteam = multiprocessing.Queue()
    controlSteam = multiprocessing.Queue()
    returnSteam = multiprocessing.Queue()

    idKey = ":id"
    timeKey = ":mt"

    def __init__(self):
        pass


v = Singleton()
