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
root.stageLocation = ""

root.steveTable={
    "Steve_Label":"Steve LVD Settings",
    "Steve_material":"soil",
    "Steve_origin_x":0,
    "Steve_origin_y":0,
    "Steve_cell_sensitivity":0,
    "Steve_line_offset":0,
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

root.collisions=[]
root.maxCollisionsTag="Canvas_Collisions To Show"
#root.maxCollisions=50
root.stageLimit=125

root.stageDefaults ={
"Camera_Label":"Camera Boundaries",
"Camera_Left":-170,
"Camera_Right":170,
"Camera_Top":130,
"Camera_Bottom":-80,
"Camera_CenterX":0,
"Camera_CenterY":0,
"Blast_Label":"Blastzone Boundaries",
"Blast_Left":-240,
"Blast_Right":240,
"Blast_Top":192,
"Blast_Bottom":-140,
"Stage_Label":"Stage Data",
"Stage_Radius":80,
"Stage_Top":47,
"Stage_Bottom":-40,
"Stage_FloorY":0,
"Stage_OriginX":0,
"Stage_OriginY":0,
"Canvas_Label":"Canvas Settings",
""+root.maxCollisionsTag:50
}

root.stageDataTable = root.stageDefaults.copy()
def ConvertSteveTag(data):
    data = (data.lower()).replace("steve_","Steve_")
    if ("top" in data):
        data = "Steve_cell_minilen_top"
    elif ("side" in data):
        data = "Steve_cell_minilen_side"
    elif ("bottom" in data):
        data = "Steve_cell_minilen_bottom"
    return data

def GetData(data):
    if ("Steve" in data):
        data = ConvertSteveTag(data)
        return root.steveTable[data]
    elif (data in root.stageDataTable):
        return root.stageDataTable[data]
    else:
        return
def SetData(data,value):
    if ("Steve" in data):
        data = ConvertSteveTag(data)
        root.steveTable[data] = value
    elif (data in root.stageDataTable):
        root.stageDataTable[data] = value
        if ("Camera" in data):
            root.stageDataTable["Camera_CenterX"] = (GetData("Camera_Left")+GetData("Camera_Right"))/2
            root.stageDataTable["Camera_CenterY"] = (GetData("Camera_Top")+GetData("Camera_Bottom"))/2
    else:
        print("Error: "+data+" key not found")

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
    root.stageLocation = root.levelFile[:root.levelFile.index(normalKey)]
    root.stageName = root.stageLocation[root.stageLocation.index(stageKey)+len(stageKey):]
    print("Stage:"+root.stageName)
    if (root.stageName == ""):
        messagebox.showerror(root.programName,"There is no valid stage within that stage folder!")
        return
    root.modParams = root.stageLocation+"/normal/param/"
    root.modDir = root.levelFile[:root.levelFile.index(stageKey)]
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
    "CameraLeft":root.stageDefaults["Camera_Left"],"CameraRight":root.stageDefaults["Camera_Right"],
    "CameraTop":root.stageDefaults["Camera_Top"],"CameraBottom":root.stageDefaults["Camera_Bottom"],
    "Label2":"Blastzone Settings",
    "BlastLeft":root.stageDefaults["Blast_Left"],"BlastRight":root.stageDefaults["Blast_Right"],
    "BlastTop":root.stageDefaults["Blast_Top"],"BlastBottom":root.stageDefaults["Blast_Bottom"],
    "Label3":"Stage Settings",
    "StageRadius":root.stageDefaults["Stage_Radius"],"StageFloorY":root.stageDefaults["Stage_FloorY"],
    "StageTop":root.stageDefaults["Stage_Top"],"StageBottom":root.stageDefaults["Stage_Bottom"]}
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
        #If accidentally selected the Yaml version instead of the lvd verison, select yaml instead
        possibleYaml = desiredFile.replace(".lvd",".yaml")
        if (os.path.exists(possibleYaml)):
            desiredFile=possibleYaml

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


