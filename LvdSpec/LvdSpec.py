import os
import os.path
from os import listdir
from pathlib import Path

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import fileinput

import shutil
import subprocess
import sys
import webbrowser

import xml.etree.ElementTree as ET
import yaml
import configparser

import re
import math

#create ui for program
root = Tk()
root.programName="LVD Spec"
root.title(root.programName)
root.iconbitmap(os.getcwd() +"/icon.ico")
root.withdraw()

# Check if yaml is installed
package_name = 'yaml'

import importlib.util
spec = importlib.util.find_spec(package_name)
if spec is None:
    print(package_name +" is not installed")
    #subcall = ["pip install"+package_name]
    #with open('output.txt', 'w+') as stdout_file:
    #    process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
    #    print(process_output.__dict__)
    #spec = importlib.util.find_spec(package_name)
    #if spec is None:
    messagebox.showerror(root.programName,"Please install "+package_name+" to use this program!")
    root.destroy()
    sys.exit("User does not have "+package_name)



#truncate strings for labels
def truncate(string,direciton=W,limit=20,ellipsis=True):
    if (len(string) < 3):
        return string
    text = ""
    addEllipsis = "..." if (ellipsis and (len(string)>limit)) else ""
    if direciton == W:
        text = addEllipsis+string[len(string)-limit:len(string)]
    else:
        text = string[0:limit]+addEllipsis
    return text
