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
import re

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
root.programName="Steve Spec"
root.title(root.programName)
root.iconbitmap(os.getcwd() +"/icon.ico")
root.withdraw()

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

root.stageName = None
root.cameraLeftValue=-190
root.cameraRightValue=190
root.cameraTopValue=145
root.cameraBottomValue=-60
root.blastLeftValue=-190
root.blastRightValue=190
root.blastTopValue=145
root.blastBottomValue=-60
root.stageRadius=80
root.stageTop=50
root.stageBottom=-40
root.collisions=[]
root.maxCollisions=50

root.yamlFile = ""
root.modParams = ""
root.popup = None
root.popupOptions = {}
root.FirstLoad=True

def LoadMod():
    #On First Load, read from config
    if (root.FirstLoad):
        root.modDir = config["DEFAULT"]["modDir"]
        if (not os.path.isdir(root.modDir)):
            root.modDir = ""

        #If no proper directory, manually set
        if (root.modDir == ""):
            setModDir()
        #else, ask if user wants to use mod directory from config
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
    #If called from File menu, then set mod directory
    else:
        originalModDir = root.modDir
        setModDir(quitOnFail=False)

        #If no proper directory, then return
        if (not os.path.isdir(root.modDir)):
            root.modDir = ""
        if (root.modDir==""):
            root.modDir = originalModDir
            return

    #Update config
    config.set("DEFAULT","modDir",root.modDir)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)
    print("Mod set to "+os.path.basename(root.modDir))

    #Reset stage-specific options
    root.stageName = ""
    root.yamlFile = ""
    root.modParams = ""
    root.collisions=[]
    OpenStage()

def OpenStage():
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

    if (root.stageName == None):
        messagebox.showerror(root.programName,"There is no valid stage within that stage folder!")
        root.destroy()
        sys.exit("Not a stage folder")

    defaultGroundInfo = os.getcwd() + r"\groundconfig.prcxml"
    root.TempGroundInfo = os.getcwd() + r"\tempconfig.prcxml"
    f = open(root.TempGroundInfo, "w")
    f.close()
    #root.TempGroundInfo = shutil.copy(defaultGroundInfo,os.getcwd() + r"\tempconfig.prcxml")

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
                for child in type_tag:
                    childName = child.get("hash")

                    if (childName == "cell_minilen_side"):
                        root.steveSideValue = float(child.text)
                    elif (childName == "cell_minilen_top"):
                        root.steveTopValue = float(child.text)
                    elif (childName == "cell_minilen_bottom"):
                        root.steveBottomValue = float(child.text)
        tree.write(root.TempGroundInfo)

    root.modParams = root.modDir + "/stage/"+root.stageName+"/normal/param/"
    print("Stage Loaded, stage params should be at "+root.modParams)
    SetYaml(automatic=True)

def exportGroundInfoLazy():
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    shutil.copy(root.TempGroundInfo,targetLocation + r"\groundconfig.prcxml")
    messagebox.showinfo(root.programName,"Exported Info to "+root.stageName)
    webbrowser.open(targetLocation)

def exportGroundInfo():
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



def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

import fileinput

def FinishedCreateYaml():
    #create yaml by copying our sample
    root.yamlFile = root.modParams+root.stageName+"_spec.yaml"
    shutil.copy(os.getcwd() + "/sample.yaml", root.yamlFile)

    # Replace all tagged values
    with open(root.yamlFile, 'r') as file :
        filedata = file.read()

    for option in root.popupOptions:
        filedata = filedata.replace(option, root.popupOptions[option].get())

    filedata = filedata.replace("RingL", "-"+root.popupOptions["StageRadius"].get())
    filedata = filedata.replace("RingR", root.popupOptions["StageRadius"].get())

    # Write to the copy
    with open(root.yamlFile, 'w') as file:
        file.write(filedata)

    #Destroy popup, and return to main
    root.popup.destroy()
    Main()
def ClosedCreateYaml():
    if (root.FirstLoad):
        quit()

