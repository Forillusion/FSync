import hashlib
import time


class DataWithCallback:
    def __init__(self,data):
        self.data=data
        self.len=len(data)
        self.current=0

    def getMD5(self):
        # L=time.perf_counter()
        md5=hashlib.md5(self.data).hexdigest()
        # print("DataMD5计算用时(ms):",(time.perf_counter()-L)*1000)
        return md5

    def read(self, size=-1):

        size = size if size >= 0 else self.len
        chunk = self.data[self.current:min(self.current+size,self.len)]

        self.current=min(self.current+size,self.len)

        # print("current_size:",size,"\tlen_size:",self.len,"\tprogress:",self.current/self.len*100,"%      ",end="\r")
        p=self.current/self.len*100
        if p-int(p)<0.05 and int(p)%10==0:
            print(int(self.current/self.len*100),end=" ")
        return chunk
