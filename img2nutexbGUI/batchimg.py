import os
import os.path
from os import listdir
from os.path import isfile, join
import sys
import pathlib
import shutil
import subprocess
import imghdr

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

import configparser
config = configparser.ConfigParser()


from multiprocessing import Process
import threading
from queue import Queue

root = Tk()
progressroot = Tk()
root.fromOutside=False
root.currentDir = os.getcwd()

#assumedLocation of img program if no config
defaultLocation = root.currentDir + "\img2nutexb.exe"
#default configuration
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'img2nutexbLocation': defaultLocation,
    'searchDir' : "",
    'destDir' : "",
    'root.maxThreads': "4"
    }


def CreateConfig():
    print("creating valid config")
    with open('config.ini', 'w+') as configfile:
        defaultConfig.write(configfile)
    config.read('config.ini')

#truncate strings for labels
def truncate(string,direciton=W,limit=20,ellipsis=True):
    if (len(string) < 3):
        return string
    text = ""
    addEllipsis = "..." if (ellipsis) else ""
    if direciton == W:
        text = addEllipsis+string[len(string)-limit:len(string)]
    else:
        text = string[0:limit]+addEllipsis
    return text

#show message
def message(text,type=""):
    type = type.lower()
    #what do you mean match type is only for 3.10?!?
    if type=="error":
        messagebox.showerror(root.title(),text)
    elif type=="warning":
        messagebox.showwarning(root.title(),text)
    else:
        messagebox.showinfo(root.title(),text)
    print(type+": "+text)
    
#check to make sure that the program is a valid file
def ValidExe():
    if (not root.imgnutexbLocation): return False
    if (os.path.isfile(root.imgnutexbLocation)):
        if (root.imgnutexbLocation.endswith(".exe")):
            return True
    return False
        

def ValidatePorgram():
    #if we don't have img2nutexb here, then ask for it!
    if (ValidExe() == False):
        message(type = "Warning",text = "img2nutexb.exe not found, please select it")
        ftypes = [    
            ('img2nutexb program', ["*.exe"])
        ]
        file = filedialog.askopenfile(title = "Search",filetypes = ftypes)
        root.imgnutexbLocation = file.name if file else ""
        #if selected file is in valid, quit
        if (not ValidExe()):
            config.set("DEFAULT","img2nutexbLocation",defaultLocation)
            message(type = "ERROR",text = "Selected file not valid")
            root.destroy()
            sys.exit("No img2nutexb.exe file")

        #write new location to config
        config.set("DEFAULT","img2nutexbLocation",root.imgnutexbLocation)
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)

    #blank nutexbFile
    root.blankFile = root.currentDir + r"\blank.nutexb"
    if (not os.path.isfile(root.blankFile)):
        message(type = "ERROR",text = "blank.nutexb is missing!")
        root.destroy()
        sys.exit("No blank nutexb")


    #create output file
    outputFile = open('output.txt','w+')
    outputFile.close()


def HasValidSearch():
    validPath = os.path.isdir(root.searchDir)
    if (validPath):
        #make sure there are files to search for in the search directory
        files = [f for f in listdir(root.searchDir) if isfile(join(root.searchDir, f))]
        if (len(files)>0):
            return True
    return False

def HasValidDest():
    return os.path.isdir(root.destDir)

def saveSearch():
    #Replace the textureListFile contents with the contents of our GUI
    textureListFile = open('textureList.txt','w+')
    textureListFile.write(root.textureEntry.get("1.0","end-1c"))
    textureListFile.close()
    print("Updated search file")
def setSearch():
    global desiredSearch
    root.searchDir = filedialog.askdirectory(title = "Search")
    if (root.searchDir != ""):
        validColor = "black" if HasValidSearch() else "red"
        root.search_label.config(text = truncate(root.searchDir), fg = validColor)
        
    config.set("DEFAULT","searchDir",root.searchDir)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)
        
    #when choosing a new directory, remove DNE tags
    newEntry = root.textureEntry.get("1.0","end-1c")
    newEntry = newEntry.replace("$DNE_","")
    root.textureEntry.delete("1.0","end")
    root.textureEntry.insert("1.0",newEntry)
    saveSearch()
    
def setDest():
    root.destDir = filedialog.askdirectory(title = "Destination")
    if (root.destDir != ""):
        validColor = "black" if HasValidDest() else "red"
        root.dest_label.config(text = truncate(root.destDir), fg = validColor)
        
    config.set("DEFAULT","destDir",root.destDir)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)


