import os
from os import listdir
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
import yaml

import configparser
config = configparser.ConfigParser()
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'parcelDir' : "",
    'arcDir' : "",
    'yamlvd' : "",
    'stageParamsLocation' : "",
    'modDir' : ""
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
#root.iconbitmap(os.getcwd() +"/icon.ico")
root.withdraw()

root.arcDir = config["DEFAULT"]["arcDir"]
root.stageParamsFolderShortcut = r"/stage/common/shared/param/"

#make sure that it is a validated parcel folder, otherwise quit
def IsValidParcel():
    #Is this the directory with Parcel.exe?
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
        if (os.path.exists(root.arcDir + r"/export" + root.stageParamsFolderShortcut + "groundconfig.prc")):
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
    #Copy em for our working file
    shutil.copy(root.stageParams + "groundconfig.prc", os.getcwd()+"/groundconfig.prc")

def SetYamlvd():
    messagebox.showinfo(root.title(),"Set Yamlvd directory")
    root.yamlvd = filedialog.askdirectory(title = "Select your Yamlvd directory")
    if (root.yamlvd == ""):
        root.destroy()
        sys.exit("Invalid folder")
    root.yamlvd = root.yamlvd + r"/yamlvd.exe"
    print(root.yamlvd)
    if (os.path.exists(root.yamlvd) == False):
        messagebox.showerror(root.title(),"Please select the root of your Yamlvd folder")
        root.destroy()
        sys.exit("Invalid Folder")


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

#Get or Set root.stageParams
root.yamlvd = config["DEFAULT"]["yamlvd"]
if (not os.path.exists(root.yamlvd)):
    root.yamlvd = ""
if (root.yamlvd == ""):
    print("no yamlvd")
    SetYamlvd()

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
config.set("DEFAULT","yamlvd",root.yamlvd)
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

tree = None
treeRoot = None
root.steveSideName = "cell_minlen_side"
root.steveTopName = "cell_minlen_top"
root.steveBottomName = "cell_minlen_bottom"
root.steveSideValue = 0
root.steveTopValue = 0
root.steveBottomValue = 0


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

                if (childName == "cell_minilen_side"):
                    root.steveSideValue = float(child.text)
                elif (childName == "cell_minilen_top"):
                    root.steveTopValue = float(child.text)
                elif (childName == "cell_minilen_bottom"):
                    root.steveBottomValue = float(child.text)
    tree.write(root.TempGroundInfo)


def exportGroundInfoLazy():
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    shutil.copy(root.TempGroundInfo,targetLocation + r"\groundconfig.prcxml")
    messagebox.showinfo(root.title(),"Exported Info to "+root.stageName)
    webbrowser.open(targetLocation)

def exportGroundInfo():
    #Part one of parcel: patch the original file with our edited values
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    os.makedirs(targetLocation)
    tempPrc = os.getcwd() +"/temp.prc"
    sourcePrc = root.stageParams + "/groundconfig.prc"
    parcel = root.parcelDir + r"/parcel.exe"

    subcall = [parcel,"patch",sourcePrc,root.TempGroundInfo,tempPrc]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)
    print("Temp prc created!")

    #Part two: patch our working folder, as well
    workingPrc = os.getcwd() + "/groundconfig.prc"
    subcall = [parcel,"patch",workingPrc,root.TempGroundInfo,workingPrc]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)

    print("Working prc patched!")
    #Part three: run parcel with the original and the patch to receive a prcx

    subcall = [parcel,"diff",sourcePrc,tempPrc,targetLocation+"groundconfig.prcx"]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)

    print("Prcx created!")

    #Part four: copy the temp prcxml to the destination
    os.remove(tempPrc)
    shutil.copy(root.TempGroundInfo,targetLocation + r"groundconfig.prcxml")
    messagebox.showinfo(root.title(),"Exported groundconfig info to "+root.stageName)
    webbrowser.open(targetLocation)

root.cameraLeftValue=-190
root.cameraRightValue=190
root.cameraTopValue=145
root.cameraBottomValue=-60
root.blastLeftValue=-190
root.blastRightValue=190
root.blastTopValue=145
root.blastBottomValue=-60
root.stageRadius=80
root.collisions=[]

