#!/usr/bin/python

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import ttk
import os
import shutil
from keyGenerationBase import *

secImg = None
coverImg = None
t = 10
zeros = 0

def sendFilesOverNetwork():
    # the ip address or hostname of the server, the receiver
    host = txtIpAddress.get()
    # the port, let's use 5001
    port = 5001
    
    coverImgFileSize = os.path.getsize(coverImage)
    keyFileSize = os.path.getsize(keyFile)
    
    
    


def pixelToBin(i):
    rBin = bin(i[0]).split('b')[1].zfill(8)
    gBin = bin(i[1]).split('b')[1].zfill(8)
    bBin = bin(i[2]).split('b')[1].zfill(8)
    return rBin + gBin + bBin

def rightShift(numInStr, n):
  shiftBy = n % 24
  firstPart = numInStr[-1*shiftBy:]
  secondPart = numInStr[0:-1*shiftBy]
  # print(firstPart + " " + secondPart)
  # print(firstPart+secondPart)
  return firstPart + secondPart

def leftShift(numInStr, n):
  shiftBy = n % 24
  firstPart = numInStr[n:]
  secondPart = numInStr[0:n]
  # print(firstPart + " " + secondPart)
  # print(firstPart+secondPart)
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
        # print(binFormat, flippedValue, shiftedValue)
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
    
    # print(ci,coverDnaStr,si,secDnaStr, xor, zeros, appendStr, stegoKey)
    
    return stegoKey
                    
    

def generateKey():
    if secImg is None or coverImg is None:
            messagebox.showerror(title = "File error", message = "Select both secrete image and cover image files!")
            return False
    
    fileStegoKey = open(keyFile, 'w')
    I = list(secImg.getdata())
    C = list(coverImg.getdata())
    for i in range(0,len(I)):
    # for i in range(0,100):
        fakeImgPixel = generateFakeSecreteImg(I[i])
        stegoKey = stegoKeyGeneration(C[i], fakeImgPixel)
        if i != 0 and i%250 == 0:
            stegoKey = "\n" + stegoKey + ","
        else:
            stegoKey += ","
        fileStegoKey.write(stegoKey)
    fileStegoKey.close()
    
    
    
    return "stegoKey.csv"

# def open_img_sec(imgType):
#     open_img(fram1, labelSelectSecreteImage, secImgPanel)

# def open_img_cover():
#     open_img(fram2, labelSelectCoverImage, coverImgPanel)

def generateKeyGui():
    file = generateKey()
    if(bool(file)):
        messagebox.showinfo(title = "Success!", message = "Stego - Key Generated Successfully. You may look at it in the file " + file)
        frmSender.pack()

def open_img(frame, imgPanel, imgType):
# def open_img():   
    global secImg
    global coverImg
    
    # Select the Imagename  from a folder
    x = filename = filedialog.askopenfilename(title ='Select an image')
    
    if x == "":
        messagebox.showwarning(title = "File error", message = "No file selected")
        return x
 
    # opens the image
    img = Image.open(x)
     
    # resize the image and apply a high-quality down sampling filter
    img = img.resize((250, 250), Image.ANTIALIAS)
 
    # PhotoImage class is used to add image to widgets, icons etc
    pImg = ImageTk.PhotoImage(img)
  
    imgPanel.configure(image = pImg)
    imgPanel.img = pImg
    
    if imgType == "sec":
        secImg = img
        with open(".temp", "w") as file:
            file.write(x)
    else:
        coverImg = img
        shutil.copy(x,coverImage)
def imagesTuple():
    with open(".temp", "r") as file:
        fileName = file.read()
    return (keyFile, coverImage, fileName)

def verify():
    user_pass = l_pass.get()
    user_id = lid.get()
    if user_id == "sender" and user_pass == "sender123":
        login_by = "Admin"
        login_allow()
    else:
        messagebox.showinfo("", "wrong input")


def login_allow():
    l_login.pack_forget()
    rootFrame.pack()

def sendFile(filenameTuple):
    # the ip address or hostname of the server, the receiver
    host = txtIpAddress.get()
    # the port
    port = int(txtPortNumber.get())
    
    j = 0
    
    for filename in filenameTuple:    
        filesize = os.path.getsize(filename)

        # create the client socket
        s = socket.socket()

        print(f"[+] Connecting to {host}:{port}")
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            return 1
        keygenLog("[+] Connected.")


        # send the filename and filesize
        keygenLog("Sending file",filename,". Size:", filesize)
        if j == 2:
            s.send(f"secImg{SEPARATOR}{filesize}".encode())
        else:
            s.send(f"{filename}{SEPARATOR}{filesize}".encode())
        j += 1

        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", \
                             unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            i = 1
            while True:
                # read the bytes from the file
                keygenLog("Reading Buffer")
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    keygenLog("No bytes read")
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                keygenLog(str(i) + ". Sending bytes")
                i += 1
                s.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
    return 0

def sendFilesOverNetwork():    
    if sendFile(imagesTuple()) != 0:
        messagebox.showerror(title = "Network error",
                               message = "Unable to connect to server")
    else:
        messagebox.showinfo(title = "Success",
                               message = "Sending cover image and stego key successful")

#main

#Create placeHolder directory if does not exist

if os.path.exists(placeHolder):
    shutil.rmtree(placeHolder)
os.makedirs(placeHolder)

#Create app using with separating widget

root=Tk()  
#App Title  
root.title("Key Generation - Zero Steganography - Sender")
root.geometry("1000x1000") 

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

ttk.Label(rootFrame, text="Key Generation for Zero Steganography Using DNA Sequences").pack() 

#Create Frams  
mf = Frame(rootFrame)
mf.pack()

fram1=ttk.Frame(mf, relief=RAISED)  
fram2=ttk.Frame(mf, relief=RAISED)  
fram1.grid(row = 0, column = 0, padx = 50)
fram2.grid(row = 0, column = 1, padx = 50)

buttonSecImg = Button(fram1, 
                 text ='Open secrete file',
                 command = lambda: open_img(fram1, secImgPanel, "sec"))
buttonSecImg.pack()

secImgPanel = Label(fram1, text = "No image selected")
secImgPanel.pack(pady = 50, padx = 50)


buttonCoverImg = Button(fram2, 
                 text ='Open Cover Image file',
                 command = lambda: open_img(fram2, coverImgPanel, "cover"))
buttonCoverImg.pack()

coverImgPanel = Label(fram2, text = "No image selected")
coverImgPanel.pack(pady = 50, padx = 50)

buttnGenerateKey = Button(rootFrame, 
                 text ='Generate Key',
                         command=generateKeyGui)
buttnGenerateKey.pack(pady = 20)


#Sender Frame
frmSender = Frame(rootFrame, relief = RAISED)

lblIpAddress = Label(frmSender, text = "IP Address")
lblIpAddress.grid(row = 0, column = 0)

txtIpAddress = Entry(frmSender)
txtIpAddress.insert(0, "127.0.0.1")
txtIpAddress.grid(row = 0, column  = 1)

lblPortNumber = Label(frmSender, text = "Port Number")
lblPortNumber.grid(row = 1, column = 0)

txtPortNumber = Entry(frmSender)
txtPortNumber.insert(0, "5001")
txtPortNumber.grid(row = 1, column  = 1)

buttnSend = Button(frmSender, 
                 text ='Send',
                 command=sendFilesOverNetwork)
buttnSend.grid(row = 2, column = 1, columnspan = 2)

#Calling Main()  
root.mainloop()  