#populate root.textureEntry with textureFile contents
def readTexturesToGUI():
    root.textureEntry.delete("1.0","end-1c")
    textureListFile = open('textureList.txt','r')
    textures = textureListFile.readlines()
    textures = [texture.rstrip() for texture in textures]
    textureListFile.close()
    #Populate textfile without adding an extra new line at the end
    for i in range(len(textures)):
        newLine='\n' if i<len(textures)-1 else ''
        root.textureEntry.insert(END,textures[i]+newLine)

#GUI
def startGUI():
    pythonInfo = "Python: " + sys.version
    root.status = Label(root, text=truncate(pythonInfo,E,14,False), bd=1, relief=SUNKEN, anchor=E)
    root.status.pack(side = BOTTOM, fill=X)

    #scrollFrame = PanedWindow(orient = VERTICAL,borderwidth=10,width = 40)  
    #scrollFrame.pack(side = RIGHT,fill = Y, expand = 1)  
    #scroll = Scrollbar(scrollFrame)
    #scroll.pack(side = RIGHT, fill=Y)

    searchFrame = PanedWindow(orient = VERTICAL,borderwidth=10,width = root.width/2)  
    searchFrame.pack(side = LEFT, fill = Y, expand = 1)  
    searchFrame_label = Label(root, text="Set Directories to Search / Copy To", bd=1, relief=SUNKEN, anchor=N)
    searchFrame.add(searchFrame_label)
      
    root.search_label = Label(searchFrame,width=50,text=truncate(root.searchDir))
    root.dest_label = Label(searchFrame,width=50,text=truncate(root.destDir))
    search_btn = Button(searchFrame, text="Set Search Directory", command=setSearch)
    dest_btn = Button(searchFrame, text="Set Destination Directory", command=setDest)
    searchFrame.add(search_btn)
    searchFrame.add(root.search_label)
    searchFrame.add(dest_btn)
    searchFrame.add(root.dest_label)


    listFrame = PanedWindow(orient = VERTICAL,borderwidth=10,width = (root.width/2))  
    listFrame.pack(side = TOP,fill = Y, expand = 1)
    listFrame_label = Label(root, text="Files to Find (leave blank for all files)", bd=1, relief=SUNKEN)
    listFrame.add(listFrame_label)   

    root.textureEntry = ScrolledText(listFrame, bd = 2)  
    listFrame.add(root.textureEntry)

    #root.textureEntry.configure(yscrollcommand=scroll.set)
      
    #scroll.config(command=root.textureEntry.yview,width=40)
    #scrollFrame.add(scroll)
    
    #makesure it exists first
    textureListFile = open('textureList.txt','a+')
    textureListFile.close()
    readTexturesToGUI()


    #create run button
    run_btn = Button(searchFrame, text="Run", command=run,anchor=S)
    searchFrame.add(run_btn,pady=30)

imageExtensions = ["png", "jpg", "gif", "dds",
                   "tga", "tiff", "tco", "bmp"]
def ValidImage(img):
    ext = img[len(img)-3:len(img)]
    return ext in imageExtensions

def printAndWrite(string,color="black"):
    print(string)
    if (root.fromOutside):
        return
    root.status.config(text = string, fg = color)
    with open("output.txt", "a") as file:
        file.write(string)
        file.write("\n")
        
#main functions
def run():    
    printAndWrite("")
    #run img for each file, assuming said file exists
    if (not HasValidSearch()):
        message(type = "ERROR",text = "Search or Destination path invalid")
        return
    
    saveSearch()
    #gather a list of textures to find
    textureListFile = open('textureList.txt','r')
    textures = textureListFile.readlines()
    textures = [texture.rstrip() for texture in textures]
    textureListFile.close()

    root.emptyList=False
    #if textureList is blank, set the target list to ALL the files in a folder
    if (len(textures)<1):
        root.emptyList=True
        mypath = root.searchDir
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        for f in files:
            textures.append(f)

    #remove blanks
    while("" in textures) :
        textures.remove("")

    BatchImg(textures)