root.yamlFile = ""
root.yamlDir = root.modDir + "/stage/"+root.stageName+"/normal/param/"
root.popup = None
root.popupOptions = {}

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

import fileinput

def FinishedCreateYaml():
    #create yaml by copying our sample
    root.yamlFile = root.yamlDir+"/"+root.stageName+".yaml"
    shutil.copy(os.getcwd() + "/sample.yaml", root.yamlFile)

    # Replace all tagged values
    with open(root.yamlFile, 'r') as file :
        filedata = file.read()

    for option in root.popupOptions:
        filedata = filedata.replace(option, root.popupOptions[option].get())

    filedata = filedata.replace("RadiusL", "-"+root.popupOptions["StageRadius"].get())
    filedata = filedata.replace("RadiusR", root.popupOptions["StageRadius"].get())

    # Write to the copy
    with open(root.yamlFile, 'w') as file:
        file.write(filedata)

    #Destroy popup, and return to main
    root.popup.destroy()
    Main()

def CreateYaml():
    if (not os.path.isdir(root.yamlDir)):   
        messagebox.showinfo(root.title(),"Set directory to save yaml to")
        root.yamlDir = filedialog.askdirectory(title = "Select your yaml directory")
        if (root.yamlDir == ""):
            root.destroy()
            sys.exit("Invalid folder")

    root.popup = Toplevel()
    root.popup.title("Create Yaml")

    label = Label(root.popup,text="Enter Values")
    label.pack(fill = X,expand=1)

    root.fr_Options = Frame(root.popup)
    root.fr_Options.pack(fill = BOTH,expand=1,anchor=N)
    root.popupOptions = {}
    stageOptions = {"CameraLeft":root.cameraLeftValue,"CameraRight":root.cameraRightValue,
    "CameraTop":root.cameraTopValue,"CameraBottom":root.cameraBottomValue,
    "BlastLeft":root.blastLeftValue,"BlastRight":root.blastRightValue,
    "BlastTop":root.blastTopValue,"BlastBottom":root.blastBottomValue,
    "StageRadius":root.stageRadius}
    for option in stageOptions:
        optionData = stageOptions[option]
        optionFrame = Frame(root.fr_Options)
        optionFrame.pack(fill = X,expand=1)
        optionName = Entry(optionFrame,width=15)
        optionName.insert(0,option)
        optionName.configure(state ='disabled')
        optionName.pack(side = LEFT, fill = BOTH,anchor=E)
        optionValue = Entry(optionFrame,width=15)
        optionValue.insert(0,optionData)
        optionValue.pack(side = RIGHT, fill = BOTH,expand=1)
        root.popupOptions.update({option:optionValue})

    button = Button(root.popup, text="Create Yaml", command=FinishedCreateYaml,width = 10).pack(side=BOTTOM)
    root.popup.protocol("WM_DELETE_WINDOW", FinishedCreateYaml)
    root.withdraw();

def SetYaml():
    #Attempt to find automatically first, if valid directory file exists
    if (os.path.isdir(root.yamlDir)):
        if (root.yamlFile == ""):
            paramfiles = [f for f in listdir(root.yamlDir) if os.path.exists(os.path.join(root.yamlDir, f))]
            root.yamlFile = ""
            root.yaml = {}
            for f in list(paramfiles):
                extension = os.path.splitext(os.path.basename(f))[1]
                if (extension == ".yaml"):
                    root.yamlFile = root.yamlDir + "/"+f
                    break
    if (root.yamlFile == ""):
        #SetYaml manually
        messagebox.showinfo(root.title(),"Select your yaml or lvd file for your mod's stage")
        filetypes = (
            ('All File Types', '*.yaml *lvd'),
            ('Yaml File', '*.yaml'),
            ('LVD File', '*lvd')
        )
        desiredFile = filedialog.askopenfilename(title = "Search",filetypes=filetypes,initialdir = root.modDir)
        if (desiredFile == ""):
            #enter manually
            messagebox.showwarning(root.title(),"Let's manually create a yaml file then!")
            CreateYaml()
            return
        extension = os.path.splitext(os.path.basename(desiredFile))[1]
        #If it's a yaml file, we did it!
        if (extension == ".yaml"):
            root.yamlFile = desiredFile
        #else yamlvd it
        elif (extension == ".lvd"):
            print("yamlvd")
            root.yamlFile = desiredFile.replace(".lvd",".yaml")
            subcall = [root.yamlvd,desiredFile,root.yamlFile]
            with open('output.txt', 'a+') as stdout_file:
                process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
                print(process_output.__dict__)
            if (not os.path.exists(root.yamlFile)):
                #enter manually
                messagebox.showwarning(root.title(),"Yamlvd not compatible with this stage! Let's create a yaml file!")
                CreateYaml()
                return
    Main()