#Why isn't this built in?
def clamp(val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val



config = configparser.ConfigParser()
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'parcelDir' : "",
    'arcDir' : "",
    'yamlvd' : "",
    'stageParamsLocation' : "",
    'levelFile' : ""
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


def UpdateTitle(newtitle=""):
    if (newtitle!=""):
        newtitle = " - "+newtitle
    root.title(root.programName+newtitle)

root.arcDir = config["DEFAULT"]["arcDir"]
root.stageParamsFolderShortcut = r"/stage/common/shared/param/"

#make sure that it is a validated parcel folder, otherwise quit
def IsValidParcel():
    #Is this the directory with Parcel.exe?
    return (os.path.exists(root.parcelDir + r"/parcel.exe"))

def SetParcel():
    messagebox.showinfo(root.programName,"Set Parcel directory")
    root.parcelDir = filedialog.askdirectory(title = "Select your Parcel directory")
    if (root.parcelDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidParcel() == False):
        messagebox.showerror(root.programName,"Please select the root of your Parcel folder")
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
            messagebox.showerror(root.programName,"Please extra the folder stage/common/shared/param")
            root.destroy()
            sys.exit("Needs Param Folder")
    return False

#Get Stage Params folder from Valid Arc
def SetStageParams():
    #First, check to see if ArcExplorer Exists
    messagebox.showinfo(root.programName,"Set ArcExplorer directory")
    root.arcDir = filedialog.askdirectory(title = "Select your ArcExplorer directory")
    if (root.arcDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidArc() == False):
        messagebox.showerror(root.programName,"Please select the root of your ArcExplorer folder")
        root.destroy()
        sys.exit("Invalid Folder")

    root.stageParams = root.arcDir + r"/export"+ root.stageParamsFolderShortcut
    #Copy em for our working file
    shutil.copy(root.stageParams + "groundconfig.prc", os.getcwd()+"/groundconfig.prc")

def SetYamlvd():
    messagebox.showinfo(root.programName,"Set Yamlvd directory")
    root.yamlvd = filedialog.askdirectory(title = "Select your Yamlvd directory")
    if (root.yamlvd == ""):
        root.destroy()
        sys.exit("Invalid folder")
    root.yamlvd = root.yamlvd + r"/yamlvd.exe"
    if (os.path.exists(root.yamlvd) == False):
        messagebox.showerror(root.programName,"Please select the root of your Yamlvd folder")
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
def setModDir(quitOnFail=True):
    quitOnFail=False
    messagebox.showinfo(root.programName,"Select your mod's main folder")
    root.modDir = filedialog.askdirectory(title = "Select your mod's main folder")
    if (root.modDir == ""):
        if (quitOnFail):
            root.destroy()
            sys.exit("Invalid folder")
        return
    if (IsValidModFolder() == False):
        root.modDir=""
        messagebox.showerror(root.programName,"Please select the root of your mod's folder! This folder should contain a stage folder within it!")
        if (quitOnFail):
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

config.set("DEFAULT","parcelDir",root.parcelDir)
config.set("DEFAULT","arcDir",root.arcDir)
config.set("DEFAULT","stageParamsLocation",root.stageParams)
with open('config.ini', 'w+') as configfile:
    config.write(configfile)

root.stageName = ""
root.steveSideValue = 0
root.steveTopValue = 0
root.steveBottomValue = 0
root.steveOrginX=0
root.steveOrginY=0
root.steveSensitivity=0
root.steveOffset=0
root.steveMaterial="soil"
root.steveTable={
    "Steve_Label":"Steve LVD Settings",
    "Steve_material":root.steveMaterial,
    "Steve_origin_x":root.steveOrginX,
    "Steve_origin_y":root.steveOrginY,
    "Steve_cell_sensitivity":root.steveSensitivity,
    "Steve_line_offset":root.steveOffset,
    "Steve_cell_minilen_side":0,
    "Steve_cell_minilen_top":0,
    "Steve_cell_minilen_bottom":0
}
root.steveMaterials=[
"soil",
"wool",
"sand",
"ice",
]

#GetData("Camera_Left")=-170
#GetData("Camera_Right")=170
#GetData("Camera_Top")=130
#GetData("Camera_Bottom")=-80
#GetData("Blast_Left")=-240
#GetData("Blast_Right")=240
#GetData("Blast_Top")=192
#GetData("Blast_Bottom")=-140
#GetData("Stage_Radius")=80
#GetData("Stage_BaseY")=0
#GetData("Stage_OriginX")=0
#GetData("Stage_OriginY")=0
#GetData("Stage_Top")=47.3
#GetData("Stage_Bottom")=-40
root.collisions=[]
root.maxCollisionsTag="Collisions To Show"
root.maxCollisions=50
root.stageLimit=125


root.stageDataTable = {
"Camera_Label":"Camera Boundaries",
"Camera_Left":-170,
"Camera_Right":170,
"Camera_Top":130,
"Camera_Bottom":-80,
"Blast_Label":"Blastzone Boundaries",
"Blast_Left":-240,
"Blast_Right":240,
"Blast_Top":192,
"Blast_Bottom":-140,
"Stage_Label":"Stage Data",
"Stage_Radius":80,
"Stage_Top":47,
"Stage_Bottom":-40,
"Stage_BaseY":0,
"Stage_OriginX":0,
"Stage_OriginY":0,
"Canvas_Label":"Canvas Settings",
"Canvas_"+root.maxCollisionsTag:root.maxCollisions
}
def GetData(data):
    return root.stageDataTable[data]

root.levelFile = ""
root.modParams = ""
root.popup = None
root.popupOptions = {}
root.FirstLoad=True
root.Loading=True

#Deprecated
def SetStageFromRoot():
    print("Open Stage from root:"+root.modDir)

    if (root.modDir==""):
        SetYaml(False)
        return
    SetStage(root.modDir+ "/stage/")

def SetStageFromLVD():
    stageKey="/stage/"
    normalKey="/normal/"
    #We need to find whatever is in between stageKey and normalKey
    stageLocation = root.levelFile[:root.levelFile.index(normalKey)]
    root.stageName = stageLocation[stageLocation.index(stageKey)+len(stageKey):]
    print("Stage:"+root.stageName)
    if (root.stageName == ""):
        messagebox.showerror(root.programName,"There is no valid stage within that stage folder!")
        return
    root.modParams = stageLocation+"/normal/param/"
    print("Stage Loaded, stage params should be at "+root.modParams)


def SetStage(stageDir):
    print("Find stage at "+stageDir)
    root.stageName = None
    subfolders = [s.path for s in os.scandir(stageDir) if s.is_dir()]
    for dirname in list(subfolders):
        if (dirname != "common"):
            root.stageName = os.path.basename(dirname)
    if (root.stageName == None):
        messagebox.showerror(root.programName,"There is no valid stage within that stage folder!")
        return
        #root.destroy()
        #sys.exit("Not a stage folder")




def FinishedCreateYaml():
    #create yaml by copying our sample
    #root.levelFile = root.modParams+root.stageName+"_spec.yaml"
    shutil.copy(os.getcwd() + "/sample.yaml", root.levelFile)

    # Replace all tagged values
    with open(root.levelFile, 'r') as file :
        filedata = file.read()

    for option in root.popupOptions:
        filedata = filedata.replace(option, root.popupOptions[option].get())

    filedata = filedata.replace("RingL", "-"+root.popupOptions["StageRadius"].get())
    filedata = filedata.replace("RingR", root.popupOptions["StageRadius"].get())

    # Write to the copy
    with open(root.levelFile, 'w') as file:
        file.write(filedata)

    #Destroy popup, and return to main
    root.popup.destroy()
    root.deiconify()
    LoadYaml()

def ClosedCreateYaml():
    root.levelFile=""
    root.popup.destroy()
    root.deiconify()
    LoadYaml()

def CreateYaml():
    print(root.levelFile)
    if (root.levelFile==""):   
        messagebox.showinfo(root.programName,"Set directory to save yaml to")
        root.modParams = filedialog.askdirectory(title = "Select your yaml directory")
        if (root.modParams == ""):
            return
        root.levelFile = root.modParams
        SetStageFromLVD()
        print("Create Stage:"+root.stageName)
        root.levelFile=root.modParams+root.stageName+"_spec.yaml"

    root.popup = Toplevel()
    root.popup.title("Create Yaml")

    root.fr_Options = Frame(root.popup)
    root.fr_Options.pack(fill = BOTH,expand=1,anchor=N)
    root.popupOptions = {}
    stageOptions = {
    "Label1":"Camera Settings",
    "CameraLeft":GetData("Camera_Left"),"CameraRight":GetData("Camera_Right"),
    "CameraTop":GetData("Camera_Top"),"CameraBottom":GetData("Camera_Bottom"),
    "Label2":"Blastzone Settings",
    "BlastLeft":GetData("Blast_Left"),"BlastRight":GetData("Blast_Right"),
    "BlastTop":GetData("Blast_Top"),"BlastBottom":GetData("Blast_Bottom"),
    "Label3":"Stage Settings",
    "StageRadius":GetData("Stage_Radius"),"StageBaseY":GetData("Stage_BaseY"),
    "StageTop":GetData("Stage_Top"),"StageBottom":GetData("Stage_Bottom")}
    for option in stageOptions:
        if ("Label" in option):
            optionFrame = Frame(root.fr_Options)
            optionFrame.pack(fill = X,expand=1)
            optionName = Label(optionFrame,text=stageOptions[option])
            optionName.pack(fill = BOTH)
            continue
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
    root.popup.protocol("WM_DELETE_WINDOW", ClosedCreateYaml)
    root.withdraw();

def LoadLastYaml():
    root.levelFile = config["DEFAULT"]["levelFile"]
    if (not os.path.exists(root.levelFile)):
        root.levelFile = ""
    else:
        SetStageFromLVD()
    Main()

def SetYaml(automatic=False):
    originalYaml = root.levelFile
    root.levelFile=""
    #Attempt to find automatically first, if valid directory file exists
    if (automatic and os.path.isdir(root.modParams)):
        if (root.levelFile == ""):
            #Automatically comb through modParams to find the first yaml file
            paramfiles = [f for f in listdir(root.modParams) if os.path.exists(os.path.join(root.modParams, f))]
            root.yaml = {}
            for f in list(paramfiles):
                filename = os.path.splitext(os.path.basename(f))[0]
                extension = os.path.splitext(os.path.basename(f))[1]
                if (extension == ".yaml"):
                    #if (root.stageName in filename): #this checks if the filename contains the stage name, which might not always be the case
                    root.levelFile = root.modParams +f
                    break

    if (root.levelFile != ""):
        print(os.path.basename(root.levelFile)+" was automatically retrieved")
    elif (root.levelFile == "" or not automatic):
        #SetYaml manually. First select an lvd/yaml file
        #messagebox.showinfo(root.programName,"Select your stage collision file (usually found in stage/normal/params)")        
        filetypes = (
            ('All File Types', '*.yaml *lvd'),
            ('Yaml File', '*.yaml'),
            ('LVD File', '*lvd')
        )
        desiredFile = filedialog.askopenfilename(title = "Search",filetypes=filetypes,initialdir = root.modParams)

        if (desiredFile == ""):
            print("No lvd selected")
            #enter manually if rejected, and no current file
            if (root.levelFile == "" and originalYaml==""):
                messagebox.showwarning(root.programName,"Let's manually create a yaml file then!")
                CreateYaml()
            #otherwise close window?
            else:
                root.levelFile=originalYaml
            return

        #If it's the same file, do nothing
        if (desiredFile == originalYaml):
            return

        desiredFileName = os.path.basename(desiredFile)
        extension = os.path.splitext(desiredFileName)[1]

        #If it's a yaml file, continue to the main program
        if (extension == ".yaml"):
            root.levelFile = desiredFile
        #else yamlvd it
        elif (extension == ".lvd"):
            print("Use yamlvd")

            #Get or Set Yamlvd
            root.yamlvd = config["DEFAULT"]["yamlvd"]
            if (not os.path.exists(root.yamlvd)):
                root.yamlvd = ""
            if (root.yamlvd == ""):
                print("no yamlvd")
                SetYamlvd()
            config.set("DEFAULT","yamlvd",root.yamlvd)
            with open('config.ini', 'w+') as configfile:
                    config.write(configfile)

            #run yamlvd on the lvd file
            root.levelFile = desiredFile.replace(".lvd",".yaml")
            subcall = [root.yamlvd,desiredFile,root.levelFile]
            with open('output.txt', 'a+') as stdout_file:
                process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
                print(process_output.__dict__)
            #if yamlvd doesn't work with this stage, enter values manually
            if (not os.path.exists(root.levelFile)):
                #enter manually
                messagebox.showwarning(root.programName,"Yamlvd not compatible with this stage! Let's create a yaml file!")
                CreateYaml()
                return
        LoadYaml()

def LoadYaml():
    root.Loading=True
    root.collisions=[]
    print("")
    print("Loaded New Yaml")
    if (root.levelFile != ""):
        SetStageFromLVD() 

        config.set("DEFAULT","levelFile",root.levelFile)
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)
    Main() 