def init(searchDir="",destDir="",currentDir=""):
    root.title("img2nutexbGUI")

    root.searchDir = searchDir
    root.destDir = destDir
    root.currentDir = currentDir if currentDir != "" else os.getcwd()
    root.fromOutside = currentDir != ""

    if (not root.fromOutside):
        root.iconbitmap("icon.ico")
        root.width=600
        root.height=250
        root.geometry(str(root.width)+"x"+str(root.height))

        #create a config if necessary
        if (not os.path.isfile(root.currentDir + r"\config.ini")):
            CreateConfig()
        config.read('config.ini')

        #search and destination directory functions
        root.searchDir = config["DEFAULT"]["searchDir"]
        root.destDir = config["DEFAULT"]["destDir"]
    else:
        config.read(currentDir+'config.ini')


    root.imgnutexbLocation = config["DEFAULT"]["img2nutexbLocation"]
    print("imgnutexbLocation: "+root.imgnutexbLocation)
    if not "root.maxThreads" in config["DEFAULT"]:
        config["DEFAULT"]["root.maxThreads"]="4"
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)
    root.maxThreads = int(config["DEFAULT"]["maxThreads"])

    progressroot.withdraw()
    progressroot.minsize(250,100)
    root.withdraw()
    root.emptyList=False

    #BatchImg(textures,True)

def BatchImg(textures):
    rewriteList=False
    overwritePrompt=True
    overwriteFiles=True
    useDDSPrompt=True
    useDDSOption=True
    renamePrompt=True
    rename=True

    subcallName=[]
    subcallTarget=[]
    subcallNewFile=[]
    subcallExtra=[]

    printAndWrite("Running...")
    #For each texture, see if we can run the program
    for i in range(len(textures)):
        t = textures[i]
        #ignore files with the common tag
        if (t.find("/common/")>-1):
            printAndWrite(t + " is a common file; skipping")
            continue
        #ignore files we know do not exist
        if (t.startswith("$DNE_")):
            printAndWrite(t + " has DNE tag; skipping")
            continue

        #find the desired new name
        split_tup = os.path.splitext(t)
        basename = split_tup[0]
        if "." in basename:
            basesplit = os.path.splitext(basename)
            if basesplit[0] != basesplit[1] and basesplit[1] != "":
                basename = basesplit[0]
        newNutexb = root.destDir + "/" +basename+".nutexb"
        newNutexb = newNutexb.lower()

        #replace nrm with nor
        if (newNutexb.find("_nrm.")>-1 or newNutexb.find("_dif.")>-1):
            if (renamePrompt):
                renamePrompt = False
                rename = messagebox.askyesno(root.title(), "Rename _dif and _nrm suffixes to Ultimate's _col and _nor?",icon ='info')
            if (rename):
                newNutexb = newNutexb.replace("_dif.nutexb","_col.nutexb")
                newNutexb = newNutexb.replace("_nrm.nutexb","_nor.nutexb")
        
        #if we find a file that already exists, ask to overwrite
        if (os.path.isfile(newNutexb)):
            if (overwritePrompt):
                overwritePrompt = False
                overwriteFiles = messagebox.askyesno(root.title(), "Some files already exists in the destination directory! Overwrite all files?",icon ='warning')
                
            if (overwriteFiles == False):
                printAndWrite(t + " exists and will not overwrite")
                continue
            

        #if search target does not have an extension, let's find it
        if (t.find(".")<0):
            for (dirpath, dirnames, filenames) in os.walk(root.searchDir):
                #print([os.path.join(dirpath, file) for file in filenames])
                for filename in filenames:
                    split_tup = os.path.splitext(filename)
                    basename = split_tup[0]
                    if (basename == t):
                        #Set rewrite list to true, helps prevent looping through all files in the future
                        rewriteList=True
                        #update t
                        t = t+split_tup[1]
                        #update the item in the list
                        textures[i] = t
                        break
             
        #create name of search target
        targetFile = root.searchDir + "/" + t
        fileNameExists = os.path.isfile(targetFile)
        
        #if file doesn't exist, skip
        if (not fileNameExists):
            rewriteList=True
            textures[i] = "$DNE_" + t
            printAndWrite(t + " does not exist")
            continue
        #if it's not an image file, ignore it
        if (not ValidImage(targetFile)):
            rewriteList=True
            textures[i] = "$DNE_" + t
            printAndWrite(os.path.basename(targetFile) + " is not an image file")
            continue
        

        internalName = os.path.splitext(os.path.basename(targetFile))[0]
        subcallName.append(internalName)
        subcallTarget.append(targetFile)
        subcallNewFile.append(newNutexb)
        
    if (useDDSPrompt):
        useDDSPrompt = False
        useDDSOption = messagebox.askyesno(root.title(), "Use img2nutexb DDS options for DDS Files? (Some failed dds conversions can be fixed by not using these options)",icon ='info')
    if (useDDSOption):
        subcallExtra.append("-d")
        subcallExtra.append("-u")

    root.withdraw()
        


    progressroot.deiconify()

    progressroot.queue = Queue(maxsize=0)

    for i in range(len(subcallName)):
        internalName = subcallName[i]
        targetFile = subcallTarget[i]
        newNutexb = subcallNewFile[i]
        if (internalName == "" or targetFile == "" or newNutexb == ""):
            continue

        #clone blank file
        shutil.copy(root.blankFile,newNutexb)

        
        #run program on it depending on if the text file ends in dds
        subcall = [root.imgnutexbLocation,"-n "+internalName,targetFile,newNutexb]
        if len(subcallExtra)>0:
            for e in subcallExtra:
                subcall.append(e)
        progressroot.queue.put(subcall)

    imgThread = threading.Thread(target=StartThreads, args=())
    imgThread.start()

    progressroot.grid()
    progressroot.progressBar = ttk.Progressbar(
        progressroot,
        orient='horizontal',
        mode='determinate',
        length=280
    )
    progressroot.progressBar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
    progressroot.progressBar['value'] = 0
    progressroot.Progress=0

    progressroot.progressLabel = Label(progressroot, text=UpdateProgressLabel(progressroot.progressBar['value']))
    progressroot.progressLabel.grid(column=0, row=1, columnspan=2)
    progressroot.deiconify()
    progressroot.protocol("WM_DELETE_WINDOW", quit)

    start = time.time()

    progressroot.footer = Label(progressroot, text="This could take awhile...", bd=1, relief=SUNKEN, anchor=N)
    progressroot.footer.grid(row=2,columnspan=2,sticky="ew")

    while imgThread.is_alive():
        progressroot.update()
        progressroot.progressBar['value'] = (progressroot.Progress*100)
        progressroot.progressLabel['text'] = UpdateProgressLabel(progressroot.progressBar['value'])
        elapsed = truncate(str(time.time()-start),E,5,False)
        progressroot.footer.config(text="Time elapsed: "+elapsed+"s")
        pass

    progressroot.progressBar['value'] = 100
    progressroot.progressLabel['text'] = UpdateProgressLabel(progressroot.progressBar['value'])
    progressroot.update()
    time.sleep(1.0)
    print("Images converted")

    progressroot.withdraw()
    if (root.fromOutside):
        return

    #Only rewrite if necessary
    if (rewriteList==True and root.emptyList==False):
        textureListFile = open('textureList.txt','w')
        textureListFile.close()
        #Rewrite textureListFile
        with open('textureList.txt', 'a+') as textureListFile:
            print("Rewriting textureList.txt")
            for t in textures:
                textureListFile.write(t)
                textureListFile.write("\n")
                
        textureListFile.close()
        readTexturesToGUI()

    #progressroot.withdraw()
    #sys.exit("success")
    message("Finished!")
    root.deiconify()

