import atexit
import os
import sys
from time import sleep,time

from database import loadCloudData, loadLocalData, saveDB, saveCloudData, saveLocalData
from task import loadTask, savaTask, checkNoneNextRunTime, checkTask, checkInterruptTask
from taskThread import taskThread
import threading
import multiprocessing

from UI.uiMain import startUIThread
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


def startTaskThread():
    taskTh = threading.Thread(target=taskThread)
    taskTh.start()
    return taskTh

def getAdmin():
    # windows下获取管理员权限
    if os.name == 'nt':
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            return False

def init():
    loadCloudData()
    loadLocalData()
    loadTask()
    # createTestTask()


def saveBothDB():
    savaTask()
    saveLocalData()
    saveCloudData()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    os.system("")
    # getAdmin()
    init()

    checkTask(1)
    atexit.register(saveBothDB)
    taskTh=startTaskThread()
    checkNoneNextRunTime()
    checkInterruptTask()
    startUIThread()
    # lastTime=0

    while not v.mainQuitFlag:
        # if time()-lastTime>=1:
        #     lastTime=time()
        checkTask()
        sleep(1)

    print("主循环退出")
    v.upThreadQuitFlag=True
    v.taskThreadQuitFlag=True
    v.controlSteam.put("quit")
    print("等待线程退出")

    taskTh.join()
    print("线程退出")
    saveBothDB()
    print("保存数据")

        # sleep(0.1)

    # print(v.total)
    # print(v.finish)

# 线程1 ： 从队列中取出文件，请求创建文件，获取分片上传地址
# 线程3 ： 发送文件分片，等待上传完成，记录成功或失败次数
# 线程4 ： 上传完毕，异步轮询获取上传结果，上传失败后添加队列到线程1