def ParseSteve():
    root.steveSideValue = 0
    root.steveTopValue = 0
    root.steveBottomValue = 0
    if (root.stageName == ""):
        return

    defaultGroundInfo = os.getcwd() + r"\groundconfig.prcxml"
    root.TempGroundInfo = os.getcwd() + r"\tempconfig.prcxml"
    f = open(root.TempGroundInfo, "w")
    f.close()
    #root.TempGroundInfo = shutil.copy(defaultGroundInfo,os.getcwd() + r"\tempconfig.prcxml")

    tree = None
    treeRoot = None

    print("Parsing Steve Data...")
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
                for child in type_tag:
                    childName = "Steve_"+child.get("hash")
                    if (childName in list(root.steveTable.keys())):
                        print(childName+":"+child.text)
                        if (childName!="Steve_material"):
                            root.steveTable.update({childName:float(child.text)})
                        else:
                            root.steveTable.update({childName:child.text})
        tree.write(root.TempGroundInfo)
    print("")

def exportGroundInfoLazy():
    #Shit
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    shutil.copy(root.TempGroundInfo,targetLocation + r"\groundconfig.prcxml")
    messagebox.showinfo(root.programName,"Exported Info to "+root.stageName)
    webbrowser.open(targetLocation)

def exportGroundInfo():
    #shit
    #Part one of parcel: patch the original file with our edited values
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    if (not os.path.exists(targetLocation)):
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
    messagebox.showinfo(root.programName,"Exported groundconfig info to "+root.stageName)
    webbrowser.open(targetLocation)


