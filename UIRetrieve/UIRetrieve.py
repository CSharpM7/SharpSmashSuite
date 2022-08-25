import os
import os.path

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

import sys
import shutil

#import glob
import re
reAlpha='[^0-9]'

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

root.modType = "stage"

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
        root.modType = "stage"
        return True
    elif (root.destinationDirName == "fighter"):
        root.modType = "fighter"
        return True
    else:
        subfolders = [f.path for f in os.scandir(root.destinationDir) if f.is_dir()]
        for dirname in list(subfolders):
            if (os.path.basename(dirname) == "stage"):
                root.modType = "stage"
                return True
            elif (os.path.basename(dirname) == "fighter"):
                root.modType = "fighter"
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
        sys.exit("Not a stage/fighter folder")
        
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
root.modSkins = []

def GetModSkins():
    modelFolder = root.destinationDir+"/fighter/"+root.modName+"/model"
    print(modelFolder)
    bodyFolders = [b.path for b in os.scandir(modelFolder+"/body") if b.is_dir()]
    for fname in list(bodyFolders):
        fname = os.path.basename(fname).replace("c0","")
        fname = re.sub(reAlpha, '', fname)

        #If empty, skip
        if (fname==""): continue

        #Make sure the value is a valid int
        validValue=True
        try:
            skinID = int(fname) % 8
        except:
            validValue=False
        if (not validValue): continue

        skinName = "0"+str(skinID)
        print("found skin "+skinName)
        root.modSkins.append(skinName)

    
#Get or Set root.destinationDir
if (root.destinationDir == ""):
    setDestinationDir()

root.fighterUINames = [0,1,2,3,4,6]
def combUIFolder(target,uiArray,folderUI):
    modType = "chara" if root.modType=="fighter" else "stage"
    ui_Folder = root.arcDir + r"/export/ui/" + folderUI + r"/"+modType
    #comb through each type_N folder to find files
    subfolders = [f.path for f in os.scandir(ui_Folder) if f.is_dir()]
    for folder in list(subfolders):
        #For stages, we don't need to account for each skin
        if (len(root.modSkins)==0):
            targetName = folder+r"/"+os.path.basename(folder)+"_"+target+".bntx"
            if (os.path.exists(targetName)):
                uiArray.append(targetName)
        #Fighters on the other hand...ooooo boy
        else:
            for skin in root.modSkins:
                targetName = folder+r"/"+os.path.basename(folder)+"_"+target+"_"+skin+".bntx"
                if (os.path.exists(targetName)):
                    uiArray.append(targetName)


    return uiArray

def getUIDump(target):
    uiArray = []
    isDLC = False

    #comb through each stage/fighter_N folder to find files
    uiArray = combUIFolder(target,uiArray,"replace")

    if (len(uiArray)==0):
        isDLC = True
        uiArray = combUIFolder(target,uiArray,"replace_patch")

    return uiArray,isDLC


def getUI(quitOnFail=False):
    #Get source UI
    uiArray=[]
    uiArray,isDLC = getUIDump(root.modName)
    if (len(uiArray)==0):
        if (quitOnFail==False):
            print("Could not find UI for "+root.modName+", searching manually")
            return
        else:
            messagebox.showinfo(root.title(),"Could not find UI for that "+root.modType)
            root.destroy()
            sys.exit("no ui found")

    folderBase = "replace"
    folderDLC = "replace_patch"
    folderUI = folderDLC if isDLC else folderBase

    if (root.modType == "fighter"):
        root.modType = "chara"

    destinationFolders = []
    desitnationParent = root.destinationDir+r"/ui/"+folderUI+ r"/"+root.modType

    folderNames = range(0,5)
    if (root.modType == "chara"):
        folderNames = [0,1,2,3,4,6] 
    #Populate folders as necessary 
    for i in folderNames:
        path = desitnationParent+r"/"+root.modType+"_"+str(i)
        destinationFolders.append(path)
        os.makedirs(path, exist_ok=True)

    #for each file in the uiArray, copy it to the proper destinationFolder
    for file in uiArray:
        par = os.path.abspath(os.path.join(file, os.pardir))
        #get parent directory of file. For each destination, if the basename is the same...
        for d in destinationFolders:
            if os.path.basename(par) == os.path.basename(d):
                print(os.path.basename(par))
                #ask to copy if it exists
                if (os.path.exists(d+r"/"+os.path.basename(file))):
                    res = messagebox.askyesno(root.title(), "Overwrite "+os.path.basename(file)+"?",icon ='warning')
                    if res != True:
                        print("skip "+os.path.basename(file))
                        continue

                #copy ui to destination
                shutil.copy(file,d+r"/"+os.path.basename(file))
                break

    messagebox.showinfo(root.title(),"UI Retrieved for "+root.modName+"!")
    #open folder
    import webbrowser
    webbrowser.open(desitnationParent)

    #quit
    root.destroy()
    sys.exit("success!")



root.modName = ""
subfolders = [f.path for f in os.scandir(root.destinationDir) if f.is_dir()]
for dirname in list(subfolders):
    if (os.path.basename(dirname) == "stage"):
        modsubfolder = [s.path for s in os.scandir(dirname) if s.is_dir()]
        root.modName = os.path.basename(modsubfolder[0])
        if (root.modName == "common" and len(modsubfolder)>1):
            root.modName = os.path.basename(modsubfolder[1])
    elif (os.path.basename(dirname) == "fighter"):
        modsubfolder = [s.path for s in os.scandir(dirname) if s.is_dir()]
        root.modName = os.path.basename(modsubfolder[0])
        if (root.modName == "common" and len(modsubfolder)>1):
            root.modName = os.path.basename(modsubfolder[1])

print ("Selected mod: "+root.modName )
if (root.modType == "fighter"):
    GetModSkins()
if (root.modName!=""):
    getUI()
    #GetUI exists system on completion

#Create UI for manually if no stage/fighter name was found
def manualUI():
    root.modName = root.e.get()
    root.withdraw()
    if (root.modName==None or root.modName == ""):
        root.destroy()
        sys.exit("no input")
    getUI(True)

messagebox.showinfo(root.title(),"Could not find "+root.modType+" associated with this mod, please type in the "+root.modType+" name manually on the next window")
root.deiconify()
root.label = Label(root, text="Type in the name of the "+root.modType+" you want to destination (ie ridley,battlefield_s,etc)", anchor=N)
root.label.pack(side = TOP)
root.e = Entry(root,width =50)
root.e.pack()
root.e.focus_set()
b = Button(root, text = "OK", width = 10, command = manualUI)
b.pack()

mainloop()

    
