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

import configparser
config = configparser.ConfigParser()

#create initial GUI settings
root = Tk()
root.title("My Title")
root.iconbitmap("icon.ico")
root.width=600
root.height=250
root.geometry(str(root.width)+"x"+str(root.height))
#assumedLocation of img program if no config
defaultLocation = os.getcwd() + "\img2nutexb.exe"
#default configuration
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'img2nutexbLocation': defaultLocation,
    'searchDir' : "",
    'destDir' : ""
    }

def CreateConfig():
    print("creating valid config")
    with open('config.ini', 'w+') as configfile:
        defaultConfig.write(configfile)
    config.read('config.ini')

#create a config if necessary
if (not os.path.isfile(os.getcwd() + r"\config.ini")):
    CreateConfig()
config.read('config.ini')
      
#read in the config file to find the img program file
imgnutexbLocation = config["DEFAULT"]["img2nutexbLocation"]
print("imgnutexbLocation: "+imgnutexbLocation)

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
def message(type,string):
    type = type.lower()
    #what do you mean match type is only for 3.10?!?
    if type=="error":
        messagebox.showerror(root.title(),string)
    elif type=="warning":
        messagebox.showwarning(root.title(),string)
    else:
        messagebox.showinfo(root.title(), string)
    print(type+": "+string)
    
#check to make sure that the program is a valid file
def ValidExe():
    if (not imgnutexbLocation): return False
    if (os.path.isfile(imgnutexbLocation)):
        if (imgnutexbLocation.endswith(".exe")):
            return True
    return False
            
#if we don't have img2nutexb here, then ask for it!
if (ValidExe() == False):
    message("Warning","img2nutexb.exe not found, please select it")
    ftypes = [    
        ('img2nutexb program', ["*.exe"])
    ]
    file = filedialog.askopenfile(title = "Search",filetypes = ftypes)
    imgnutexbLocation = file.name if file else ""
    #if selected file is in valid, quit
    if (not ValidExe()):
        config.set("DEFAULT","img2nutexbLocation",defaultLocation)
        message("ERROR","Selected file not valid")
        root.destroy()
        sys.exit("No img2nutexb file")

    #write new location to config
    config.set("DEFAULT","img2nutexbLocation",imgnutexbLocation)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)

#blank nutexbFile
blankFile = os.getcwd() + r"\blank.nutexb"
if (not os.path.isfile(blankFile)):
    message("ERROR","blank.nutexb is missing!")
    root.destroy()
    sys.exit("No blank nutexb")


#search and destination directory functions
root.searchDir = config["DEFAULT"]["searchDir"]
root.destDir = config["DEFAULT"]["destDir"]
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

def setSearch():
    global desiredSearch
    root.searchDir = filedialog.askdirectory(title = "Search")
    if (root.searchDir != ""):
        validColor = "black" if HasValidSearch() else "red"
        search_label.config(text = truncate(root.searchDir), fg = validColor)
        
    config.set("DEFAULT","searchDir",root.searchDir)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)
def setDest():
    root.destDir = filedialog.askdirectory(title = "Destination")
    if (root.destDir != ""):
        validColor = "black" if HasValidDest() else "red"
        dest_label.config(text = truncate(root.destDir), fg = validColor)
        
    config.set("DEFAULT","destDir",root.destDir)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)

#GUI

pythonInfo = "Python: " + sys.version
status = Label(root, text=truncate(pythonInfo,E,14,False), bd=1, relief=SUNKEN, anchor=E)
status.pack(side = BOTTOM, fill=X)

scrollFrame = PanedWindow(orient = VERTICAL,borderwidth=10,width = 40)  
scrollFrame.pack(side = RIGHT,fill = Y, expand = 1)  
scroll = Scrollbar(scrollFrame)
#scroll.pack(side = RIGHT, fill=Y)

searchFrame = PanedWindow(orient = VERTICAL,borderwidth=10,width = root.width/2)  
searchFrame.pack(side = LEFT, fill = Y, expand = 1)  
searchFrame_label = Label(root, text="Set Directories to Search / Copy To", bd=1, relief=SUNKEN, anchor=N)
searchFrame.add(searchFrame_label)
  
search_label = Label(searchFrame,width=50,text=truncate(root.searchDir))
dest_label = Label(searchFrame,width=50,text=truncate(root.destDir))
search_btn = Button(searchFrame, text="Set Search Directory", command=setSearch)
dest_btn = Button(searchFrame, text="Set Destination Directory", command=setDest)
searchFrame.add(search_btn)
searchFrame.add(search_label)
searchFrame.add(dest_btn)
searchFrame.add(dest_label)