def OpenReadMe():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/tree/main/LvdSpec')
def OpenWiki():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/wiki')

root.string_vars = {}

reAlpha='[^0-9,.]-'
def OnSteveSettingUpdated(*args):
    if (root.Loading):
        return
    variable = "Steve_"+args[0]
    #remove letters from string
    value = root.string_vars[variable].get()
    nums = re.findall(r'\d+',value)
    if (len(nums)==0): return #if there are no numbers, return
    value = re.sub(reAlpha, '', value)

    value=float(value)
    print("Updated "+variable+" with "+str(value))
    root.steveTable.update({variable:value})
    DrawSteveBlock()

def OnSteveSliderUpdate(variable):
    if (root.Loading):
        return
    value = root.stageData[variable].get()
    value=float(value)
    print("Updated "+variable+" with "+str(value))
    root.steveTable.update({variable:value})
    #DrawSteveBlock()

def OnOriginXSliderUpdate(event):
    variable = "Steve_origin_x"
    OnSteveSliderUpdate(variable)
def OnOriginYSliderUpdate(event):
    variable = "Steve_origin_y"
    OnSteveSliderUpdate(variable)
def OnLineSliderUpdate(event):
    variable = "Steve_line_offset"
    OnSteveSliderUpdate(variable)
def OnSensitivitySliderUpdate(event):
    variable = "Steve_cell_sensitivity"
    OnSteveSliderUpdate(variable)


