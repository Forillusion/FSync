import os
from time import sleep

from api.fileList import getAllFileListOld
from database import getCloudListToData, loadCloudData, loadLocalData, updateCloudData, updataLocalData
from findID import findFloaderID, findFileID
from tools import localPathToCloud
from var import v

def rebuildTask(task):
    v.cTask = task
    # 1.  使用getCloudListToData函数获取初始列表数据
    getCloudListToData(v.cloudRoot)
    # 2.  遍历本地文件夹
    for root, dirs, files in os.walk(v.localRoot):
        sleep(1)
        root = root.replace("\\", "/")
        print(root, dirs, files)
    #     # 3.  获取云端文件夹的文件列表
        code, dirID =findFloaderID(root)  # 获取id
        print(dirID)
    #     # 获取id
        code, data = getAllFileListOld(dirID)
        if code == 0:
            for x in data:
                if x["type"] == 0:
                    updateCloudData(localPathToCloud(root+"/"+x["filename"]), "create file", x["fileID"])
                else:
                    updateCloudData(localPathToCloud(root+"/"+x["filename"]), "create folder", x["fileID"])

        for dir in dirs:
            code, dirID = findFloaderID(root+"/"+dir)
            updataLocalData(root+"/"+dir, "create folder", 0)

        for file in files:
            code, fileID = findFileID(root+"/"+file)
            if fileID != -2:
                updataLocalData(root+"/"+file, "create file", int(os.path.getmtime(root+"/"+file)))
            else:
                updataLocalData(root+"/"+file, "create file", 0)

        for file in data:
            if file["filename"] not in files:
                if file["type"] == 0:
                    updataLocalData(root+"/"+file["filename"], "create file", 0)
                else:
                    updataLocalData(root+"/"+file["filename"], "create folder", 0)


    v.cTask = None
    #

# def testTask():
#     task=newTask()
#     task["localPath"]=r"E:/test"
#     task["cloudPath"]=r"/test"
#     return task
#
# if __name__ == '__main__':
#     loadCloudData()
#     loadLocalData()
#     task=testTask()
#     rebuildTask(task)
#
#     saveAllDB()
