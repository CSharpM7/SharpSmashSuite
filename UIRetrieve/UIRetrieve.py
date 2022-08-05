import os
import os.path
import json
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
import shutil
import glob
import sys

import configparser
config = configparser.ConfigParser()
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'arcDir' : ""
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

#create ui for program
root = Tk()
root.title("UI Retrieve")
root.withdraw()

#make sure that it is a validated destination folder, otherwise quit
def IsValidArc():
    #Is this the directory with ArcExplorer.exe?
    if (os.path.exists(root.arcDir + r"/ArcExplorer.exe")):
        #Has ui/replace been extracted?
        if (os.path.exists(root.arcDir + r"/export/ui/replace")):
            return True
    return False

#open folder dialogue
def setarcDir():
    messagebox.showinfo(root.title(),"Set ArcExplorer directory")
    root.arcDir = filedialog.askdirectory(title = "Select your ArcExplorer directory")
    if (root.arcDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidArc() == False):
        messagebox.showerror(root.title(),"Please select the root of your ArcExplorer folder")
        root.destroy()
        sys.exit("Not a stage folder")

#make sure that it is a validated destination folder, otherwise quit
def IsValidDestination():
    root.destinationDirName = os.path.basename(root.destinationDir)
    if (root.destinationDirName == "stage"):
        return False
    else:
        subfolders = [f.path for f in os.scandir(root.destinationDir) if f.is_dir()]
        for dirname in list(subfolders):
            if (os.path.basename(dirname) == "stage"):
                return True
    return False

#open folder dialogue
def setDestinationDir():
    messagebox.showinfo(root.title(),"Select your mod's main folder")
    root.destinationDir = filedialog.askdirectory(title = "Select your mod's main folder")
    if (root.destinationDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidDestination() == False):
        messagebox.showerror(root.title(),"Please select the root of your mod's folder! This folder should contain a stage or fighter folder within it!")
        root.destroy()
        sys.exit("Not a stage folder")
        
#Set Arc Directory if needed
root.arcDir = config["DEFAULT"]["arcDir"]
if (not os.path.isdir(root.arcDir)):
    root.arcDir = ""
    
#Get or Set root.destinationDir
if (root.arcDir == ""):
    print("no arc")
    setarcDir()

config.set("DEFAULT","arcDir",root.arcDir)
with open('config.ini', 'w+') as configfile:
        config.write(configfile)

#Set Destination Dir
root.destinationDir = ""
    
#Get or Set root.destinationDir
if (root.destinationDir == ""):
    setDestinationDir()

def combUIFolder(target,uiArray,folderUI):
    ui_Folder = root.arcDir + r"/export/ui/" + folderUI + r"/stage"
    #comb through each stage_N folder to find files
    subfolders = [f.path for f in os.scandir(ui_Folder) if f.is_dir()]
    for folder in list(subfolders):
        targetName = folder+r"/"+os.path.basename(folder)+"_"+target+".bntx"
        if (os.path.exists(targetName)):
            uiArray.append(targetName)
    return uiArray

def getUIDump(target):
    uiArray = []
    isDLC = False

    #comb through each stage_N folder to find files
    uiArray = combUIFolder(target,uiArray,"replace")

    if (len(uiArray)==0):
        isDLC = True
        uiArray = combUIFolder(target,uiArray,"replace_patch")

    return uiArray,isDLC

def callback():
    root.stageName = root.e.get()
    root.withdraw()
    print (root.stageName )
    if (root.stageName==""):
        root.destroy()
        sys.exit("no input")


    #Get source UI
    uiArray=[]
    uiArray,isDLC = getUIDump(root.stageName)
    if (len(uiArray)==0):
        messagebox.showinfo(root.title(),"Could not fine UI for that stage")
        root.destroy()
        sys.exit("no ui found")

    folderBase = "replace"
    folderDLC = "replace_patch"
    folderUI = folderDLC if isDLC else folderBase


    destinationFolders = []
    desitnationParent = root.destinationDir+r"/ui/"+folderUI+ r"/stage"
    #Populate folders as necessary 
    for i in range(0,5):
        path = desitnationParent+r"/stage_"+str(i)
        destinationFolders.append(path)
        os.makedirs(path, exist_ok=True)

    #for each file in the uiArray, copy it to the proper destinationFolder
    for file in uiArray:
        par = os.path.abspath(os.path.join(file, os.pardir))
        #get parent directory of file. For each destination, if the basename is the same...
        for d in destinationFolders:
            if os.path.basename(par) == os.path.basename(d):
                print(os.path.basename(par))
                #copy ui to destination
                shutil.copy(file,d+r"/"+os.path.basename(file))
                break

    messagebox.showinfo(root.title(),"UI Retrieved!")
    #open folder
    import webbrowser
    webbrowser.open(desitnationParent)

    #quit
    root.destroy()
    sys.exit("success!")

root.deiconify()
root.title("UI Retrieve")
root.stageName = ""
root.label = Label(root, text="Type in the name of the stage you want to search (ie battlefield_s)", anchor=N)
root.label.pack(side = TOP)
root.e = Entry(root,width =50)
root.e.pack()

root.e.focus_set()

b = Button(root, text = "OK", width = 10, command = callback)
b.pack()

mainloop()

    
