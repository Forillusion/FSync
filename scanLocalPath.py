import os


def scanLocalPath(localRoot):
    # 传入需要扫描的本地根目录文件夹路径，返回扫描结果
    folders=localRoot.split("\\")
    folders=[x for x in folders if x!=""]
    data={}
    current=data
    for folder in folders:
        current[folder]={}
        current=current[folder]
    current.update(recursionLocalPath(localRoot))
    return data


def recursionLocalPath(path):
    data={}
    if os.path.isdir(path):
        for i in os.listdir(path):
            if i != "$RECYCLE.BIN":
                try:
                    x = recursionLocalPath(os.path.join(path, i))
                    data[i] = x
                except:
                    pass
    else:
        data[":time"] = int(os.path.getmtime(path))

    return data
