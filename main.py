from time import sleep,time

from database import loadCloudData, loadLocalData
from task import loadTask, savaTask, checkNoneNextRunTime, checkTask, checkInterruptTask
from taskThread import taskThread
import threading
import multiprocessing

from UI.uiMain import window
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


def init():
    loadCloudData()
    loadLocalData()
    loadTask()
    # createTestTask()


if __name__ == '__main__':
    multiprocessing.freeze_support()

    init()

    checkTask(1)
    startTaskThread()
    checkNoneNextRunTime()
    checkInterruptTask()

    w = window()
    lastTime=0
    while w.isVisible():
        w.runWindow()
        if time()-lastTime>=1:
            lastTime=time()
            checkTask()
            savaTask()

    v.upThreadQuitFlag=True
    v.taskThreadQuitFlag=True
    v.controlSteam.put("quit")
        # sleep(0.1)

    # print(v.total)
    # print(v.finish)

# 线程1 ： 从队列中取出文件，请求创建文件，获取分片上传地址
# 线程3 ： 发送文件分片，等待上传完成，记录成功或失败次数
# 线程4 ： 上传完毕，异步轮询获取上传结果，上传失败后添加队列到线程1