def OnStageSettingUpdated(*args):
    if (root.Loading):
        return
    variable = "Stage_"+args[0]
    #remove letters from string
    value = root.string_vars[variable].get()
    nums = re.findall(r'\d+',value)
    if (len(nums)==0): return #if there are no numbers, return
    value = re.sub(reAlpha, '', value)

    value=float(value)
    #Clamp Radius
    if ("Radius" in variable):
        min(value,root.stageLimit)
    elif ("Origin" in variable):
        clamp(value,-10,10)

    print("Updated "+variable+" with "+str(value))
    root.stageDataTable.update({variable:value})
    DrawSteveBlock()

def OnCanvasSettingUpdated(*args):
    if (root.Loading):
        return
    variable = "Canvas_"+args[0]
    #remove letters from string
    value = root.string_vars[variable].get()
    nums = re.findall(r'\d+',value)
    if (len(nums)==0): return #if there are no numbers, return
    value = re.sub(reAlpha, '', value)
    if (variable=="Canvas_"+root.maxCollisionsTag and value != ""):
        root.maxCollisions=int(value)
        print("Updated "+variable+" with "+str(value))
        DrawCollisions()



root.canvasWidth = 576
root.canvasHeight = 480 
#This should really only run once, maybe I should split this up but idk
def CreateCanvas():
    #Define window stuff
    root.geometry("1080x512")
    root.deiconify()
    root.mainFrame = Frame(root)
    root.mainFrame.pack(fill = X,expand=1)
    root.my_canvas = Canvas(root.mainFrame,width=root.canvasWidth,height=root.canvasHeight,bg="white")
    root.my_canvas.pack(padx=20,pady=20,side=LEFT)
    #Rectangle variables for later
    root.steveArea = root.my_canvas.create_rectangle(-10,-10,-10,-10,fill = "lime green",tag="steve")
    root.cameraArea = root.my_canvas.create_rectangle(-10,-10,-10,-10,outline = "blue",tag="camera")
    root.blastArea = root.my_canvas.create_rectangle(-10,-10,-10,-10,outline = "red",tag = "blast")

    #File menu
    root.menubar = Menu(root)
    root.filemenu = Menu(root.menubar, tearoff=0)
    root.filemenu.add_command(label="Load Stage Collision File", command=SetYaml)
    root.filemenu.add_command(label="Export Patch File To Mod", command=exportGroundInfo)
    root.filemenu.add_separator()
    root.filemenu.add_command(label="Exit", command=quit)
    root.menubar.add_cascade(label="File", menu=root.filemenu)

    root.helpmenu = Menu(root.menubar, tearoff=0)
    root.helpmenu.add_command(label="About", command=OpenReadMe)
    root.helpmenu.add_command(label="Wiki", command=OpenWiki)
    #root.helpmenu.add_command(label="About...", command=donothing)
    root.menubar.add_cascade(label="Help", menu=root.helpmenu)
    root.config(menu=root.menubar)

    #Settings displayed on the side,
    root.fr_Settings = Frame(root.mainFrame)
    root.fr_Settings.pack(pady=20,expand=1,fill=BOTH,side=RIGHT)
    root.fr_SteveSettings = Frame(root.fr_Settings)
    root.fr_SteveSettings.pack(padx=10,side=LEFT,anchor=N)
    root.fr_StageSettings = Frame(root.fr_Settings)
    root.fr_StageSettings.pack(padx=10,side=LEFT,anchor=N)

    root.stageData = {}
    dataTable = {}
    dataTable.update(root.steveTable)
    dataTable.update(root.stageDataTable)
    for data in dataTable:
        frame = root.fr_StageSettings
        if ("Steve" in data):
            frame = root.fr_SteveSettings
        #For labels, don't use Entries
        if ("Label" in data):
            dataFrame = Frame(frame)
            dataFrame.pack(fill = X,expand=1)
            dataName = Label(dataFrame,text=dataTable[data])
            dataName.pack(fill = BOTH)
            continue

        dataText=re.sub(r'[^a-zA-Z _]', '', data)
        dataText=dataText[dataText.index("_")+1:]
        dataDefault = truncate(str(dataTable[data]),E,6)

        dataFrame = Frame(frame)
        dataFrame.pack(fill = X,expand=1)

        dataName = Entry(dataFrame)
        dataName.insert(0,dataText)
        dataName.configure(state ='disabled')
        dataName.pack(side = LEFT, fill = BOTH,anchor=E)
        dataEntry=None
        #For Steve Entries, trace any updates
        if ("Steve" in data or "Stage" in data or "Canvas" in data):
            #Sensitivity is a slider
            if ("sensitivity" in data):
                dataEntry = Scale(dataFrame, from_=0, to=1,orient=HORIZONTAL,resolution=0.01)
                dataEntry.bind("<ButtonRelease-1>",OnSensitivitySliderUpdate)
                dataEntry.set(dataDefault)
            elif ("line" in data):
                dataEntry = Scale(dataFrame, from_=0, to=10,orient=HORIZONTAL,resolution=0.01)
                dataEntry.bind("<ButtonRelease-1>",OnLineSliderUpdate)
                dataEntry.set(dataDefault)
            #Origin is now using textEntry
            elif ("Xorigin" in data):
                dataEntry = Scale(dataFrame, from_=-10, to=10,orient=HORIZONTAL,resolution=0.01)
                dataEntry.set(dataDefault)
                if ("_x" in data):
                    dataEntry.bind("<ButtonRelease-1>",OnOriginXSliderUpdate)
                elif ("_y" in data):
                    dataEntry.bind("<ButtonRelease-1>",OnOriginYSliderUpdate)
            else:
                root.string_vars.update({data:StringVar(name=dataText)})
                var = root.string_vars[data]
                if ("Steve" in data):
                    var.trace_add("write",OnSteveSettingUpdated)
                elif ("Stage" in data):
                    var.trace_add("write",OnStageSettingUpdated)
                else:
                    var.trace_add("write",OnCanvasSettingUpdated)

                dataEntry = Entry(dataFrame,textvariable=var)
                dataEntry.insert(0,dataDefault)

                #Material is uneditable
                if ("material" in data):
                    dataEntry.configure(state ='disabled')
        #Disable non-editable categories
        else:
            dataEntry = Entry(dataFrame)
            dataEntry.insert(0,dataDefault)
            dataEntry.configure(state ='disabled')
        dataEntry.pack(side = RIGHT, fill = BOTH,expand=1)
        root.stageData.update({data:dataEntry})

    #Wizard Button
    button = Button(root.fr_SteveSettings, text="Wizard", command=OnWizard)
    button.pack(side = RIGHT, fill = BOTH,expand=1,pady=10,padx=4)

