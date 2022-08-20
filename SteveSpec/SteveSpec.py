import os
import os.path
import json
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
import shutil
import subprocess
import glob
import sys
import webbrowser
import xml.etree.ElementTree as ET

import configparser
config = configparser.ConfigParser()
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'parcelDir' : "",
    'arcDir' : "",
    'stageParamsLocation' : "",
    'modDir' : "",
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
root.title("Steve Spec")
root.withdraw()

root.arcDir = config["DEFAULT"]["arcDir"]
root.stageParamsFolderShortcut = r"/stage/common/shared/param/"

#make sure that it is a validated parcel folder, otherwise quit
def IsValidParcel():
    #Is this the directory with ArcExplorer.exe?
    return (os.path.exists(root.parcelDir + r"/parcel.exe"))

def SetParcel():
    messagebox.showinfo(root.title(),"Set Parcel directory")
    root.parcelDir = filedialog.askdirectory(title = "Select your Parcel directory")
    if (root.parcelDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidParcel() == False):
        messagebox.showerror(root.title(),"Please select the root of your Parcel folder")
        root.destroy()
        sys.exit("Invalid Folder")

#make sure that it is a validated arc folder, otherwise quit
def IsValidArc():
    #Is this the directory with ArcExplorer.exe?
    if (os.path.exists(root.arcDir + r"/ArcExplorer.exe")):
        #Has stageParams been extracted?
        if (os.path.exists(root.arcDir + r"/export" + root.stageParamsFolderShortcut + r"groundconfig.prc")):
            return True
        else:
            messagebox.showerror(root.title(),"Please extra the folder stage/common/shared/param")
            root.destroy()
            sys.exit("Needs Param Folder")
    return False

#Get Stage Params folder from Valid Arc
def SetStageParams():
    #First, check to see if ArcExplorer Exists
    messagebox.showinfo(root.title(),"Set ArcExplorer directory")
    root.arcDir = filedialog.askdirectory(title = "Select your ArcExplorer directory")
    if (root.arcDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidArc() == False):
        messagebox.showerror(root.title(),"Please select the root of your ArcExplorer folder")
        root.destroy()
        sys.exit("Invalid Folder")

    root.stageParams = root.arcDir + r"/export"+ root.stageParamsFolderShortcut

#make sure that it is a validated destination folder, otherwise quit
def IsValidModFolder():
    root.modDirName = os.path.basename(root.modDir)
    if (root.modDirName == "stage"):
        return False
    else:
        subfolders = [f.path for f in os.scandir(root.modDir) if f.is_dir()]
        for dirname in list(subfolders):
            if (os.path.basename(dirname) == "stage"):
                return True
    return False

#open folder dialogue
def setModDir():
    messagebox.showinfo(root.title(),"Select your mod's main folder")
    root.modDir = filedialog.askdirectory(title = "Select your mod's main folder")
    if (root.modDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidModFolder() == False):
        messagebox.showerror(root.title(),"Please select the root of your mod's folder! This folder should contain a stage folder within it!")
        root.destroy()
        sys.exit("Not a stage folder")
        
#Set Parcel Directory if needed
root.parcelDir = config["DEFAULT"]["parcelDir"]
if (not os.path.isdir(root.parcelDir)):
    root.parcelDir = ""
#Get or Set root.parcelDir
if (root.parcelDir == ""):
    print("no parcel")
    SetParcel()

#Set Arc Directory and StageParams if needed
root.stageParams = config["DEFAULT"]["stageParamsLocation"]
if (not os.path.isdir(root.stageParams)):
    root.stageParams = ""
    
#Get or Set root.stageParams
if (root.stageParams == ""):
    print("no arc")
    SetStageParams()

#Set Mod Dir
root.modDir = config["DEFAULT"]["modDir"]
if (not os.path.isdir(root.modDir)):
    root.modDir = ""

#Get or Set root.modDir
if (root.modDir == ""):
    setModDir()
else:
    if (IsValidModFolder()):
        basename = os.path.basename(root.modDir)
        res = messagebox.askquestion(root.title(), 'Use most recent search directory? ('+basename+')')
        if res == 'yes':
            print("using same mod dir")
        elif res == 'no':
            setModDir()
            print("new mod directory")
        else:
            root.destroy()
            sys.exit("exited prompt")
    else:
        setModDir()

config.set("DEFAULT","parcelDir",root.parcelDir)
config.set("DEFAULT","arcDir",root.arcDir)
config.set("DEFAULT","stageParamsLocation",root.stageParams)
config.set("DEFAULT","modDir",root.modDir)
with open('config.ini', 'w+') as configfile:
        config.write(configfile)


root.stageName = None
subfolders = [f.path for f in os.scandir(root.modDir) if f.is_dir()]
for dirname in list(subfolders):
    if (os.path.basename(dirname) == "stage"):
        stagesubfolder = [s.path for s in os.scandir(dirname) if s.is_dir()]
        root.stageName = os.path.basename(stagesubfolder[0])
        if (root.stageName == "common"):
            root.stageName = None
            if (len(stagesubfolder)>1):
                root.stageName = os.path.basename(stagesubfolder[1])