def Main():
    print(root.yamlFile)
    with open(root.yamlFile, "r") as stream:
        try:
            root.yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for i in root.yaml:
        #print(i)
        #Get Camera Info
        if (i=="camera"):
            root.cameraLeftValue = float(root.yaml[i][0]["left"])
            root.cameraRightValue = float(root.yaml[i][0]["right"])
            root.cameraTopValue = float(root.yaml[i][0]["top"])
            root.cameraBottomValue = float(root.yaml[i][0]["bottom"])
        #get boundary Info
        elif (i=="blastzones"):
            print(root.yaml[i])
            print(root.yaml[i][0])
            root.blastLeftValue = float(root.yaml[i][0]["left"])
            root.blastRightValue = float(root.yaml[i][0]["right"])
            root.blastTopValue = float(root.yaml[i][0]["top"])
            root.blastBottomValue = float(root.yaml[i][0]["bottom"])
        #get collision Info
        elif (i=="collisions"):
            for c in root.yaml[i]:
                #print(c)
                #print(c["verts"])
                if (len(root.collisions)<5):
                    root.collisions.append(c["verts"])

    #exportGroundInfo()
    #root.destroy()
    #sys.exit("cool!")


    root.geometry("720x512")
    root.deiconify()
    root.canvasWidth = 640
    root.canvasHeight = 480 #240
    my_canvas = Canvas(root,width=root.canvasWidth,height=root.canvasHeight,bg="white")
    my_canvas.pack(pady=20)
    root.steveArea = my_canvas.create_rectangle(-10,-10,-10,-10,fill = "green",tag="steve")
    root.cameraArea = my_canvas.create_rectangle(-10,-10,-10,-10,outline = "blue",tag="camera")
    root.blastArea = my_canvas.create_rectangle(-10,-10,-10,-10,outline = "red",tag = "blast")

    def GetAdjustedCoordinates(x1=0,y1=0,x2=0,y2=0):
        xC = root.canvasWidth/2
        yC = root.canvasHeight/2
        x1=x1+xC
        y1=(-y1)+yC
        x2=x2+xC
        y2=(-y2)+yC
        return x1,y1,x2,y2

    def DrawSteveBlock():
        xC = root.canvasWidth/2
        yC = root.canvasHeight/2
        x1 = root.cameraLeftValue+root.steveSideValue
        x2 = root.cameraRightValue-root.steveSideValue
        y1 = root.cameraTopValue-root.steveTopValue
        y2 = root.cameraBottomValue+root.steveBottomValue
        x1,y1,x2,y2 = GetAdjustedCoordinates(x1,y1,x2,y2)
        my_canvas.coords(root.steveArea,x1,y1,x2,y2)
    def DrawBoundaries():
        x1,y1,x2,y2 = GetAdjustedCoordinates(root.cameraLeftValue,root.cameraTopValue,root.cameraRightValue,root.cameraBottomValue)
        my_canvas.coords(root.cameraArea,x1,y1,x2,y2)
        x1,y1,x2,y2 = GetAdjustedCoordinates(root.blastLeftValue,root.blastTopValue,root.blastRightValue,root.blastBottomValue)
        my_canvas.coords(root.blastArea,x1,y1,x2,y2)

    def DrawCollisions():
        for c in root.collisions:
            for vert in range(len(c)-1):
                x1=float(c[vert]["x"])
                y1=float(c[vert]["y"])
                x2=float(c[vert+1]["x"])
                y2=float(c[vert+1]["y"])
                x1,y1,x2,y2 = GetAdjustedCoordinates(x1,y1,x2,y2)
                my_canvas.create_line(x1,y1,x2,y2, fill = "black")

    print(root.blastRightValue)
    DrawSteveBlock()
    DrawBoundaries()
    DrawCollisions()


SetYaml()

root.mainloop()