def OnWizard():
    res = messagebox.askquestion("LVD Wizard: "+os.path.basename(root.levelFile), "Make sure you have all these variables set in Stage Data for this to work!"
        "\n"
        "\nRadius (Radius of the main ring)"
        "\nTop (Y Position of highest platform)"
        "\nBase (Y Position of baseline on the main ring, should be a spawn point's y)"
        "\nBottom (Y Position of lowest point on the main ring)"
        "\nOrigin (A multiple of 50 that is as close to 0,0 as possible. For stages that have been shifted up/left, this could be 0,200 for a highup stage, or 100,0 for a stage that's far to the right)"
        "\n"
        "\nReady to start Wizard?")
    if res != 'yes':
        return
    isWall= (GetData("Stage_Bottom")<GetData("Camera_Bottom")+5)
    print(isWall)
    #BF (plankable)
    #Side: Steve40,Cam170
    #Bottom: Steve30,Cam-80
    #Top: Steve60,Cam130,Stage47
    #BottomStage: 40
    #Radius: 80 (90 or 2.125)

    #FD (plankable)
    #Side: Steve50,Cam180
    #Bottom: Steve10,Cam-60
    #Top: Steve70,Cam130,Stage0
    #BottomStage: 40
    #Radius: 80 (100 or 2.25)

    #Kalos (wall)
    #Side: Steve35,Cam165
    #Bottom: Steve10,Cam-60
    #Top: Steve70,Cam130,Stage30
    #BottomStage: -inf
    #Radius: 80 (85 or 2.062)

    #T&C (good)
    #Side: Steve28,Cam160
    #Bottom: Steve40,Cam-75
    #BottomStage: -23.5
    #Radius: 83 (77 or 1.927)

    #SteveTop could be CamTop-StageTop/2
    #SteveSide seems to be (CamSide-Radius)/2 where Radius is shifted by OriginX
    #SteveBottom seems to be CamBottom-StageBase
    desiredBottom = GetData("Camera_Bottom")-GetData("Stage_Bottom")+20
    if (isWall):
        stageMiddle=abs(GetData("Stage_OriginY")-GetData("Camera_Bottom"))/2
        desiredBottom=stageMiddle-10
    desiredBottom=abs(round(desiredBottom))
    desiredSide = (GetData("Camera_Right")-(GetData("Stage_Radius")+GetData("Stage_OriginX")))/2
    desiredSide=math.floor(desiredSide-5)
    desiredTop=math.floor((GetData("Camera_Top")-GetData("Stage_Top"))/2)

    #Origin should do something with radius, maybe?
    stageCenter = (GetData("Camera_Left")+GetData("Camera_Right"))/2
    desiredOriginX= stageCenter % 10
    desiredOriginY=GetData("Stage_BaseY") % 10
    print(str((desiredOriginX)))



