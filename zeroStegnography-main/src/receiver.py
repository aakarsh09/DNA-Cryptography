#!/usr/bin/python

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import ttk
import os
import shutil
from keyGenerationBase import *
import threading
from time import sleep

t = 10
zeros = 0
cimg = None


def pixelToBin(i):
    rBin = bin(i[0]).split('b')[1].zfill(8)
    gBin = bin(i[1]).split('b')[1].zfill(8)
    bBin = bin(i[2]).split('b')[1].zfill(8)
    return rBin + gBin + bBin

def rightShift(numInStr, n):
  shiftBy = n % 24
  firstPart = numInStr[-1*shiftBy:]
  secondPart = numInStr[0:-1*shiftBy]
  # keygenLog(firstPart + " " + secondPart)
  # keygenLog(firstPart+secondPart)
  return firstPart + secondPart

def leftShift(numInStr, n):
  shiftBy = n % 24
  firstPart = numInStr[n:]
  secondPart = numInStr[0:n]
  # keygenLog(firstPart + " " + secondPart)
  # keygenLog(firstPart+secondPart)
  return firstPart + secondPart

# Fake Secret Image Generation
# Input: Secret image (I) and system time measure in
#        seconds (t) recorded at the start of key generation.
# Output: Fake secret image (I’)
# Steps:
#     1. Convert each pixel(RGB) of I into its binary format.
#     2. Flip all bits of I.
#     3. Count the number of zeroes (z). If count is even,
#        circular shift-left by 2*t bits. If the count of zeros is odd,
#        circular shift-right by 4*t bits.
def generateFakeSecreteImg(i):
    
        global zeros
        
        #Convert each pixel(RGB) of I into its binary format.
        binFormat = pixelToBin(i)
        
        #Flip all bits of I
        flippedValue = ''.join('1' if x == '0' else '0' for x in binFormat)
        
        # Count the number of zeroes (z). If count is even,
        # circular shift-left by 2*t bits. If the count of zeros is odd,
        # circular shift-right by 4*t bits.
        zeros = flippedValue.count('0')
        
        if (zeros%2) == 0:
            #If even circular shift by 2*t bits
            n = t * 2
            shiftedValue = leftShift(flippedValue, n)
        else:
            n = t*4
            shiftedValue = rightShift(flippedValue, n)
        # keygenLog(binFormat, flippedValue, shiftedValue)
        return shiftedValue
        
# Input:    Fake secret image (I’) and cover image (C)
# Output:   Stego-key (K)
# Steps:
#        1. Convert each pixel(RGB) of C into its binary
#           format.
#        2. Transform the binary format of the fake secret image
#           (I’) and cover image (C) into its DNA format using the
#           substitution rule.
#        3. Perform XOR operation to the DNA formats of I’
#           and C using the XOR Truth Table as shown in Table II.
#           Append four DNA alphabets at the end of the
#           sequence. Append ‘A’ to the end of the DNA sequence if z,
#           count of zeros in the fake secret image is even; otherwise,
#           append ‘C’. The last three DNA alphabets shall be the DNA
#           equivalent of the six-bit representation of t.
def stegoKeyGeneration(ci, si):
    global zeros
    
    # Convert each pixel(RGB) of C into its binary format.
    ci = pixelToBin(ci)
    
    # Transform the binary format of the fake secret image
    # (I’) and cover image (C) into its DNA format using the
    # substitution rule.
    
    dnaSubRuleDict = {
        "00":"A",
        "01":"C",
        "10":"G",
        "11": "T"}
    i = 0
    coverDnaStr = ""
    secDnaStr = ""
    while i<len(ci):
        coverDnaStr += dnaSubRuleDict[ci[i] + ci[i+1]]
        secDnaStr += dnaSubRuleDict[si[i] + si[i+1]]
        i += 2
    
#           Perform XOR operation to the DNA formats of I’
#           and C using the XOR Truth Table as shown in Table II.
#           Append four DNA alphabets at the end of the
#           sequence. Append ‘A’ to the end of the DNA sequence if z,
#           count of zeros in the fake secret image is even; otherwise,
#           append ‘C’. The last three DNA alphabets shall be the DNA
#           equivalent of the six-bit representation of t.

    xorDict = {
        "AA": "A",
        "AC": "C",
        "AG": "G",
        "AT": "T",
        "CA": "C",
        "CC": "A",
        "CG": "T",
        "CT": "G",
        "GA": "G",
        "GC": "T",
        "GG": "A",
        "GT": "C",
        "TA": "T",
        "TC": "G",
        "TG": "C",
        "TT": "A"}
    xor = ""
    for i in range(0,len(secDnaStr)):
        xor = xor + xorDict[secDnaStr[i] + coverDnaStr[i]]
    
    appendStr = ""
    if zeros%2 == 0:
        appendStr = appendStr + 'A'
    else:
        appendStr = appendStr + 'C'

    t_bin = bin(t).split('b')[1].zfill(6)
    k = 0
    newStr = ""
    while k<len(t_bin):
        str = t_bin[k] + t_bin[k+1]
        newStr = newStr + dnaSubRuleDict[str]
        k = k+2
    appendStr = appendStr + newStr
    
    stegoKey = xor + appendStr
    
    # keygenLog(ci,coverDnaStr,si,secDnaStr, xor, zeros, appendStr, stegoKey)
    
    return stegoKey
                    
    

def generateSecImg():    
    with open(".temp", "r") as file:
        fileName = file.read()
    keygenLog(fileName)
    sleep(5)
    # opens the image
    img = Image.open(secImgGenerated)
     
    # resize the image and apply a high-quality down sampling filter
    img = img.resize((250, 250), Image.ANTIALIAS)
 
    # PhotoImage class is used to add image to widgets, icons etc
    pImg = ImageTk.PhotoImage(img)
  
    secImgPanel.configure(image = pImg)
    secImgPanel.img = pImg

