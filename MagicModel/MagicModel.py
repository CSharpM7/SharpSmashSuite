import ssbh_data_py

import os
import os.path

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

import sys
import webbrowser

#create ui for program
root = Tk()
root.title("MagicModel")
root.withdraw()

root.destinationDir = ""
root.hasModel=False
root.hasMesh=False
root.hasMaterial=False

#make sure that it is a validated destination folder, otherwise quit
def IsValidDestination():
    root.hasModel = os.path.exists(root.destinationDir+"/model.numdlb")
    root.hasMesh = os.path.exists(root.destinationDir+"/model.numshb")
    root.hasMaterial = os.path.exists(root.destinationDir+"/model.numatb")
    return (root.hasModel or root.hasMesh or root.hasMaterial)
        

#open folder dialogue
def setDestinationDir():
    messagebox.showinfo(root.title(),"Select your model's folder")
    root.destinationDir = filedialog.askdirectory(title = "Select your model's folder")
    if (root.destinationDir == ""):
        root.destroy()
        sys.exit("rejected folder")
    if (IsValidDestination() == False):
        messagebox.showerror(root.title(),"That folder doesn't contain a model,mesh or material file")
        root.destroy()
        sys.exit("No model")
        
setDestinationDir()

FinishMessage = "Magic Model finished!"
#Assign all models their material based on their mesh's name
if (root.hasModel):
    modl = ssbh_data_py.modl_data.read_modl(root.destinationDir+"/model.numdlb")
    modl.save("model_old.numdlb")
    for modl_entry in modl.entries:
        newName = modl_entry.mesh_object_name
        suffix = (newName.find('.0'))
        newName = newName[0:suffix] if suffix>-1 else newName
        modl_entry.material_label = newName
    modl.save(root.destinationDir+"/model.numdlb")
    FinishMessage+="\n All models have their material set to their mesh's name"

#Sort by Name/Label for all meshes and materials
def SortByName(e):
    return e.name
def SortByLabel(e):
    return e.material_label

if (root.hasMesh):
    mesh = ssbh_data_py.mesh_data.read_mesh(root.destinationDir+"/model.numshb")
    mesh.objects.sort(key=SortByName)
    mesh.save(root.destinationDir+"/model.numshb")
    FinishMessage+="\n Meshes have been sorted alphabetically"

matl = ssbh_data_py.matl_data.read_matl(root.destinationDir+"/model.numatb")
if (root.hasMaterial):
    matl.entries.sort(key=SortByLabel)
    matl.save(root.destinationDir+"/model.numatb")
    FinishMessage+="\n Materials have been sorted alphabetically"

messagebox.showinfo(root.title(),FinishMessage)
webbrowser.open(root.destinationDir)