#Load info from yaml into our canvas
def ParseYaml():
    if (root.levelFile!=""):
        print("Parsing yaml:"+root.levelFile)
        with open(root.levelFile, "r") as stream:
            try:
                root.yaml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                root.destroy()
                sys.exit("Yaml exploded")

        root.collisions=[]
        spawns=[]
        for i in root.yaml:
            #print(i)
            #Get Camera Info
            if (i=="camera"):
                cameraLeftValue = float(root.yaml[i][0]["left"])
                cameraRightValue = float(root.yaml[i][0]["right"])
                cameraTopValue = float(root.yaml[i][0]["top"])
                cameraBottomValue = float(root.yaml[i][0]["bottom"])
            #get boundary Info
            elif (i=="blastzones"):
                blastLeftValue = float(root.yaml[i][0]["left"])
                blastRightValue = float(root.yaml[i][0]["right"])
                blastTopValue = float(root.yaml[i][0]["top"])
                blastBottomValue = float(root.yaml[i][0]["bottom"])
            #get collision Info
            elif (i=="collisions"):
                for c in root.yaml[i]:
                    root.collisions.append(c["verts"])
            #get spawn
            elif (i=="spawns"):
                for s in root.yaml[i]:
                    pos_y = s["pos"]["y"]
                    spawns.append(float(pos_y))
        #Parse stage data
        largestX=0
        originX=(cameraLeftValue+cameraRightValue)/2
        originY=(cameraTopValue+cameraBottomValue)/2
        highestY=-10 if (len(spawns)>0) else originY
        lowestY=0
        baseY=-900 
        for s in spawns:
            if (s>highestY):
                highestY=s

        for c in root.collisions:
            for vert in range(len(c)-1):
                x1=float(c[vert]["x"])
                y1=float(c[vert]["y"])
                #Make sure largestX is in between camera boundaries
                if (x1>largestX and cameraLeftValue<x1 and x1<cameraRightValue):
                    largestX=x1
                    if (y1>baseY):
                        sign =math.copysign(1, y1)
                        baseY=sign*math.floor(abs(y1))
                elif (y1<lowestY):
                    lowestY=y1
        stageRadius=min(largestX,root.stageLimit)
        stageBaseY= baseY
        stageOriginX= math.floor(originX/100)*100
        stageOriginY= math.floor(originY/100)*100
        stageTop=highestY
        stageBottom=lowestY

    stageDataTableUpdates={
    "Camera_Left":cameraLeftValue,
    "Camera_Right":cameraRightValue,
    "Camera_Top":cameraTopValue,
    "Camera_Bottom":cameraBottomValue,
    "Blast_Left":blastLeftValue,
    "Blast_Right":blastRightValue,
    "Blast_Top":blastTopValue,
    "Blast_Bottom":blastBottomValue,
    "Stage_Radius":stageRadius,
    "Stage_BaseY":stageBaseY,
    "Stage_Top":stageTop,
    "Stage_Bottom": stageBottom,
    "Stage_OriginX":stageOriginX,
    "Stage_OriginY":stageOriginY,
    }
    for d in stageDataTableUpdates:
        root.stageDataTable.update({d:stageDataTableUpdates[d]})


root.my_canvas = None

def GetAdjustedCoordinates(x1=0,y1=0,x2=0,y2=0):
    #Center Of Canvas
    xC = root.canvasWidth/2
    yC = root.canvasHeight/2
    #Offset, center of camera boundaries
    xO = (GetData("Camera_Left")+GetData("Camera_Right"))/2
    yO = (GetData("Camera_Top")+GetData("Camera_Bottom"))/2
    #Coordinates
    x1=x1+xC+xO
    y1=(-y1)+yC+yO
    x2=x2+xC+xO
    y2=(-y2)+yC+yO

    return x1,y1,x2,y2