imgThread = None
def UpdateProgressLabel(v):

    labelText = f"{v}"
    labelText = truncate(str(progressroot.progressBar['value']),E,5,False)
    return f"Current Progress: "+labelText+"%"

def StartThreads():
    subthreads = []
    for i in (range(root.maxThreads)):
        subthread=threading.Thread(target=BatchImgSubCall, args=())
        subthreads.append(subthread)
        subthread.start()
    # checks whether thread is alive #
    startSize = progressroot.queue.qsize()
    while True:
        if progressroot.queue.qsize()==0:
            break
        else:
            progressroot.Progress = 1-(float(progressroot.queue.qsize())/float(startSize))
    progressroot.Progress = 1
    print("Finished Conversions")


import time
def BatchImgSubCall():
    while True:
        subcall = progressroot.queue.get()
        print("Converting "+os.path.basename(subcall[2]))
        try:
            process_output = subprocess.run(subcall)#, stdout=stdout_file, stderr=stdout_file, text=True)
        except:
            print(os.path.basename(newNutexb) + " can't be converted; might be open in another program")

        convertedDDS = "" if len(subcall)>4 else " using dds options"
        print("Created "+os.path.basename(subcall[3]) + convertedDDS)
        progressroot.queue.task_done()
        


#on window closed
def onClosed():
    saveSearch()
    root.destroy()
    sys.exit("User exited")
    

def Main():
    init()
    root.deiconify()
    ValidatePorgram()
    startGUI()

if __name__ == '__main__':
    Main()
    root.protocol("WM_DELETE_WINDOW", onClosed)
    root.mainloop()