listFrame = PanedWindow(orient = VERTICAL,borderwidth=10,width = (root.width/2))  
listFrame.pack(side = TOP,fill = Y, expand = 1)
listFrame_label = Label(root, text="Files to Find (leave blank for all files)", bd=1, relief=SUNKEN)
listFrame.add(listFrame_label)   

textureEntry = Text(listFrame, bd = 5)  
listFrame.add(textureEntry)

textureEntry.configure(yscrollcommand=scroll.set)
  
scroll.config(command=textureEntry.yview,width=40)
scrollFrame.add(scroll)
    
#populate textureEntry with textureFile contents
def readTexturesToGUI():
    textureEntry.delete("1.0","end-1c")
    textureListFile = open('textureList.txt','r')
    textures = textureListFile.readlines()
    textures = [texture.rstrip() for texture in textures]
    textureListFile.close()
    #Populate textfile without adding an extra new line at the end
    for i in range(len(textures)):
        newLine='\n' if i<len(textures)-1 else ''
        textureEntry.insert(END,textures[i]+newLine)

#makesure it exists first
textureListFile = open('textureList.txt','a+')
textureListFile.close()
readTexturesToGUI()

imageExtensions = ["png", "jpg", "gif", "dds",
                   "tga", "tiff", "tco", "bmp"]
def ValidImage(img):
    ext = img[len(img)-3:len(img)]
    return ext in imageExtensions

outputFilePath="output.txt"
#create output file
outputFile = open('output.txt','w+')
outputFile.close()
def printAndWrite(string):
    print(string)
    with open(outputFilePath, "a") as file:
        file.write(string)
        file.write("\n")
        
#main functions
def run():    
    #run img for each file, assuming said file exists
    if (not HasValidSearch()):
        message("ERROR","Search or Destination path invalid")
        return
    
    #Replace the textureListFile contents with the contents of our GUI
    textureListFile = open('textureList.txt','w+')
    textureListFile.write(textureEntry.get("1.0","end-1c"))
    textureListFile.close()
    #gather a list of textures to find
    textureListFile = open('textureList.txt','r')
    textures = textureListFile.readlines()
    textures = [texture.rstrip() for texture in textures]
    textureListFile.close()

    emptyList=False
    #if textureList is blank, set the target list to ALL the files in a folder
    if (len(textures)<1):
        emptyList=True
        mypath = root.searchDir
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        for f in files:
            textures.append(f)

    #remove blanks
    while("" in textures) :
        textures.remove("")

    rewriteList=False
    #For each texture, see if we can run the program
    for i in range(len(textures)):
        t = textures[i]
        #ignore files with the common tag
        if (t.find("/common/")==True):
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
        
        #if it's not an image file, ignore it
        if (not ValidImage(targetFile)):
            printAndWrite("Skipped "+t)
            continue
        
        #create new name for nutexb texture
        split_tup = os.path.splitext(t)
        newNutexb = root.destDir + "/" +split_tup[0]+".nutexb"

        #If the file exists, let's run the program
        if (os.path.isfile(targetFile)):
            #clone blank file
            shutil.copy(blankFile,newNutexb)
            #run program on it depending on if the text file ends in dds
            subcall = [imgnutexbLocation,"-n "+split_tup[0],targetFile,newNutexb]
            if (split_tup[1] == ".dds"):
                subcall.append("-d")
                subcall.append("-u")
            #output any errors to a textfile
            with open('output.txt', 'a+') as stdout_file:
                process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
                print(process_output.__dict__)
                
            printAndWrite("Created "+newNutexb)
        else:
            printAndWrite(targetFile + " does not exist")
        

    #Only rewrite if necessary
    if (rewriteList==True and emptyList==False):
        textureListFile = open('textureList.txt','w')
        textureListFile.close()
        #Rewrite textureListFile
        with open('textureList.txt', 'a+') as textureListFile:
            print("REWRITE")
            for t in textures:
                textureListFile.write(t)
                textureListFile.write("\n")
                
        textureListFile.close()
        readTexturesToGUI()

    root.withdraw()
    sys.exit("success")

#create run button
run_btn = Button(searchFrame, text="Run", command=run,anchor=S)
searchFrame.add(run_btn,pady=30)      
    
root.mainloop()

