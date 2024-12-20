import hashlib
import time
from var import v


class DataWithCallback:
    def __init__(self, data,current,returnSteam):
        self.data = data
        self.len = len(data)  # current slice size
        self.currentSize = 0
        self.returnSteam=returnSteam
        self.sliceSize=current["sliceSize"]
        self.currentSlice=current["currentSlice"]
        self.totalSize=current["size"]



    def getMD5(self):
        return hashlib.md5(self.data).hexdigest()

    def read(self, size=-1):
        size = size if size >= 0 else self.len
        chunk = self.data[self.currentSize:min(self.currentSize + size, self.len)]

        self.currentSize = min(self.currentSize + size, self.len)

        self.progressCallback(self.currentSize)
        return chunk

    def progressCallback(self,upsize):
        up=self.sliceSize*(self.currentSlice-1)+upsize
        p=up/self.totalSize*100
        if self.returnSteam.empty():
            self.returnSteam.put({"totalProgress":p})