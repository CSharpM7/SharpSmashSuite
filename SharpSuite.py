import ssbh_data_py

import os
import os.path

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

import sys
import webbrowser

import shutil
import subprocess
import imghdr

import configparser
config = configparser.ConfigParser()
if (not os.path.isfile(os.getcwd() + r"/img2nutexbGUI/config.ini")):
    messagebox.showerror(root.title(),"Please set img2nutexb program via img2nutexbGUI")
    sys.exit("No img")
config.read(os.getcwd() +'/img2nutexbGUI/config.ini')
imgnutexbLocation = config["DEFAULT"]["img2nutexbLocation"]

#create ui for program
root = Tk()
root.title("Sharp Smash Suite")
root.withdraw()

root.destinationDir = ""
root.searchDir = ""

root.hasModel=False
root.hasMesh=False

imgnutexbLocation = os.getcwd() + "/img2nutexbGUI/img2nutexb.exe"

def GetMaterialFile():
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
    return (root.hasModel or root.hasMesh or root.hasMaterial)

#open folder dialogue
def SetDestinationDir():
    messagebox.showinfo(root.title(),"Select your model's folder")
    root.destinationDir = filedialog.askdirectory(title = "Select your model's folder")
    if (root.destinationDir == ""):
        root.destroy()
        sys.exit("rejected folder")
    if (IsValidDestination() == False):
        messagebox.showerror(root.title(),"That folder doesn't contain a model,mesh or material folder")
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
    GetMaterialFile()
    ReadMaterialFile()
    SetDestinationDir()
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
        newEntry = Numatb_Copy(currentEntry)
        newEntry.material_label = mat
        newEntry.textures[0].data = texture
        root.matl.entries.insert(i+1,newEntry)

    root.matl.entries.pop(0)
    root.matl.entries.sort(key=Magic_SortByLabel)
    root.matl.save(root.destinationDir+"/model.numatb")

    print("Numatb created")

#Sort by Name/Label for all meshes and materials
def Magic_SortByName(e):
    return e.name
def Magic_SortByLabel(e):
    return e.material_label

def MagicModel():
    FinishMessage = "Magic Model finished!"
    #Assign all models their material based on their mesh's name
    if (root.hasModel):
        modl = ssbh_data_py.modl_data.read_modl(root.destinationDir+"/model.numdlb")
        modl.save(root.destinationDir+"model_old.numdlb")
        for modl_entry in modl.entries:
            newName = modl_entry.mesh_object_name
            suffix = (newName.find('.0'))
            newName = newName[0:suffix] if suffix>-1 else newName
            modl_entry.material_label = newName
        modl.save(root.destinationDir+"/model.numdlb")
        FinishMessage+="\n All models have their material set to their mesh's name"

    #Sort mesh and material alphabetically
    if (root.hasMesh):
        mesh = ssbh_data_py.mesh_data.read_mesh(root.destinationDir+"/model.numshb")
        mesh.objects.sort(key=Magic_SortByName)
        mesh.save(root.destinationDir+"/model.numshb")
        FinishMessage+="\n Meshes have been sorted alphabetically"

    print("Meshes assigned their materials")


imageExtensions = ["png", "jpg", "gif", "dds",
                   "tga", "tiff", "tco", "bmp"]
def ValidImage(img):
    ext = img[len(img)-3:len(img)]
    return ext in imageExtensions
     
#main functions
def BatchImg():    
    emptyList=False
    rewriteList=False
    overwritePrompt=True
    overwriteFiles=True
    useDDSPrompt=True
    useDDSOption=True
    renamePrompt=True
    rename=True
    print("Running...")
    #For each texture, see if we can run the program
    textures=[]
    for i in root.materials:
        textures.append(root.materials[i])
    for i in range(len(textures)):
        t = textures[i]
        #ignore files with the common tag
        if (t.find("/common/")>-1):
            print(t + " is a common file; skipping")
            continue
        #ignore files we know do not exist
        if (t.startswith("$DNE_")):
            print(t + " has DNE tag; skipping")
            continue

        #find the desired new name
        split_tup = os.path.splitext(t)
        newNutexb = root.destinationDir + "/" +split_tup[0]+".nutexb"
        newNutexb = newNutexb.lower()

        #replace nrm with nor
        if (newNutexb.find("_nrm.")>-1 or newNutexb.find("_dif.")>-1):
            if (renamePrompt):
                renamePrompt = False
                rename = messagebox.askyesno(root.title(), "Rename _dif and _nrm suffixes to Ultimate's _col and _nor?",icon ='info')
            if (rename):
                newNutexb = newNutexb.replace("_dif.nutexb","_col.nutexb")
                newNutexb = newNutexb.replace("_nrm.nutexb","_nor.nutexb")
        
        #if we find a file that already exists, ask to overwrite
        if (os.path.isfile(newNutexb)):
            if (overwritePrompt):
                overwritePrompt = False
                overwriteFiles = messagebox.askyesno(root.title(), "Some files already exists in the destination directory! Overwrite all files?",icon ='warning')
                
            if (overwriteFiles == False):
                print(t + " exists and will not overwrite")
                continue
            

        #if search target does not have an extension, let's find it
        if (t.find(".")<0):
            for (dirpath, dirnames, filenames) in os.walk(root.searchDir):
                #print([os.path.join(dirpath, file) for file in filenames])
                for filename in filenames:
                    split_tup = os.path.splitext(filename)
                    basename = split_tup[0]
                    if (basename == t):
                        #Set rewrite list to true, helps prevent looping through all files in the future
                        rewriteList=True
                        #update t
                        t = t+split_tup[1]
                        #update the item in the list
                        textures[i] = t
                        break
                    

             
        #create name of search target
        targetFile = root.searchDir + "/" + t
        fileNameExists = os.path.isfile(targetFile)
        
        #if file doesn't exist, skip
        if (not fileNameExists):
            print(t + " does not exist")
            continue
        #if it's not an image file, ignore it
        if (not ValidImage(targetFile)):
            print(os.path.basename(targetFile) + " is not an image file")
            continue
        
        #clone blank file
        blankFile = os.getcwd() + r"\img2nutexbGUI\blank.nutexb"
        shutil.copy(blankFile,newNutexb)

        print("Converting "+os.path.basename(targetFile))
        internalName = os.path.splitext(os.path.basename(targetFile))[0]
        
        #run program on it depending on if the text file ends in dds
        subcall = [imgnutexbLocation,"-n "+internalName,targetFile,newNutexb]
        convertedDDS = ""
        if (split_tup[1] == ".dds"):
            if (useDDSPrompt):
                useDDSPrompt = False
                useDDSOption = messagebox.askyesno(root.title(), "Use img2nutexb DDS options for DDS Files? (Some failed dds conversions can be fixed by not using these options)",icon ='info')
            if (useDDSOption):
                subcall.append("-d")
                subcall.append("-u")
                convertedDDS = " using dds options"
        #output any errors to a textfile
        with open('output.txt', 'a+') as stdout_file:
            try:
                process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
            except:
                print(os.path.basename(newNutexb) + " can't be converted; might be open in another program")
            #print(process_output.__dict__)
                
        print("Created "+os.path.basename(newNutexb) + convertedDDS)

    print("Images converted")
        
def Main():
    Init()
    BatchImg()
    Numatb_CreateMatl()
    MagicModel()
    messagebox.showinfo(root.title(),"Finished!")
    webbrowser.open(root.destinationDir)

Main()