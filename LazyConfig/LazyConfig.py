import os
import os.path
import json
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import glob
import sys

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
    root.searchDir = filedialog.askdirectory(title = "Select the ""stage"" folder of your mod")
    if (root.searchDir == ""):
        root.destroy()
        sys.exit("Invalid folder")
    ValidateSearch()

#make sure that it is a validated search folder, otherwise quit
def ValidateSearch():
    root.searchDirName = os.path.basename(root.searchDir)
    if (root.searchDirName != "stage"):
        messagebox.showerror(root.title(),"Please select a folder with the ""stage"" name in your mod!")
        root.destroy()
        sys.exit("Not a stage folder")
        

#Set Search Dir
root.searchDir = config["DEFAULT"]["searchDir"]
if (not os.path.isdir(root.searchDir)):
    root.searchDir = ""
    
#Get or Set root.searchDir
if (root.searchDir == ""):
    print("no search")
    setsearchDir()
else:
    res = messagebox.askquestion(root.title(), 'Use most recent search directory?')
    if res == 'yes':
        print("using same search dir")
    elif res == 'no':
        setsearchDir()
    else:
        root.destroy()
        sys.exit("exited prompt")

#write new location to config file      
config.set("DEFAULT","searchDir",root.searchDir)
with open('config.ini', 'w+') as configfile:
        config.write(configfile)

#create dataTree for json
data = {}
data["new-dir-files"] = {}
addFiles = data["new-dir-files"]

#recursively scan subfolders to find "model" folders
def scanSubFolders(dir,modelFolders):
    folderName = os.path.basename(dir)
    if (folderName == "model"):
        modelFolders.append(dir)
        
    subfolders = [f.path for f in os.scandir(dir) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(scanSubFolders(dirname,modelFolders))
    return subfolders,modelFolders


subfolders,modelFolders = scanSubFolders(root.searchDir,[])
#trims a file/folder name to stage/*
def trimName(file):
    print(file)
    prefix = (file.find('stage\\'))
    newName = file[prefix:len(file)]
    newName = newName.replace("\\","/")
    return newName

#for each model folder, gather the folders
for folder in modelFolders:
    models = [f.path for f in os.scandir(folder) if f.is_dir()]
    for m in models:
        #for each model, trim down its name and add trimmed name to json
        newName = trimName(m)
        addFiles[newName] = []
        #comb through each file that ends in nutexb or nuanmb
        for file in os.listdir(m):
            if file.endswith(".nutexb") or file.endswith(".nuanmb"):
                addFiles[newName].append(newName + r"/" + file)

#create configJson file
writeLocation = root.searchDir + '/config.json'
writeFile = open(writeLocation,'w')
writeFile.close()
with open(writeLocation, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
    
messagebox.showinfo(root.title(),"Config.json created at: "+root.searchDir)
#open folder
import webbrowser
webbrowser.open(root.searchDir)

#quit
root.destroy()
sys.exit("success!")