def DrawSteveBlock():
    if (root.stageName == ""):
        root.my_canvas.coords(root.steveArea,-10,-10,-10,-10)
        return

    side=root.steveTable["Steve_cell_minilen_side"]
    top=root.steveTable["Steve_cell_minilen_top"]
    bottom=root.steveTable["Steve_cell_minilen_bottom"]
    xC = root.canvasWidth/2
    yC = root.canvasHeight/2
    x1 = GetData("Camera_Left")+side
    x2 = GetData("Camera_Right")-side
    y1 = GetData("Camera_Top")-top
    y2 = GetData("Camera_Bottom")+bottom
    if (y2>y1 and bottom>top):
        y2=y1
    elif(y1<y2 and top>bottom):
        y1=y2
    x1,y1,x2,y2 = GetAdjustedCoordinates(x1,y1,x2,y2)
    root.my_canvas.coords(root.steveArea,x1,y1,x2,y2)

    #Create Grid for Steveblock
    root.my_canvas.delete('grid_line')

    xO=float(root.steveTable["Steve_origin_x"])+GetData("Stage_OriginX")
    yO=float(root.steveTable["Steve_origin_y"])+GetData("Stage_OriginY")
    xO,yO,xO2,yO2 = GetAdjustedCoordinates(xO,yO,0,0)
    print(str(xO)+":"+str(yO))
    maxX=int(GetData("Stage_Radius"))+10
    minY=-20
    maxY=20
    #Vertical Lines
    for i in range(-maxX,maxX+1,10):
        #yO2-30,y02+15
        root.my_canvas.create_line([(xO+i, yO-maxY), (xO+i, yO-minY)], tag='grid_line',fill='dark green')
    #Horizontal Lines
    for i in range(minY,maxY+1,10):
        root.my_canvas.create_line([(xO-maxX, yO-i), (xO+maxX, yO-i)], tag='grid_line',fill='dark green')

def DrawBoundaries():
    x1,y1,x2,y2 = GetAdjustedCoordinates(GetData("Camera_Left"),GetData("Camera_Top"),GetData("Camera_Right"),GetData("Camera_Bottom"))
    root.my_canvas.coords(root.cameraArea,x1,y1,x2,y2)
    x1,y1,x2,y2 = GetAdjustedCoordinates(GetData("Blast_Left"),GetData("Blast_Top"),GetData("Blast_Right"),GetData("Blast_Bottom"))
    root.my_canvas.coords(root.blastArea,x1,y1,x2,y2)

def DrawCollisions():
    root.my_canvas.delete("collision")
    for c in range(min(len(root.collisions),root.maxCollisions)):
        col = root.collisions[c]
        for vert in range(len(col)-1):
            x1=float(col[vert]["x"])
            y1=float(col[vert]["y"])
            x2=float(col[vert+1]["x"])
            y2=float(col[vert+1]["y"])
            x1,y1,x2,y2 = GetAdjustedCoordinates(x1,y1,x2,y2)
            root.my_canvas.create_line(x1,y1,x2,y2, fill = "black",width=2,tags="collision")

#If yaml file is reloaded, then you should call this
def RefreshCanvas():
    DrawSteveBlock()
    DrawBoundaries()
    DrawCollisions()

def RefreshValues():
    print("Refreshing for "+root.stageName)
    disableSteve = "disable" if (root.stageName=="") else "normal"
    for data in root.stageData:
        entry = root.stageData[data]
        if ("Steve" in data):
            entry.configure(state = "normal")
            value = root.steveTable[data]
            if ("sensitivity" in data or "line" in data or "Xorigin" in data):
                entry.set(value)
            else:
                entry.delete(0,END)
                if (root.stageName==""):
                    entry.insert(0,"?")
                else:
                    entry.insert(0,value)

            if ("material" in data): 
                entry.configure(state = "disable")
            else:
                entry.configure(state = disableSteve)
        else:
            value = root.stageDataTable[data]
            entry.configure(state = "normal")
            entry.delete(0,END)
            entry.insert(0,value)
            if ("Canvas" in data or "Stage" in data):
                entry.configure(state = disableSteve)
            else:
                entry.configure(state = "disable")
    root.filemenu.entryconfig("Export Patch File To Mod", state=disableSteve)

def Main():
    print("Running main: "+root.stageName)
    if (root.stageName!="" and os.path.exists(root.levelFile)):
        UpdateTitle(os.path.basename(root.stageName) +": "+os.path.basename(root.levelFile))

    ParseSteve()
    ParseYaml()
    if (root.FirstLoad):
        CreateCanvas()
    else:
        RefreshValues()
    RefreshCanvas()
    root.FirstLoad=False
    root.Loading=False

def quit():
    root.withdraw()
    sys.exit("user exited")

LoadLastYaml()
root.mainloop()
