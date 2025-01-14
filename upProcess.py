from time import sleep

from api.upload import uploadFileSlice


def upProcess(upSteam, controlSteam, returnSteam):
    upProcessQuitFlag = False
    current = None
    while not upProcessQuitFlag:
        while not controlSteam.empty():
            msg = controlSteam.get()
            if msg == "quit":
                upProcessQuitFlag = True
                break

        while not upSteam.empty():
            current = upSteam.get()
            # status = uploadFileSlice(current["URL"], current["path"], current["sliceSize"], current["currentSlice"],returnSteam)
            status = uploadFileSlice(current, returnSteam)
            returnSteam.put({"code": status})

        sleep(0.1)