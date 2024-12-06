import time


def tryRequests(func,**args):
    code=-1
    response=None
    tryTime=0
    while code!=0 and tryTime<3:
        try:
            tryTime+=1
            response=func(**args)

            code=response.json()["code"]
            if code!=0:
                print(args)
                print(response.text)
            if code==429:
                time.sleep(1.2)
        except Exception as e:
            print(func.__name__,args)
            print(e)
    # print(code,tryTime)
    return code,response


def localPathToCloud(localPath,localRoot,cloudRoot):
    return localPath.replace(localRoot,cloudRoot)


splitPath = lambda x: [i for i in x.split("\\") if i != ""]