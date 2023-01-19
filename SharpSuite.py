import ssbh_data_py

import os
import os.path

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path

import sys
import webbrowser

import shutil
import subprocess
from multiprocessing import Process
import threading
import imghdr

from queue import Queue

#create ui for program
root = Tk()
root.title("Sharp Smash Suite")
root.withdraw()

root.destinationDir = ""
root.searchDir = ""

root.hasModel=False
root.hasMesh=False

import configparser
config = configparser.ConfigParser()
if (not os.path.isfile(os.getcwd() + r"/img2nutexbGUI/config.ini")):
    messagebox.showerror(root.title(),"Please set img2nutexb program via img2nutexbGUI")
    sys.exit("No img")
config.read(os.getcwd() +'/img2nutexbGUI/config.ini')
imgnutexbLocation = config["DEFAULT"]["img2nutexbLocation"]
if not "maxThreads" in config["DEFAULT"]:
    config["DEFAULT"]["maxThreads"]="4"
    with open(os.getcwd() +'/img2nutexbGUI/config.ini', 'w+') as configfile:
        config.write(configfile)
maxThreads = int(config["DEFAULT"]["maxThreads"])

def truncate(string,direciton=W,limit=20,ellipsis=True):
    if (len(string) < 3):
        return string
    text = ""
    addEllipsis = "..." if (ellipsis) else ""
    if direciton == W:
        text = addEllipsis+string[len(string)-limit:len(string)]
    else:
        text = string[0:limit]+addEllipsis
    return text


imgnutexbLocation = os.getcwd() + "/img2nutexbGUI/img2nutexb.exe"

def GetMaterialFile():
    root.materialFile = root.destinationDir+"/materials.txt"
    if (not os.path.isfile(root.materialFile)):
        messagebox.showinfo(root.title(),"Please select your materials.txt exported via Blender")
        ftypes = [    
            ('materials list', ["*.txt"])
        ]
        file = filedialog.askopenfile(title = "Select materials.txt",filetypes = ftypes)
        root.materialFile = file.name if file else ""
    if (root.materialFile == ""):
        root.destroy()
        sys.exit("No model")

#make sure that it is a validated destination folder, otherwise quit
def IsValidDestination():
    root.hasModel = os.path.exists(root.destinationDir+"/model.numdlb")
    root.hasMesh = os.path.exists(root.destinationDir+"/model.numshb")
    root.hasMaterials = os.path.exists(root.destinationDir+"/materials.txt")
    return (root.hasModel and root.hasMesh and root.hasMaterials)

#open folder dialogue
def SetDestinationDir():
    messagebox.showinfo(root.title(),"Select your model's folder")
    root.destinationDir = filedialog.askdirectory(title = "Select your model's folder")
    if (root.destinationDir == ""):
        root.destroy()
        sys.exit("rejected folder")
    if (IsValidDestination() == False):
        messagebox.showerror(root.title(),"That folder doesn't contain a model and mesh file, as also needs a materials.txt generated from Blender")
        root.destroy()
        sys.exit("No model")

#make sure that it is a validated destination folder, otherwise quit
def IsValidSearch():
    validPath = os.path.isdir(root.searchDir)
    if (validPath):
        return True
    return False

#open folder dialogue
def SetSearchDir():
    messagebox.showinfo(root.title(),"Select folder with images")
    root.searchDir = filedialog.askdirectory(title = "Select folder with images")
    if (root.searchDir == ""):
        root.destroy()
        sys.exit("rejected folder")
    if (IsValidSearch() == False):
        messagebox.showerror(root.title(),"That folder doesn't contain a model,mesh or material folder")
        root.destroy()
        sys.exit("No model")
        

root.materials={}
def ReadMaterialFile():
    labels=[]
    textures=[]
    useLabel=False

    materialListFile = open(root.materialFile,'r')
    lines = materialListFile.readlines()
    lines = [line.rstrip() for line in lines]
    materialListFile.close()
    #Populate textfile without adding an extra new line at the end
    for i in range(len(lines)):
        if ("-Materials-" in lines[i]):
            useLabel=True
        elif ("-Textures-" in lines[i]):
            useLabel=False
        elif (not "---" in lines[i]):
            if (useLabel):
                labels.append(lines[i])
            else:
                textures.append(lines[i])

    for l in range(len(labels)):
        root.materials.update({labels[l]:textures[l]})

def Init():
    messagebox.showinfo(root.title(),"Make sure you imported your model already via StudioSB, and saved the materials.txt file generated from Blender to that model's folder")
    SetDestinationDir()
    GetMaterialFile()
    ReadMaterialFile()
    SetSearchDir()

root.matl = None

from typing import NewType
def Numatb_CopyEntry(matEntry,cloneEntry):
    for i in matEntry:
        entrytype = type(i)
        param_id = i.param_id
        data = i.data
        c = entrytype(param_id,data)
        cloneEntry.append(c)
    return cloneEntry
def Numatb_Copy(matEntryData):
    clone = ssbh_data_py.matl_data.MatlEntryData(matEntryData.material_label,matEntryData.shader_label)
    
    clone.blend_states = Numatb_CopyEntry(matEntryData.blend_states,clone.blend_states)
    clone.floats = Numatb_CopyEntry(matEntryData.floats,clone.floats)
    clone.booleans = Numatb_CopyEntry(matEntryData.booleans,clone.booleans)
    clone.vectors = Numatb_CopyEntry(matEntryData.vectors,clone.vectors)
    clone.rasterizer_states = Numatb_CopyEntry(matEntryData.rasterizer_states,clone.rasterizer_states)
    clone.samplers = Numatb_CopyEntry(matEntryData.samplers,clone.samplers)
    clone.textures = Numatb_CopyEntry(matEntryData.textures,clone.textures)
    return clone

def Numatb_CreateMatl():
    root.matl = ssbh_data_py.matl_data.read_matl(os.getcwd() + "/template.numatb")

    i=0
    currentEntry = root.matl.entries[0]
    for mat in root.materials:
        texture = root.materials[mat]
        if ("." in texture):
            texture = texture[0:texture.index(".")]
        newEntry = Numatb_Copy(currentEntry)
        newEntry.material_label = mat
        newEntry.textures[0].data = texture
        root.matl.entries.insert(i+1,newEntry)

    root.matl.entries.pop(0)
    root.matl.entries.sort(key=Magic_SortByLabel)
    root.matl.save(root.destinationDir+"/model.numatb")

    print("Numatb created")

def Magic_SortByLabel(e):
    return e.material_label
def MagicModel():
    from MagicModel import MagicModel
    sys.path.insert(0, '/img2nutexbGUI/')
    MagicModel.Init(root.destinationDir)

def BatchImg():  
    textures=[]
    for i in root.materials:
        textures.append(root.materials[i])

    from img2nutexbGUI import img2nutexbGUI
    sys.path.insert(0, '/img2nutexbGUI/')
    img2nutexbGUI.init(root.searchDir,root.destinationDir,os.getcwd() + r"/img2nutexbGUI/")
    img2nutexbGUI.ValidatePorgram()
    img2nutexbGUI.BatchImg(textures)

def Main():
    Init()
    BatchImg()
    Numatb_CreateMatl()
    MagicModel()
    #messagebox.showinfo(root.title(),"Finished!")
    #webbrowser.open(root.destinationDir)

if __name__ == '__main__':
    Main()
    root.mainloop()