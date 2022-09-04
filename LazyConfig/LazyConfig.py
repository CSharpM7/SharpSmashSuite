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

root.modType = "stage"

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

#write new location to config file      
config.set("DEFAULT","searchDir",root.searchDir)
with open('config.ini', 'w+') as configfile:
        config.write(configfile)

print("Mod type: "+root.modType)

#create dataTree for json
data = {}
data["new-dir-infos"] = []
data["new-dir-infos-base"] = []
data["new-dir-files"] = {}
addFiles = data["new-dir-files"]
addFolders = data["new-dir-infos"]
root.folderAddition=False

def UseFolderAddition(folderkey):
    root.folderAddition=True
    if (not folderkey in addFolders):
        addFolders.append(folderkey)


#recursively scan subfolders to find "model" folders
def scanSubFolders(dir,modelFolders):
    folderName = os.path.basename(dir)
    if (folderName == "model" and root.modType == "stage"):
        modelFolders.append(dir)
    #Include animation for directoryAddition
    elif (folderName == "motion" and root.modType == "stage"):
        modelFolders.append(dir)
        
    subfolders = [f.path for f in os.scandir(dir) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(scanSubFolders(dirname,modelFolders))
        #for fighters, check every body/alt folder
        if (folderName == "model" and root.modType == "fighter"):
            fighterFolders = [m.path for m in os.scandir(dir) if m.is_dir()]
            for fname in list(fighterFolders):
                modelFolders.append(fname)
    return subfolders,modelFolders

#start of recursion, this will only begin recursive search if the directory name is a whitelist,
#or a subfolder in the directory is in the whitelist
def scanSubFoldersStart(dir,modelFolders):
    whitelist = ["fighter","stage"]

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


subfolders,modelFolders = scanSubFoldersStart(root.searchDir,[])
if (len(modelFolders)==0):
    messagebox.showinfo(root.title(),"Nothing to add to config.json")
    root.destroy()
    sys.exit("Nothing came of scan")
#trims a file/folder name to [stage or fighter]/*

def trimName(file):
    print(file)
    prefix = (file.find(root.modType+'\\'))
    trimmedName = file[prefix:len(file)]
    trimmedName = trimmedName.replace("\\","/")
    return trimmedName

root.currentSlot = ""
root.canClone = False

#for each model folder, gather the folders
for folder in modelFolders:
    models = [f.path for f in os.scandir(folder) if f.is_dir()]
    for m in models:
        baseName = os.path.basename(m)

        if (os.path.basename(folder) == "motion"):
            if (not baseName.startswith("new_")):
                continue

        #for each model, trim down its name and add trimmed name to json
        trimmedName = trimName(m)
        entryName = trimmedName
        fighterSlot = 0

        #fighters have different entryNames
        if (root.modType == "fighter"):
            fighterNameR = trimmedName.find("/model")
            fighterName = (trimmedName[0:fighterNameR]).replace("fighter/","")
            fighterSlot = trimmedName[len(trimmedName)-4:len(trimmedName)]
            entryName = "fighter/" + fighterName + fighterSlot 
            if (root.currentSlot == ""):
                root.currentSlot = fighterSlot
                root.canClone = True
            elif (root.currentSlot != fighterSlot):
                root.canClone = False

        #if entryName doesn't already exist, add it
        if (not entryName in addFiles):
            addFiles[entryName] = []

        #determine whether to use dirAddtion
        newDir = False
        #For Fighters, if the slot is greater than 7, then use dirAddition
        if (root.modType == "fighter"):
            fighterSlotAsInt = int(fighterSlot[3:4]) 
            if (fighterSlotAsInt>=8):
                UseFolderAddition(entryName)
                newDir=True
        #For Stages, if the folder contains the prefix "new_", then use dirAddition
        elif (root.modType == "stage" and baseName.startswith("new_")):
            UseFolderAddition(entryName)
            newDir=True


        #comb through each file that ends in nutexb or nuanmb
        for file in os.listdir(m):
            includeFile=file.endswith(".nutexb") or file.endswith(".nuanmb")
            if (includeFile or newDir):
                addFiles[entryName].append(trimmedName + r"/" + file)
        #remove any folders with no addition
        if (len(addFiles[entryName])==0):
            del addFiles[entryName]

#I really should put this in it's own function but I'm too lazy
if (root.canClone):
    res = messagebox.askquestion(root.title(), 'Make copies of '+root.currentSlot+' config data across c00-c07?')
    if res == 'yes':
        currentSlotAsInt = int(root.currentSlot[3:4])
        originalFiles = addFiles.copy()
        #clone
        for i in range(8):
            if (i == currentSlotAsInt):
                continue
            currentKey = list(originalFiles)[0]
            newKey = currentKey.replace(root.currentSlot,"/c0"+str(i))
            print(newKey)
            addFiles[newKey] = []
            for value in originalFiles.get(currentKey):
                newValue = value.replace(root.currentSlot,"/c0"+str(i))
                addFiles[newKey].append(newValue)
                print(newValue)
            #originalFiles[]

#remove folderAddition if not used
if (not root.folderAddition):
    del data["new-dir-infos"]
    del data["new-dir-infos-base"]
elif (root.modType == "fighter"):
    messagebox.showwarning(root.title(),"Folder addition was used for "+entryName+", you will need to manually add sound files and infobase files")
elif (root.modType == "stage"):
    del data["new-dir-infos-base"]
    #data["new-dir-infos-base"] = data["new-dir-infos"]
    #messagebox.showinfo(root.title(),"Folder addition was used for "+entryName)

#create configJson file
writeLocation = root.searchDir + '/config.json'
writeFile = open(writeLocation,'w')
writeFile.close()
with open(writeLocation, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
    
messagebox.showinfo(root.title(),"Config.json created at: "+root.searchDir)
#open folder
webbrowser.open(root.searchDir)

#quit
root.destroy()
sys.exit("success!")