def GetConfigFromYaml():
    toReturn = root.modDir + root.stageParamsFolderShortcut + r"groundconfig_"
    toReturn = toReturn+os.path.basename(root.levelFile).replace(".yaml","")
    toReturn=toReturn+".prcxml"
    return toReturn

def ParseSteve(UseSource=False):
    SetData("Steve_Side", 0)
    SetData("Steve_Top",0)
    SetData("Steve_Bottom", 0)
    if (root.stageName == ""):
        return
    tree = None
    treeRoot = None

    sourceGroundInfo = os.getcwd() + r"\groundconfig.prcxml"
    if (not os.path.exists(sourceGroundInfo)):
        messagebox.showerror(root.programName,"Source Groundconfig missing from this folder")
        return
    workingGroundInfo = GetConfigFromYaml()
    print("Info:"+workingGroundInfo)
    if (not UseSource):
        if (not os.path.exists(workingGroundInfo)):
            UseSource = True
        else:
            #Make sure the mod has our desired stage
            hasStage = False
            with open(workingGroundInfo, 'rb') as file:
                parser = ET.XMLParser(encoding ='utf-8')
                tree = ET.parse(file,parser)
                treeRoot = tree.getroot()
                for type_tag in treeRoot.findall('struct'):
                    nodeName = type_tag.get('hash')
                    if (nodeName != root.stageName):
                        treeRoot.remove(type_tag)
                    else:
                        hasStage=True
            UseSource = not hasStage
            print("Current mod's groundconfig excludes the desired stage, using source instead")

    root.TempGroundInfo = os.getcwd() + r"\tempconfig.prcxml"
    f = open(root.TempGroundInfo, "w")
    f.close()

    GroundInfo = sourceGroundInfo if UseSource else workingGroundInfo

    print("Parsing Steve Data...")
    #Parse Steve data from main groundconfig file and place it in a temporary file
    with open(GroundInfo, 'rb') as file:
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

def exportGroundInfo():
    tempPrc = os.getcwd() +"/temp.prc"
    sourcePrc = root.stageParams + "groundconfig.prc"
    parcel = root.parcelDir + r"/parcel.exe"

    if (not os.path.exists(sourcePrc)):
        messagebox.showerror(root.programName,"Cannot export without ArcExplorer's groundconfig.prc")
        return
    if (not os.path.exists(parcel)):
        messagebox.showerror(root.programName,"Cannot export without Parcel")
        return

    tree = None
    treeRoot = None

    #Write our changes to TempGroundInfo
    with open(root.TempGroundInfo, 'rb') as file:
        parser = ET.XMLParser(encoding ='utf-8')
        tree = ET.parse(file,parser)
        treeRoot = tree.getroot()

        for type_tag in treeRoot.findall('struct'):
            nodeName = type_tag.get('hash')
            if (nodeName != root.stageName):
                treeRoot.remove(type_tag)
            else:
                for child in type_tag:
                    childName = "Steve_"+child.get("hash")
                    if (childName in list(root.steveTable.keys())):
                        value = GetData(childName)
                        print("Write:"+childName+":"+str(value))
                        child.text = str(value)
        tree.write(root.TempGroundInfo)


    #Patch the source file with our edited values, and create a clone as TempPRC

    subcall = [parcel,"patch",sourcePrc,root.TempGroundInfo,tempPrc]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)
    print("Temp prc created!")

    #Patch our working folder's prc, as well
    workingPrc = os.getcwd() + "/groundconfig.prc"
    if (os.path.exists(workingPrc)):
        subcall = [parcel,"patch",workingPrc,root.TempGroundInfo,workingPrc]
        with open('output.txt', 'a+') as stdout_file:
            process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
            print(process_output.__dict__)

        print("Working prc patched!")
        #Run parcel with the original and the patch to receive a prcx
    else:
        messagebox.showwarning(root.programName,"groundconfig.prc missing from LvdSpec")

    #Create Prcx for mod
    targetLocation = root.modDir + root.stageParamsFolderShortcut
    if (not os.path.exists(targetLocation)):
        os.makedirs(targetLocation)
    targetFile = GetConfigFromYaml()

    subcall = [parcel,"diff",sourcePrc,tempPrc,targetFile.replace(".prcxml",".prcx")]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)

    print("Prcx created!")

    #Copy the temp prcxml to the destination
    shutil.copy(root.TempGroundInfo,targetFile)

    #Final part: remove temp and navigate to new folder
    os.remove(tempPrc)
    messagebox.showinfo(root.programName,"Exported steve parameters as "+os.path.basename(targetFile)+"!"
        "\nMake sure you rename the file to 'groundconfig' in your mod file"
        "\n"
        "\nLVDSpec's groundconfig.prc has also been updated!")
    webbrowser.open(targetLocation)