def CreateYaml():
    if (not os.path.isdir(root.modParams)):   
        messagebox.showinfo(root.programName,"Set directory to save yaml to")
        root.modParams = filedialog.askdirectory(title = "Select your yaml directory")
        if (root.modParams == ""):
            root.destroy()
            sys.exit("Invalid folder")

    root.popup = Toplevel()
    root.popup.title("Create Yaml")

    root.fr_Options = Frame(root.popup)
    root.fr_Options.pack(fill = BOTH,expand=1,anchor=N)
    root.popupOptions = {}
    stageOptions = {
    "Label1":"Camera Settings",
    "CameraLeft":root.cameraLeftValue,"CameraRight":root.cameraRightValue,
    "CameraTop":root.cameraTopValue,"CameraBottom":root.cameraBottomValue,
    "Label2":"Blastzone Settings",
    "BlastLeft":root.blastLeftValue,"BlastRight":root.blastRightValue,
    "BlastTop":root.blastTopValue,"BlastBottom":root.blastBottomValue,
    "Label3":"Stage Settings",
    "StageRadius":root.stageRadius,"StageTop":root.stageTop,"StageBottom":root.stageBottom}
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

def SetYaml(automatic=False):
    #Attempt to find automatically first, if valid directory file exists
    if (automatic and os.path.isdir(root.modParams)):
        if (root.yamlFile == ""):
            #Automatically comb through modParams to find the first yaml file
            paramfiles = [f for f in listdir(root.modParams) if os.path.exists(os.path.join(root.modParams, f))]
            root.yaml = {}
            for f in list(paramfiles):
                filename = os.path.splitext(os.path.basename(f))[0]
                extension = os.path.splitext(os.path.basename(f))[1]
                if (extension == ".yaml"):
                    #if (root.stageName in filename): #this checks if the filename contains the stage name, which might not always be the case
                    root.yamlFile = root.modParams +f
                    break
    if (root.yamlFile != ""):
        print(os.path.basename(root.yamlFile)+" was automatically retrieved")
    elif (root.yamlFile == "" or not automatic):
        #SetYaml manually. First select an lvd/yaml file
        messagebox.showinfo(root.programName,"Select your yaml or lvd file for "+root.stageName)

        
        filetypes = (
            ('All File Types', '*.yaml *lvd'),
            ('Yaml File', '*.yaml'),
            ('LVD File', '*lvd')
        )
        desiredFile = filedialog.askopenfilename(title = "Search",filetypes=filetypes,initialdir = root.modDir)

        if (desiredFile == ""):
            #enter manually if rejected, and no current file
            if (root.yamlFile == ""):
                messagebox.showwarning(root.programName,"Let's manually create a yaml file then!")
                CreateYaml()
            #otherwise close window
            else:
                return
            return

        desiredFileName = os.path.basename(desiredFile)
        print(os.path.basename(root.modDir)+"/"+desiredFileName)
        if (not Path(root.modDir) in Path(desiredFile).parents):
            messagebox.showerror(root.programName,"Level file does not match current stage")
            SetYaml(False)
            return

        #If level file does not contain current stage name, it could be from a different stage folder. Reject.
        #if (not root.stageName in desiredFileName):
        #    messagebox.showerror(root.programName,"Level file does not match current stage")
        #    SetYaml(False)
        #    return

        extension = os.path.splitext(desiredFileName)[1]

        #If it's a yaml file, continue to the main program
        if (extension == ".yaml"):
            root.yamlFile = desiredFile
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
            root.yamlFile = desiredFile.replace(".lvd",".yaml")
            subcall = [root.yamlvd,desiredFile,root.yamlFile]
            with open('output.txt', 'a+') as stdout_file:
                process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
                print(process_output.__dict__)
            #if yamlvd doesn't work with this stage, enter values manually
            if (not os.path.exists(root.yamlFile)):
                #enter manually
                messagebox.showwarning(root.programName,"Yamlvd not compatible with this stage! Let's create a yaml file!")
                CreateYaml()
                return
    Main()

root.canvasWidth = 640
root.canvasHeight = 480 #240


