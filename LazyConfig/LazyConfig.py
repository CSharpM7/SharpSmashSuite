import os
import os.path
import json
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import glob
import sys
import webbrowser

import configparser
config = configparser.ConfigParser()
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'searchDir' : ""
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
root.title("Lazy Config")
root.withdraw()

#open folder dialogue
def setsearchDir():
    messagebox.showinfo(root.title(),"Select your mod's main folder")
    root.searchDir = filedialog.askdirectory(title = "Select your mod's main folder")
    if (root.searchDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    if (IsValidSearch() == False):
        messagebox.showerror(root.title(),"Please select the root of your mod's folder! This folder should contain a stage or fighter folder within it!")
        root.destroy()
        sys.exit("Not a stage folder")
        

#make sure that it is a validated search folder, otherwise quit
def IsValidSearch():
    root.searchDirName = os.path.basename(root.searchDir)
    if (root.searchDirName == "stage"):
        root.modType = "stage"
        return True
    elif (root.searchDirName == "fighter"):
        root.modType = "fighter"
        return True
    else:
        subfolders = [f.path for f in os.scandir(root.searchDir) if f.is_dir()]
        for dirname in list(subfolders):
            if (os.path.basename(dirname) == "stage"):
                root.modType = "stage"
                return True
            elif (os.path.basename(dirname) == "fighter"):
                root.modType = "fighter"
                return True
    return False
        

#Set Search Dir
def InitSearch():
    root.modType = "stage"
    root.searchDir = config["DEFAULT"]["searchDir"]
    if (not os.path.isdir(root.searchDir)):
        root.searchDir = ""
        
    #Get or Set root.searchDir
    if (root.searchDir == ""):
        print("no search")
        setsearchDir()
    else:
        if (IsValidSearch()):
            basename = os.path.basename(root.searchDir)
            res = messagebox.askquestion(root.title(), 'Use most recent search directory? ('+basename+')')
            if res == 'yes':
                print("using same search dir")
            elif res == 'no':
                setsearchDir()
                print("new search directory")
            else:
                root.destroy()
                sys.exit("exited prompt")
        else:
            setsearchDir()

    #Write new location to config file      
    config.set("DEFAULT","searchDir",root.searchDir)
    with open('config.ini', 'w+') as configfile:
            config.write(configfile)

    print("Mod type: "+root.modType)

#create dataTree for json
def InitJSON():
    root.data = {}
    root.data["new-dir-infos"] = []
    root.data["new-dir-infos-base"] = []
    root.data["unshare-blacklist"] = []
    root.data["share-to-added"] = {}
    root.data["new-dir-files"] = {}
    root.addFiles = root.data["new-dir-files"]
    root.addFolders = root.data["new-dir-infos"]

def Init():
    root.folderAddition=False
    root.txtFile = os.getcwd() + r"\files_"+root.modType+".txt"

def UseFolderAddition(folderkey):
    root.folderAddition=True
    if (not folderkey in root.addFolders):
        print("(NEW DIR)"+folderkey)
        root.addFolders.append(folderkey)
    #if (root.modType == "fighter"):
    #    messagebox.showwarning(root.title(),"Folder addition was used for "+entryName+"; LazyConfig does not support Additional Slots. Please use ReslotterGUI instead.")
    #    webbrowser.open("https://github.com/CSharpM7/reslotter")
    #    root.destroy()
    #    sys.exit("Attempted Slot Addition")


#recursively scan subfolders to find "model" folders
def scanSubFolders(dir,modelFolders):
    folderName = os.path.basename(dir)
    if (root.modType == "stage"):
        #modelFolders.append(dir)
        #Include animation for directoryAddition
        if (folderName == "model" or folderName == "motion" or folderName == "effect"):
            modelFolders.append(dir)
        
    subfolders = [f.path for f in os.scandir(dir) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(scanSubFolders(dirname,modelFolders))
        #for fighters, check every body/alt folder
        if (root.modType == "fighter"):
            if (folderName == "model" or folderName == "motion" or folderName == "sound"):
                fighterFolders = [m.path for m in os.scandir(dir) if m.is_dir()]
                for fname in list(fighterFolders):
                    modelFolders.append(fname)
            elif (folderName == "effect"):
                effectFolders = [e.path for e in os.scandir(dir) if e.is_dir()]
                for ename in list(effectFolders):
                    #modelFolders.append(ename)
                    trailFolders = [t.path for t in os.scandir(ename) if t.is_dir()]
                    for tname in list(trailFolders):
                        modelFolders.append(tname)
    return subfolders,modelFolders

#start of recursion, this will only begin recursive search if the directory name is a whitelist,
#or a subfolder in the directory is in the whitelist
def scanSubFoldersStart(dir,modelFolders):
    whitelist = ["fighter","stage","effect","sound"]

    #check if current folder is in whitelist
    folderName = os.path.basename(dir)
    for w in list(whitelist):
        if (folderName.lower() == w.lower()):
            subfolders.append(scanSubFolders(dir,modelFolders))
            return subfolders,modelFolders

    #check if subfolders are in whitelist
    subfolders = [f.path for f in os.scandir(dir) if f.is_dir()]
    for dirname in list(subfolders):
        for w in list(whitelist):
            if (os.path.basename(dirname).lower() == w.lower()):
                subfolders.extend(scanSubFolders(dirname,modelFolders))

    return subfolders,modelFolders


#trims a file/folder name to [stage or fighter]/*
def trimName(file):
    prefix = (file.find(root.modType+'\\'))
    if ("effect" in file):
        if (not "battle" in file) and (not "normal" in file):
            prefix = (file.find("effect"))
    elif ("sound" in file):
        prefix = (file.find("sound"))
    trimmedName = file[prefix:]
    trimmedName = trimmedName.replace("\\","/")
    return trimmedName

def CreateVanillaDict():
    root.vanillaFiles = []
    root.vanillaDirs = []
    if (not os.path.isfile(root.txtFile)):
        return

    #find all stages in this mod
    modFolders = root.searchDir+"/"+root.modType
    mods = []
    subfolders = [f.path for f in os.scandir(modFolders) if f.is_dir()]
    for dirname in list(subfolders):
        trimmedName = trimName(dirname)
        mods.append(trimmedName)
    effectFolders = root.searchDir+"/effect/stage"
    if (os.path.isdir(effectFolders)):
        subfolders = [f.path for f in os.scandir(effectFolders) if f.is_dir()]
        for dirname in list(subfolders):
            trimmedName = trimName(dirname)
            mods.append(trimmedName)
        mods.append("effect")
        mods.append("effect/stage")

    #Relevant files are the vanilla files that pertain to these stages/fighters
    filesystemFile = open(root.txtFile,'r')
    filesystem = filesystemFile.readlines()
    filesystem = [file.rstrip() for file in filesystem]
    filesystemFile.close()
    #For each line in the txt...
    for i in range(len(filesystem)):
        newLine='\n' if i<len(filesystem)-1 else ''
        isRelevant = False
        #Make sure that it contains the stage key, if so add it
        for m in mods:
            if (m in filesystem[i]):
                isRelevant=True
                break
        if (isRelevant):
            root.vanillaFiles.append(filesystem[i])

    #Only gather information about new directories
    for r in root.vanillaFiles:
        directory = r.rfind("/")
        myDir = r[:directory]
        if (not myDir in root.vanillaDirs):
            root.vanillaDirs.append(myDir)

def FolderInVanilla(entryName):
    #If filesystem doesn't exist, just assume the folder is in vanilla
    if (len(root.vanillaDirs)==0):
        return True

    toReturn = False
    for d in root.vanillaDirs:
        if (entryName in d):
            toReturn=True
    return toReturn
def FileInVanilla(entryName):
    if "sound/bank/fighter" in entryName:
        return True
    toReturn = False
    for d in root.vanillaFiles:
        if (entryName in d):
            toReturn=True
    return toReturn

def AddEntry(m):
    baseName = os.path.basename(m)
    #for each model, trim down its name and add trimmed name to json
    trimmedName = trimName(m)
    entryName = trimmedName

    if ("effect/fighter/" in entryName):
        key = "effect/fighter/"
        fighterName = entryName[len(key):]
        if "/" in fighterName:
            fighterName = fighterName[:fighterName.find("/")]
        entryName = "fighter/"+fighterName+"/cmn/effect"
    fighterSlot = 0

    #fighters have different entryNames
    if (root.modType == "fighter" and root.searchDir+"\\fighter" in m):
        print(trimmedName.replace("fighter/",""))
        fighterNameR = trimmedName.replace("fighter/","").find("/")
        fighterName = trimmedName.replace("fighter/","")[0:fighterNameR]
        fighterSlot = trimmedName[len(trimmedName)-4:len(trimmedName)]
        entryName = "fighter/" + fighterName + fighterSlot
        if (root.currentSlot == ""):
            root.currentSlot = fighterSlot
            root.canClone = True
        elif (root.currentSlot != fighterSlot):
            root.canClone = False

    #if entryName doesn't already exist, add it
    if (not entryName in root.addFiles):
        root.addFiles[entryName] = []

    #determine whether to use dirAddtion
    newDir = False
    #For Fighters, if the slot is greater than 7, then use dirAddition
    if (root.modType == "fighter" and root.searchDir+"\\fighter" in m):
        fighterSlotAsInt = int(fighterSlot[3:4]) 
        if (fighterSlotAsInt>=8):
            UseFolderAddition(entryName)
            newDir=True
    #For Stages, check if the folder is not in vanilla
    elif (root.modType == "stage" and not FolderInVanilla(entryName)):
        UseFolderAddition(entryName)
        newDir=True

    #comb through each file
    for file in os.listdir(m):
        filename = os.path.basename(file)
        #Don't include leftover xml and jsons
        if (os.path.isdir(m+"\\"+file)):
            continue
        if (".xml" in filename or ".json" in filename or ".yml" in filename or ".motdiff" in filename):
            continue
        #Only include model folders if using file addition
        #if ("model" in trimmedName and not newDir and not ".nuanmb" in filename):
        #    continue
        if ("motion" in trimmedName and root.modType == "fighter"):
            root.hasAnims = True
        if ("sound/bank/fighter" in trimmedName and root.modType == "fighter"):
            root.hasAnims = True
            #continue

        fileToAdd = trimmedName + r"/" + file
        if (not fileToAdd in root.addFiles[entryName]):
            root.addFiles[entryName].append(fileToAdd)

    #remove any folders with no addition
    if (len(root.addFiles[entryName])==0):
        del root.addFiles[entryName]

def ScanFolders():
    subfolders,modelFolders = scanSubFoldersStart(root.searchDir,[])
    if (len(modelFolders)==0):
        messagebox.showinfo(root.title(),"Nothing to add to config.json")
        root.destroy()
        sys.exit("Nothing came of scan")

    root.currentSlot = ""
    root.canClone = False
    root.hasAnims = False

    #for each model folder, gather the folders
    for folder in modelFolders:
        models = [f.path for f in os.scandir(folder) if f.is_dir()]
        for m in models:
            if (os.path.basename(m) == "stage"):
                stages = [f.path for f in os.scandir(m) if f.is_dir()]
                for s in stages:
                    AddEntry(s)
            else:
                AddEntry(m)
        trimmedName = trimName(folder)
        if (os.path.basename(folder) == "effect"):
            AddEntry(folder)

#Ask to clone config.json across multiple Fighter slots
def CloneSlots():
    root.clonedSlots = False
    if (root.canClone):
        res = messagebox.askquestion(root.title(), "Make copies of "+root.currentSlot+"'s config data across c00-c07?")
        if res == 'yes':
            root.clonedSlots = True
            currentSlotAsInt = int(root.currentSlot[3:4])
            originalFiles = root.addFiles.copy()
            #clone
            for currentKey in list(originalFiles):
                if "effect" in currentKey:
                    continue
                for i in range(8):
                    if (i == currentSlotAsInt):
                        continue
                    newKey = currentKey.replace(root.currentSlot,"/c0"+str(i))
                    root.addFiles[newKey] = []
                    for value in originalFiles.get(currentKey):
                        newValue = value.replace(root.currentSlot+"/","/c0"+str(i)+"/")
                        root.addFiles[newKey].append(newValue)

def ShareAnims():
    if (root.hasAnims):
        shareAdded = messagebox.askquestion(root.title(), 'Use share-to-added for animations? (Otherwise use unshare-blacklist)')
        originalFiles = root.addFiles.copy()
        for currentKey in list(originalFiles):
            if "effect" in currentKey:
                continue
            for value in originalFiles.get(currentKey):
                if "/motion" in value or "sound/bank/fighter" in value:
                    if shareAdded == 'no':
                        if (FileInVanilla(value)):
                            root.data["unshare-blacklist"].append(value)
                    else:
                        #Don't use share-to-add on new files
                        if (FileInVanilla(value)):
                            root.data["share-to-added"][value] = []
                            currentSlotAsInt = int(root.currentSlot[2:4])
                            for i in range(8):
                                if (i == currentSlotAsInt):
                                    continue
                                if "sound/bank/fighter" in value:
                                    newValue = value.replace("_"+root.currentSlot.replace("/",""),"_c0"+str(i))
                                else:
                                    newValue = value.replace(root.currentSlot+"/","/c0"+str(i)+"/")
                                root.data["share-to-added"][value].append(newValue)

def FinishJSON():
    #Remove any files that are in vanilla if cloning wasn't used
    if (root.clonedSlots == False) or True:
        cloneDict = root.addFiles.copy()
        for model in cloneDict:
            cloneModel = root.addFiles[model].copy()
            for file in cloneModel:
                if (FileInVanilla(file)):
                    root.addFiles[model].remove(file)
                else:
                    print(file)
            if (len(root.addFiles[model])==0):
                del root.addFiles[model]

    #remove folderAddition if not used
    if (not root.folderAddition):
        del root.data["new-dir-infos"]
        del root.data["new-dir-infos-base"]
    elif (root.modType == "fighter"):
        messagebox.showwarning(root.title(),"Folder addition was used for "+entryName+"; LazyConfig does not support Additional Slots. Please use ReslotterGUI instead.")
        webbrowser.open("https://github.com/CSharpM7/reslotter")
    elif (root.modType == "stage"):
        del root.data["new-dir-infos-base"]

    if len(root.data["unshare-blacklist"]) == 0:
        del root.data["unshare-blacklist"]

    if len(root.data["share-to-added"]) == 0:
        del root.data["share-to-added"]

    if len(root.data["new-dir-files"]) == 0:
        del root.data["new-dir-files"]


    #create configJson file
    writeLocation = root.searchDir + '/config.json'
    writeFile = open(writeLocation,'w')
    writeFile.close()
    with open(writeLocation, 'w', encoding='utf-8') as f:
        json.dump(root.data, f, ensure_ascii=False, indent=4)
        
    messagebox.showinfo(root.title(),"Config.json created at: "+root.searchDir)
    #open folder
    webbrowser.open(root.searchDir)

    #quit
    root.destroy()
    sys.exit("success!")

def Main():
    InitSearch()
    InitJSON()
    Init()
    CreateVanillaDict()
    ScanFolders()
    ShareAnims()
    CloneSlots()
    FinishJSON()

Main()