#Uhh let's not check if there's a dump of the stage in Arc atm
#print(root.arcDir + r"/export/stage/"+root.stageName)
#if (not os.path.isdir(root.arcDir + r"/export/stage/"+root.stageName)):
#    root.stageName = None

print (root.stageName )
if (root.stageName == None):
    messagebox.showerror(root.title(),"There is no valid stage within that stage folder!")
    root.destroy()
    sys.exit("Not a stage folder")

defaultGroundInfo = os.getcwd() + r"\groundconfig.prcxml"
root.TempGroundInfo = os.getcwd() + r"\tempconfig.prcxml"
f = open(root.TempGroundInfo, "w")
f.close()
#root.TempGroundInfo = shutil.copy(defaultGroundInfo,os.getcwd() + r"\tempconfig.prcxml")
print("")

#Parse Steve data from main groundconfig file and place it in a temporary file
with open(defaultGroundInfo, 'rb') as file:
    parser = ET.XMLParser(encoding ='utf-8')
    tree = ET.parse(file,parser)
    treeRoot = tree.getroot()

    #remove cell_size
    for type_tag in treeRoot.findall('float'):
        treeRoot.remove(type_tag)
    #remove material_tabel
    for type_tag in treeRoot.findall('list'):
        treeRoot.remove(type_tag)
    #remove everything that isn't this stage
    for type_tag in treeRoot.findall('struct'):
        nodeName = type_tag.get('hash')
        if (nodeName != root.stageName):
            treeRoot.remove(type_tag)
        else:
            print(nodeName+"-"+root.stageName)
            for child in type_tag:
                childName = child.get("hash")

                #if (childName == "cell_minilen_side"):
                #    child.text = "175"
                #elif (childName == "cell_minilen_top"):
                #    child.text = "150"
                #elif (childName == "cell_minilen_bottom"):
                #    child.text = "150"
        #add 11 and 12
        #for child in item:
            #print(child.tag)
            #if (child.tag == "EnableAlphaSampleToCoverage"):
            #    child.tag = "Unk7"

    tree.write(root.TempGroundInfo)


def exportGroundInfoLazy():
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    shutil.copy(root.TempGroundInfo,targetLocation + r"\groundconfig.prcxml")
    messagebox.showinfo(root.title(),"Exported Info to "+root.stageName)
    webbrowser.open(targetLocation)

def exportGroundInfo():
    #Part one of parcel: patch the original file with our edited values
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    tempPrc = os.getcwd() +"/temp.prc"
    sourcePrc = root.stageParams + "/groundconfig.prc"
    parcel = root.parcelDir + r"/parcel.exe"

    subcall = [parcel,"patch",sourcePrc,root.TempGroundInfo,tempPrc]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)

    print("Prc patched!")
    #Part two: run parcel with the original and the patch to receive a prcx

    subcall = [parcel,"diff",sourcePrc,tempPrc,targetLocation+"/groundconfig.prcx"]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)

    print("Prcx created!")
    #Part three: copy the temp prcxml to the destination
    shutil.copy(root.TempGroundInfo,targetLocation + r"\groundconfig.prcxml")
    messagebox.showinfo(root.title(),"Exported groundconfig info to "+root.stageName)
    webbrowser.open(targetLocation)

exportGroundInfo()
root.destroy()
sys.exit("cool!")












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


def getUI(quitOnFail=False):
    #Get source UI
    uiArray=[]
    uiArray,isDLC = getUIDump(root.stageName)
    if (len(uiArray)==0):
        if (quitOnFail==False):
            return
        else:
            messagebox.showinfo(root.title(),"Could not find UI for that stage")
            root.destroy()
            sys.exit("no ui found")

    folderBase = "replace"
    folderDLC = "replace_patch"
    folderUI = folderDLC if isDLC else folderBase


    destinationFolders = []
    desitnationParent = root.modDir+r"/ui/"+folderUI+ r"/stage"
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

    messagebox.showinfo(root.title(),"UI Retrieved for "+root.stageName+"!")
    #open folder
    import webbrowser
    webbrowser.open(desitnationParent)

    #quit
    root.destroy()
    sys.exit("success!")

def manualUI():
    root.stageName = root.e.get()
    root.withdraw()
    print (root.stageName )
    if (root.stageName==None or root.stageName == ""):
        root.destroy()
        sys.exit("no input")
    getUI(True)


root.stageName = ""
subfolders = [f.path for f in os.scandir(root.modDir) if f.is_dir()]
for dirname in list(subfolders):
    if (os.path.basename(dirname) == "stage"):
        stagesubfolder = [s.path for s in os.scandir(dirname) if s.is_dir()]
        root.stageName = os.path.basename(stagesubfolder[0])

print (root.stageName )
if (root.stageName!=""):
    getUI()

#Create UI for manually if no stage/fighter name was found
messagebox.showinfo(root.title(),"Could not find stage associated with this mod, please type in the stage name manually on the next window")
root.deiconify()
root.label = Label(root, text="Type in the name of the stage you want to search (ie battlefield_s)", anchor=N)
root.label.pack(side = TOP)
root.e = Entry(root,width =50)
root.e.pack()
root.e.focus_set()
b = Button(root, text = "OK", width = 10, command = manualUI)
b.pack()

mainloop()

    