def OpenReadMe():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/tree/main/SteveSpec')
def OpenWiki():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/wiki')

root.string_vars = {}
def OnSteveSettingUpdated(*args):
    side = args[0]
    #remove letters from string
    value = root.string_vars[side].get()
    value = re.sub('[^0-9,.]', '', value)
    if (value==''): return #if there are no numbers, return

    value=float(value)
    if (side=="Side"):
        root.steveSideValue = value
    elif (side=="Top"):
        root.steveTopValue = value
    elif (side=="Bottom"):
        root.steveBottomValue = value
    DrawSteveBlock()

def OnCanvasSettingUpdate(*args):
    setting = args[0]
    #remove letters from string
    value = root.string_vars[setting].get()
    value = re.sub('[^0-9,.]', '', value)
    if (setting=="Max Collisions To Display"):
        root.maxCollisions=int(value)
        DrawCollisions()



#This should really only run once, maybe I should split this up but idc
def CreateCanvas():
    #Define window stuff
    root.geometry("960x512")
    root.deiconify()
    root.mainFrame = Frame(root)
    root.mainFrame.pack(fill = X,expand=1)
    root.my_canvas = Canvas(root.mainFrame,width=root.canvasWidth,height=root.canvasHeight,bg="white")
    root.my_canvas.pack(padx=20,pady=20,side=LEFT)
    #Rectangle variables for later
    root.steveArea = root.my_canvas.create_rectangle(-10,-10,-10,-10,fill = "green",tag="steve")
    root.cameraArea = root.my_canvas.create_rectangle(-10,-10,-10,-10,outline = "blue",tag="camera")
    root.blastArea = root.my_canvas.create_rectangle(-10,-10,-10,-10,outline = "red",tag = "blast")

    #File menu
    root.menubar = Menu(root)
    root.filemenu = Menu(root.menubar, tearoff=0)
    root.filemenu.add_command(label="Set Mod Folder", command=LoadMod)
    root.filemenu.add_command(label="Set Yaml File", command=SetYaml)
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
    root.fr_Settings.pack(padx=20,pady=20,fill = X,side=RIGHT,anchor=N)

    stageData = {
    "Label1":"Steve Boundaries",
    "1_Side":root.steveSideValue,
    "1_Top":root.steveTopValue,
    "1_Bottom":root.steveBottomValue,
    "Label2":"Camera Boundaries",
    "2_Left":root.cameraLeftValue,
    "2_Right":root.cameraRightValue,
    "2_Top":root.cameraTopValue,
    "2_Bottom":root.cameraBottomValue,
    "Label3":"Blastzone Boundaries",
    "3_Left":root.blastLeftValue,
    "3_Right":root.blastRightValue,
    "3_Top":root.blastTopValue,
    "3_Bottom":root.blastBottomValue,
    "Label4":"Stage Data",
    "4_Radius":root.stageRadius,
    "4_Top":root.stageTop,
    "4_Bottom": root.stageBottom,
    "Label5":"Canvas Settings",
    "5_Max Collisions To Display":root.maxCollisions
    }
    root.stageData = {}
    for data in stageData:
        #For labels, don't use Entries
        if ("Label" in data):
            dataFrame = Frame(root.fr_Settings)
            dataFrame.pack(fill = X,expand=1)
            dataName = Label(dataFrame,text=stageData[data])
            dataName.pack(fill = BOTH)
            continue
        dataText=re.sub(r'[^a-zA-Z ]', '', data)
        dataDefault = truncate(str(stageData[data]),E,6)

        dataFrame = Frame(root.fr_Settings)
        dataFrame.pack(fill = X,expand=1)
        dataName = Entry(dataFrame)
        dataName.insert(0,dataText)
        dataName.configure(state ='disabled')
        dataName.pack(side = LEFT, fill = BOTH,anchor=E)
        dataEntry=None
        #For Steve Entries, trace any updates
        if ("1_" in data or "5_" in data):
            root.string_vars.update({dataText:StringVar(name=dataText)})
            var = root.string_vars[dataText]
            if ("1_" in data):
                var.trace_add("write",OnSteveSettingUpdated)
            else:
                var.trace_add("write",OnCanvasSettingUpdate)

            dataEntry = Entry(dataFrame,textvariable=var)
            dataEntry.insert(0,dataDefault)
        #Disable non-editable categories
        else:
            dataEntry = Entry(dataFrame)
            dataEntry.insert(0,dataDefault)
            dataEntry.configure(state ='disabled')
        dataEntry.pack(side = RIGHT, fill = BOTH,expand=1)

        root.stageData.update({data:dataEntry})

    #Wizard Button
    button = Button(root.fr_Settings, text="Wizard", command=quit)
    button.pack(side = RIGHT, fill = BOTH,expand=1,pady=10,padx=4)