def OpenReadMe():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/tree/main/LvdSpec')
def OpenWiki():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/wiki')

root.string_vars = {}

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

reAlpha='[^0-9,.-]'
def OnSettingUpdated(variable):
    #Get Value, only take #s,- and .
    value = root.string_vars[variable].get()
    value = re.sub(reAlpha, '', value)
    #If empty, return
    if (value==""): return

    #Make sure the value is a valid float
    validValue=True
    try:
        value=float(value)
    except:
        validValue=False
        print(value+" is invalid for "+variable)

    if (not validValue): return
    value=float(value)
      
    #Convert Collisions to int 
    if (variable==root.maxCollisionsTag and value != ""):
        value=int(value)
    #Clamp Radius
    elif ("Radius" in variable):
        value=min(value,root.stageLimit)
    #Clamp Steve Origins
    elif ("Steve_origin" in variable):
        value=clamp(value,-10,10)

    print("Updated "+variable+" with "+str(value))
    SetData(variable,value)

    if ("Canvas" in variable):
        DrawCollisions()
    else:
        DrawSteveBlock()
        if ("Bottom" in variable):
            DrawBoundaries()

def OnSteveSettingUpdated(*args):
    if (root.Loading):
        return
    variable = "Steve_"+args[0]
    OnSettingUpdated(variable)

def OnStageSettingUpdated(*args):
    if (root.Loading):
        return
    variable = "Stage_"+args[0]
    OnSettingUpdated(variable)

def OnCanvasSettingUpdated(*args):
    if (root.Loading):
        return
    variable = "Canvas_"+args[0]
    OnSettingUpdated(variable)


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
        dataDefault = str(dataTable[data])

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
    #Default Button
    button = Button(root.fr_SteveSettings, text="Reset Values To Default", command=OnDefault)
    button.pack(side = RIGHT, fill = BOTH,expand=1,pady=10,padx=4)


