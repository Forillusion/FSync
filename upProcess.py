from time import sleep

from api.upload import uploadFileSlice


def upProcess(upSteam, controlSteam, returnSteam):
    quitFlag = False
    current = None
    while not quitFlag:
        while not controlSteam.empty():
            msg = controlSteam.get()
            if msg == "quit":
                quitFlag = True
                break

        while not upSteam.empty():
            current = upSteam.get()
            status = uploadFileSlice(current["URL"], current["path"], current["sliceSize"], current["currentSlice"])
            returnSteam.put(status)

        sleep(0.1)
