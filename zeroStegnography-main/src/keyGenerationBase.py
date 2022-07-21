import os
import socket
import tqdm

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step
SERVER_PORT = 5001
LOGGING = True

placeHolder = os.path.join(os.curdir, "placeHolder")
# placeHolder = os.path.join(".", "placeHolder")
keyFile = os.path.join(placeHolder, "stegoKey.csv")
coverImage = os.path.join(placeHolder, "coverImg")
keyGenX = ""

receiverHolder = os.path.join(os.curdir, "receiverFiles")
keyFileRecvd = os.path.join(receiverHolder, "stegoKey.csv")
coverImageRecvd = os.path.join(receiverHolder, "coverImg")
secImgGenerated =  os.path.join(receiverHolder, "secImg")


def keygenLog(*arg):
    if LOGGING:
        print(arg)