def OnDefault():
    res = messagebox.askquestion("LVD Wizard: "+os.path.basename(root.levelFile), "Reset Steve parameters to their original values?")
    if res != 'yes':
        return
    ParseSteve(True)
    RefreshValues()
    RefreshCanvas()
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

    #Origin should do something with radius, maybe?
    cameraCenter = GetData("Camera_CenterX")
    desiredOriginX= (cameraCenter % 10) + (round(GetData("Stage_Radius"),1) % 10)
    desiredOriginY=GetData("Stage_FloorY") % 10

    #SteveBottom seems to be CamBottom-StageBase
    desiredBottom = GetData("Camera_Bottom")-GetData("Stage_Bottom")
    if (isWall):
        stageMiddle=abs(GetData("Stage_OriginY")-GetData("Camera_Bottom"))/2
        desiredBottom=stageMiddle-10
    desiredBottom=abs(round(desiredBottom))

    #SteveSide seems to be (CamSide-Radius)/2 where Radius is shifted by OriginX
    desiredSide = ((GetData("Camera_Right")-(GetData("Stage_Radius")+GetData("Stage_OriginX")))/2)-GetData("Stage_OriginX")
    desiredSide=math.floor(desiredSide)

    #Buffer between TopPlat's position and the highest block
    TopBuffer=20
    #For TopFromBase, we'll take the median of CameraTop and the base of the stage
    TopFromBase=math.floor((GetData("Camera_Top")-GetData("Stage_FloorY"))/2)
    #For TopPlat, we'll take Stage_Top to the nearest 10, offset it by originY
    TopPlat = (math.ceil(GetData("Stage_Top")/10)*10)+desiredOriginY
    TopFromPlat=math.floor((GetData("Camera_Top")-TopPlat-TopBuffer))
    print("Base:"+str(TopFromBase)+" Plat:"+str(TopFromPlat))
    print("")
    #Pick whichever is the smallest amount
    desiredTop=min(TopFromBase,TopFromPlat)


    SetData("Steve_Top",desiredTop)
    SetData("Steve_Side",desiredSide)
    SetData("Steve_Bottom",desiredBottom)
    SetData("Steve_origin_x",desiredOriginX)
    SetData("Steve_origin_Y",desiredOriginY)
    RefreshValues()
    messagebox.showinfo(root.programName,"Steve parameters automatically set!")


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
        highestSpawn=-100 if (len(spawns)>0) else originY
        lowestSpawn=100 if (len(spawns)>0) else originY
        lowestY=0
        for s in spawns:
            if (s>highestSpawn):
                highestSpawn=s
            elif (s<lowestSpawn):
                lowestSpawn=s

        for c in root.collisions:
            for vert in range(len(c)-1):
                x1=float(c[vert]["x"])
                y1=float(c[vert]["y"])
                #Make sure largestX and lowestY is in between camera boundaries
                if (x1>largestX and cameraLeftValue<x1 and x1<cameraRightValue):
                    largestX=x1
                if (y1<lowestY and cameraBottomValue<y1 and y1<cameraTopValue):
                    lowestY=y1
        stageRadius=min(largestX,root.stageLimit)
        stageTop=highestSpawn
        stageFloorY= lowestSpawn
        stageOriginX= math.floor(originX/100)*100
        stageOriginY= math.floor(originY/100)*100
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
    "Stage_FloorY":stageFloorY,
    "Stage_Top":stageTop,
    "Stage_Bottom": stageBottom,
    "Stage_OriginX":stageOriginX,
    "Stage_OriginY":stageOriginY,
    }
    for d in stageDataTableUpdates:
        SetData(d,stageDataTableUpdates[d])


root.my_canvas = None

def GetAdjustedCoordinates(x=0,y=0):
    #Center Of Canvas
    xC = root.canvasWidth/2
    yC = root.canvasHeight/2
    #Offset, center of camera boundaries
    xO = GetData("Camera_CenterX")
    yO = GetData("Camera_CenterY")
    #Coordinates
    if (x!=None):
        x=x+xC+xO
    if (y!=None):
        y=(-y)+yC+yO

    #I really should learn how to return dynamic variable lengths
    if (x==None):
        return y
    elif (y==None):
        return x
    else:
        return x,y