#Load info from yaml into our canvas
def ParseYaml():
    print("Parsing yaml:"+root.yamlFile)
    with open(root.yamlFile, "r") as stream:
        try:
            root.yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            root.destroy()
            sys.exit("Yaml exploded")

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
            root.blastLeftValue = float(root.yaml[i][0]["left"])
            root.blastRightValue = float(root.yaml[i][0]["right"])
            root.blastTopValue = float(root.yaml[i][0]["top"])
            root.blastBottomValue = float(root.yaml[i][0]["bottom"])
        #get collision Info
        elif (i=="collisions"):
            for c in root.yaml[i]:
                root.collisions.append(c["verts"])
    #Parse stage data
    largestX=0
    highestY=0
    lowestY=0
    for c in root.collisions:
        for vert in range(len(c)-1):
            x1=float(c[vert]["x"])
            y1=float(c[vert]["y"])
            if (x1>largestX):
                largestX=x1
            if (y1>highestY):
                highestY=y1
            elif (y1<lowestY):
                lowestY=y1
    root.stageRadius=largestX
    root.stageTop=highestY
    root.stageBottom=lowestY


root.my_canvas = None

def GetAdjustedCoordinates(x1=0,y1=0,x2=0,y2=0):
    #Center Of Canvas
    xC = root.canvasWidth/2
    yC = root.canvasHeight/2
    #Offset, center of camera boundaries
    xO = (root.cameraLeftValue+root.cameraRightValue)/2
    yO = (root.cameraTopValue+root.cameraBottomValue)/2
    #Coordinates
    x1=x1+xC+xO
    y1=(-y1)+yC+yO
    x2=x2+xC+xO
    y2=(-y2)+yC+yO

    return x1,y1,x2,y2

def DrawSteveBlock():
    xC = root.canvasWidth/2
    yC = root.canvasHeight/2
    x1 = root.cameraLeftValue+root.steveSideValue
    x2 = root.cameraRightValue-root.steveSideValue
    y1 = root.cameraTopValue-root.steveTopValue
    y2 = root.cameraBottomValue+root.steveBottomValue
    if (y2>y1 and root.steveBottomValue>root.steveTopValue):
        y2=y1
    elif(y1<y2 and root.steveTopValue>root.steveBottomValue):
        y1=y2
    x1,y1,x2,y2 = GetAdjustedCoordinates(x1,y1,x2,y2)
    root.my_canvas.coords(root.steveArea,x1,y1,x2,y2)
def DrawBoundaries():
    x1,y1,x2,y2 = GetAdjustedCoordinates(root.cameraLeftValue,root.cameraTopValue,root.cameraRightValue,root.cameraBottomValue)
    root.my_canvas.coords(root.cameraArea,x1,y1,x2,y2)
    x1,y1,x2,y2 = GetAdjustedCoordinates(root.blastLeftValue,root.blastTopValue,root.blastRightValue,root.blastBottomValue)
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

def Main():
    UpdateTitle(os.path.basename(root.modDir) +": "+os.path.basename(root.yamlFile))
    ParseYaml()
    if (root.FirstLoad):
        CreateCanvas()
        root.FirstLoad=False
    RefreshCanvas()

def quit():
    root.withdraw()
    sys.exit("user exited")

LoadMod()
root.mainloop()