def open_img(frame, imgPanel, imgType):
# def open_img():   
    global secImg
    global coverImg
    
    # Select the Imagename  from a folder
    x = filename = filedialog.askopenfilename(title ='Select an image')
    keygenLog("x:",x)
    
    if x == "":
        messagebox.showwarning(title = "File error", message = "No file selected")
        return x
 
    # opens the image
    img = Image.open(x)
     
    # resize the image and apply a high-quality down sampling filter
    img = img.resize((250, 250), Image.ANTIALIAS)
 
    # PhotoImage class is used to add image to widgets, icons etc
    pImg = ImageTk.PhotoImage(img)
    secImgPanel.configure(image = pImg)
    secImgPanel.img = pImg
    
    if imgType == "sec":
        secImg = img
    else:
        coverImg = img
        shutil.copy(x,coverImage)
        
def startReceiver():
    # device's IP address
    SERVER_HOST = "0.0.0.0"
    # receive 4096 bytes each time
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    fileCounter = 0
    
    # create the server socket
    # TCP socket
    s = socket.socket()
    
    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))
    
    recIp = socket.gethostbyname(socket.gethostname())
    
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    s.listen(5)
    
    while True:
        keygenLog(f"[*] Listening as {recIp}:{SERVER_PORT}")

        # accept connection if there is any
        client_socket, address = s.accept() 
        # if below code is executed, that means the sender is connected
        keygenLog(f"[+] {address} is connected.")

        # receive the file infos
        # receive using client socket, not server socket
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        keygenLog("Receiving - File Name:", filename, "File Size:", filesize)

        # remove absolute path if there is
        filename = os.path.basename(filename)
        filename = os.path.join(receiverHolder, filename)
        
        
        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            i = 1
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                keygenLog(str(i) + ". Received bytes")
                i += 1
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
            fileCounter += 1
        if fileCounter == 3:
            fileCounter = 0
            
            #We have received both files display it on the window
            # opens the image
            print(coverImageRecvd)
            Cimg = Image.open(coverImageRecvd)

            # resize the image and apply a high-quality down sampling filter
            Cimg = Cimg.resize((250, 250), Image.ANTIALIAS)

            # PhotoImage class is used to add image to widgets, icons etc
            pImg = ImageTk.PhotoImage(Cimg)
            coverImgPanel.configure(image = pImg)
            coverImgPanel.img = pImg

    # close the client socket
    client_socket.close()
    # close the server socket
    s.close()


def verify():
    user_pass = l_pass.get()
    user_id = lid.get()
    if user_id == "" and user_pass == "":
        login_by = "Admin"
        login_allow()
        
        #Start a thread for receiver
        receiverThread = threading.Thread(target=startReceiver, args=())
        receiverThread.setDaemon(True)
        receiverThread.start()
        
    else:
        messagebox.showinfo("", "wrong input")


def login_allow():
    l_login.pack_forget()   
    recIp = socket.gethostbyname(socket.gethostname())
    coverLbl.configure(text = "Receiving at IP: " + recIp + ", Port: " + str(SERVER_PORT))
    rootFrame.pack()

#Main program
if os.path.exists(receiverHolder):
    shutil.rmtree(receiverHolder)
os.makedirs(receiverHolder)
    
#Create app using with separating widget   
root=Tk()  
#App Title  
root.title("Key Generation - Zero Steganography - Receiver")
# root.geometry("750x550")
ttk.Label(root, text="Key Generation for Zero Steganography Using DNA Sequences").pack()  

# login page
l_login = Label(bg="silver")
f_login = Frame(l_login, pady="25", padx="25")
lb0 = Label(f_login, text="Enter Details", bg="orange", fg="blue", font="lucida 10 bold", width="35",
            pady="4").grid(
    columnspan=3, row=0, pady="15")
lb1 = Label(f_login, text="Enter ID: ", font="lucida 10 bold").grid(column=0, row=2, pady="4")
lid = StringVar()
e1 = Entry(f_login, textvariable=lid, width="28").grid(column=1, row=2)
lb2 = Label(f_login, text="Enter Password: ", font="lucida 10 bold").grid(column=0, row=3, pady="4")
l_pass = StringVar()
e2 = Entry(f_login, textvariable=l_pass, width="28", show = "*").grid(column=1, row=3)
btn = Button(f_login, text="login", bg="green", fg="white", width="10", font="lucida 10 bold", command=verify)
btn.grid(columnspan=3, row=5, pady="10")
f_login.pack(pady=140)
l_login.pack()

rootFrame = ttk.Frame(root) 

mf = ttk.Frame(rootFrame)
mf.pack()

#Create Frams  
fram1=ttk.Frame(mf,relief=RAISED)  
fram2=ttk.Frame(mf,relief=RAISED)  
# fram1.pack(side=LEFT) 
# fram2.pack(side=LEFT)
fram1.grid(row = 0, column = 0, padx = 100)
fram2.grid(row = 0, column = 1, padx = 100)

coverLbl = Label(fram1, text = "Waiting to receive...")
coverLbl.pack(pady=40, padx = 40)



coverImgPanel = Label(fram1)
coverImgPanel.pack()

secLbl = Label(fram2, text = "Generated secrete Image:")
secLbl.pack(pady=40, padx = 40)

secImgPanel = Label(fram2)
secImgPanel.pack()

buttnGenerateSecImg = Button(rootFrame, 
                 text ='Generate Secrete Image',
                         command=generateSecImg)
buttnGenerateSecImg.pack()

#Calling Main()  
root.mainloop()  