def DrawSteveBlock():
    if (root.stageName == ""):
        root.my_canvas.coords(root.steveArea,-10,-10,-10,-10)
        return

    side=GetData("Steve_Side")
    top=GetData("Steve_Top")
    bottom=GetData("Steve_Bottom")
    xC = root.canvasWidth/2
    yC = root.canvasHeight/2
    x1 = GetData("Camera_Left")+side
    x2 = GetData("Camera_Right")-side
    y1 = GetData("Camera_Top")-top
    y2 = GetData("Camera_Bottom")+bottom
    camCX = GetData("Camera_CenterX")
    camCY = GetData("Camera_CenterY")
    if (x1>camCX):
        x1=camCX
    if(x2<camCX):
        x2=camCX
    if (y1<camCY):
        y1=camCY
    if(y2>camCY):
        y2=camCY
    x1,y1 = GetAdjustedCoordinates(x1,y1)
    x2,y2 = GetAdjustedCoordinates(x2,y2)
    root.my_canvas.coords(root.steveArea,x1,y1,x2,y2)

    #Create Grid for Steveblock
    root.my_canvas.delete('grid_line')

    xO=float(GetData("Steve_origin_x"))+GetData("Stage_OriginX")
    yO=float(GetData("Steve_origin_y"))+GetData("Stage_OriginY")
    xO,yO = GetAdjustedCoordinates(xO,yO)
    maxX=int(GetData("Stage_Radius"))+10
    minY=-20
    maxY=20
    #Vertical Lines
    for i in range(-maxX,maxX+1,10):
        root.my_canvas.create_line([(xO+i, yO-maxY), (xO+i, yO-minY)], tag='grid_line',fill='dark green')
    #Horizontal Lines
    for i in range(minY,maxY+1,10):
        root.my_canvas.create_line([(xO-maxX, yO-i), (xO+maxX, yO-i)], tag='grid_line',fill='dark green')


def DrawBoundaries():
    x1,y1 = GetAdjustedCoordinates(GetData("Camera_Left"),GetData("Camera_Top"))
    x2,y2 = GetAdjustedCoordinates(GetData("Camera_Right"),GetData("Camera_Bottom"))
    root.my_canvas.coords(root.cameraArea,x1,y1,x2,y2)

    #Draw guidelines for stuff
    root.my_canvas.delete('guide_line')
    stageBottom = GetData("Stage_Bottom")
    empty,stageBottom = GetAdjustedCoordinates(0,stageBottom)
    root.my_canvas.create_line([(x1, stageBottom), (x2,stageBottom)], tag='guide_line',fill='black')

    x1,y1 = GetAdjustedCoordinates(GetData("Blast_Left"),GetData("Blast_Top"))
    x2,y2 = GetAdjustedCoordinates(GetData("Blast_Right"),GetData("Blast_Bottom"))
    root.my_canvas.coords(root.blastArea,x1,y1,x2,y2)

def DrawCollisions():
    root.my_canvas.delete("collision")
    for c in range(min(len(root.collisions),GetData(root.maxCollisionsTag))):
        col = root.collisions[c]
        for vert in range(len(col)-1):
            x1=float(col[vert]["x"])
            y1=float(col[vert]["y"])
            x2=float(col[vert+1]["x"])
            y2=float(col[vert+1]["y"])
            x1,y1 = GetAdjustedCoordinates(x1,y1)
            x2,y2 = GetAdjustedCoordinates(x2,y2)
            root.my_canvas.create_line(x1,y1,x2,y2, fill = "black",width=2,tags="collision")

#If yaml file is reloaded, then you should call this
def RefreshCanvas():
    DrawSteveBlock()
    DrawBoundaries()
    DrawCollisions()

def RefreshValues():
    print("Refreshing for "+root.stageName)
    disableSteve = "disable" if (root.stageLocation=="") else "normal"
    for data in root.stageData:
        entry = root.stageData[data]
        value =str(GetData(data))
        if ("Steve" in data):
            entry.configure(state = "normal")
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
            entry.configure(state = "normal")
            entry.delete(0,END)
            entry.insert(0,value)
            if ("Canvas" in data or "Stage" in data):
                entry.configure(state = disableSteve)
            else:
                entry.configure(state = "disable")
    root.filemenu.entryconfig("Export Patch File", state=disableSteve)

def Main():
    print("Running main: "+root.stageName)
    if (root.stageName!="" and os.path.exists(root.levelFile)):
        UpdateTitle(root.stageName +": "+os.path.basename(root.levelFile))

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
