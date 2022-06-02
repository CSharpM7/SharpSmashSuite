import os
import os.path
import sys
import copy
from os import listdir
from os.path import isfile, join
import subprocess

import ssbh_data_py
import sqlite3

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import webbrowser

import configparser
config = configparser.ConfigParser()
import xml.etree.ElementTree as ET

#create GUI window
root = Tk()
appName = "numatbGUI"
root.title(appName)
root.iconbitmap("icon.ico")
root.width=600
root.height=250
root.geometry(str(root.width)+"x"+str(root.height))

#default configuration
defaultLocation = os.getcwd() + "\model.numatb"
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'numatbLocation': defaultLocation,
    'presetLocation' : "",
    'matlabLocation' : "",
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
root.numatb = config["DEFAULT"]["numatbLocation"]
root.presetNumatb = config["DEFAULT"]["presetLocation"]


# numatb file IO
def NewNumatb():
    #read in data
    print("NEW")
    root.matl = ssbh_data_py.matl_data.MatlData(major_version=1, minor_version=8)
    root.numatb = ""
    #now refresh GUI and whatnot
    RefreshGUI()
    ChangedNumatb()

root.matl = None
root.preset = None
root.filetypes = (
    ('All File Types', '*.numatb *numatb.bk'),
    ('Material File', '*.numatb'),
    ('Backup Matl', '*numatb.bk')
)
root.filenumatb = [
    root.filetypes[1]
]
root.fileexe = (
    ('MatLab exe', '*.exe'),
)

def SetPreset():
    numatb = filedialog.askopenfilename(title = "Search",filetypes=root.filetypes)
    if (numatb == ""):
        return
    root.presetNumatb = numatb
    #only set configuration on opening, or saving as
    config.set("DEFAULT","presetLocation",root.presetNumatb)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)

    #read in data
    root.preset = ssbh_data_py.matl_data.read_matl(root.presetNumatb)
    #now refresh GUI and whatnot
    UpdatePresetMenus()
    message("Preset Updated")


def ExportPreset():
    matLab = config["DEFAULT"]["matlabLocation"]
    if (not os.path.isfile(matLab)):
        message("Please select your MatLab.exe file")
        matLab = filedialog.askopenfilename(filetypes=root.fileexe)
        if (not os.path.isfile(matLab)):
            message(type="error",text="Invalid matlab file")
            return
        else:
            config.set("DEFAULT","matlabLocation",matLab)
            with open('config.ini', 'w+') as configfile:
                config.write(configfile)

    if (root.preset == ""):
        return
    exportDir = filedialog.askdirectory(title = "Select a folder to export to")
    if (exportDir == ""):
        message(type="error",text="Invalid folder")
        return

    #create output file
    outputFile = open('output.txt','w+')
    outputFile.close()
    #runmatlab
    exportLocation = root.presetNumatb.replace("numatb","xml")
    subcall = [matLab,root.presetNumatb,exportLocation]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)

    file = open(exportLocation, encoding='utf-8', errors='replace')
    context = ET.iterparse(file, events=('end',))
    for event, elem in context:
        if elem.tag == 'material':
            print(elem)
            title = elem.attrib['label']
            filename = format(exportDir + "\\"+title + ".xml")
            #print(filename)
            with open(filename, 'wb') as f:
                #do we even need this?
                f.write(b"<?xml version=\"1.0\" encoding=\"UTF-16\"?>\n")
                f.write(ET.tostring(elem))

    message("Preset Exported!")


def OpenNumatb():
    numatb = filedialog.askopenfilename(title = "Search",filetypes=root.filetypes)
    if (numatb == ""):
        return
    root.numatb = numatb
    #only set configuration on opening, or saving as, provided current != preset
    if (root.numatb != root.presetNumatb):
        config.set("DEFAULT","numatbLocation",root.numatb)
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)

    #read in data
    root.matl = ssbh_data_py.matl_data.read_matl(root.numatb)
    #now refresh GUI and whatnot
    RefreshGUI()
    UpdatePresetMenus()

def SaveAsNumatb():
    file = filedialog.asksaveasfile(filetypes = root.filenumatb, defaultextension = root.filenumatb)
    if (file is None):
        return

    root.numatb = file.name
    root.matlLabel.config(text=truncate(root.numatb,limit=40) )
    config.set("DEFAULT","numatbLocation",root.numatb)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)

    SaveNumatb(False)

    
def SaveNumatb(backUp=True):
    #create backup first
    if (backUp==True):
        backUp = ssbh_data_py.matl_data.read_matl(root.numatb)
        backupLocation = root.numatb.replace(".numatb",".numatb.bk")
        backUp.save(backupLocation)
    # Save any changes made to the root.matl.
    root.matl.save(root.numatb)
    root.title(appName)
    message("Saved!")
    UpdatePresetMenus()

def ChangedNumatb():
    root.title(appName+"*")


#truncate strings for labels
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

#show message
def message(text,type=""):
    type = type.lower()
    #what do you mean match type is only for 3.10?!?
    if type=="error":
        messagebox.showerror(root.title(),text)
    elif type=="warning":
        messagebox.showwarning(root.title(),text)
    else:
        messagebox.showinfo(root.title(),text)
    print(type+": "+text)

def RefreshGUI(selection=-1):
    isNewFile = (root.numatb == "")

    #Change header text based on openfile
    newFileText = "New File" if isNewFile else truncate(root.numatb,limit=40) 
    root.matlLabel.config(text=newFileText)

    #gray out Save based on newFile
    saveState = "disabled" if isNewFile else "normal"
    root.filemenu.entryconfig("Save", state=saveState)

    #refresh list of materials
    root.list_Material.delete(0,END)
    for i in range(len(root.matl.entries)):
        entry = root.matl.entries[i]
        root.list_Material.insert(i, entry.material_label)

    if (selection >-1):
        root.list_Material.select_set(selection)
    RefreshGUI_Info()

#convert parameters to more legible string
def ReadParamID(param_id):
    paramName = str(param_id)
    paramName = paramName[paramName.find(".")+1:paramName.find(":")]
    return paramName

def CleanParamData(data):
    toRemove = ["ssbh_data_py.matl_data.BlendStateData",
    "ssbh_data_py.matl_data.RasterizerStateData","WrapMode.","<",">",
    "ssbh_data_py.matl_data.SamplerData"
    ]
    string = str(data)
    for r in toRemove:
        string = string.replace(r,"")
    return string

def ReadAllParams(params):
    for p in params:
        for i in p:
            paramName = ReadParamID(i.param_id)
            paramValue = CleanParamData(i.data)
            addParamText(paramName +": "+paramValue+"\n")

#converts shader_label to shader_Name and render_Name
def GetShaderNames(shader):
    _s = shader.rfind("_")
    shaderName = shader[0:_s]
    renderName = shader[_s+1:len(shader)]
    return shaderName,renderName

def RefreshGUI_Info():
    #Clear any prior information
    root.shaderButton.config(text = "")
    root.renderOptions.set("")
    root.renderOptions['values'] = []
    clearParamText();
    #if a material is not selected, exit
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    #get shader and render name, set names
    shaderName,renderName = GetShaderNames(entry.shader_label)
    root.shaderButton.config(text = shaderName)

    #repopulate renderOptions combobox and set to current value
    root.renderOptions['values'] = ('opaque', 
                          'sort',
                          'near',
                          'far')

    renderValue = root.renderOptions['values'].index(renderName)
    root.renderOptions.current(renderValue)
    #fill out parameter box
    params = [entry.floats,entry.booleans,entry.vectors,entry.textures,
    entry.samplers,entry.blend_states,entry.rasterizer_states
    ]
    ReadAllParams(params)

#GUI  
def donothing():
   x = 0
def quitOut():
    root.withdraw()
    sys.exit("user exited")
   

root.menubar = Menu(root)
root.filemenu = Menu(root.menubar, tearoff=0)
root.filemenu.add_command(label="New", command=NewNumatb)
root.filemenu.add_command(label="Open", command=OpenNumatb)
root.filemenu.add_command(label="Save", command=SaveNumatb)
root.filemenu.add_command(label="Save As", command=SaveAsNumatb)
root.filemenu.add_separator()
root.filemenu.add_command(label="Exit", command=quitOut)
root.menubar.add_cascade(label="File", menu=root.filemenu)

root.configmenu = Menu(root.menubar, tearoff=0)
root.configmenu.add_command(label="Set Preset Numatb", command=SetPreset)
root.configmenu.add_command(label="Export Presets To LazyMat", command=ExportPreset)
root.menubar.add_cascade(label="Presets", menu=root.configmenu)

def OpenWiki():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/wiki')

root.helpmenu = Menu(root.menubar, tearoff=0)
root.helpmenu.add_command(label="Wiki", command=OpenWiki)
#root.helpmenu.add_command(label="About...", command=donothing)
root.menubar.add_cascade(label="Help", menu=root.helpmenu)

root.config(menu=root.menubar)

pythonInfo = "Python: " + sys.version
status = Label(root, text=truncate(pythonInfo,E,14,False), bd=1, relief=SUNKEN, anchor=E)
status.pack(side = BOTTOM, fill=X)


fr_Material = PanedWindow(orient = VERTICAL,borderwidth=10,width = root.width/2)  
fr_Material.pack(side = LEFT, fill = BOTH, expand = 1)  
root.matlLabel = Label(root, text="", bd=1, relief=SUNKEN, anchor=N)
fr_Material.add(root.matlLabel)

def getSelectedMaterial():
    selection = root.list_Material.curselection()
    if (len(selection)==0):
        return -1
    return selection[0]

#fired on selected, refreshGUI_Info
def onMaterialSelected(event):
    RefreshGUI_Info()
    
root.list_Material = Listbox(fr_Material,
                  height = 10, 
                  width = 15, 
                  #bg = "grey",
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg = "black",
                  exportselection=False
                  )
fr_Material.add(root.list_Material)
root.list_Material.bind('<<ListboxSelect>>', onMaterialSelected)

def onClosedPopup():
    root.popup.destroy()
    root.deiconify()


def AddPreset():
    selection = getSelectedMaterial()
    currentEntry = root.matl.entries[selection]

    root.preset.entries.append(currentEntry)
    root.preset.save(root.presetNumatb)
    message("Added "+currentEntry.material_label+" to presets!")


def UpdatePresetMenus():
    #Disable preset commands if you're editing the preset file!
    hasPreset = "normal" if os.path.isfile(root.presetNumatb) else "disabled"
    if (hasPreset=="normal"):
        if (root.numatb == root.presetNumatb):
            hasPreset = "disabled"
    menu_listMaterial.entryconfigure(0, state=hasPreset)
    menu_listMaterial.entryconfigure(1, state=hasPreset)

def ChangeToPreset():
    root.deiconify()
    #make sure a material AND a preset are selected
    selection = getSelectedMaterial()
    p = root.list_Presets.curselection()
    root.popup.destroy()
    if (selection <0):
        return
    if (len(p)==0):
        return
    presetSelection = p[0]

    #record the original material and its name (used for the messagepopup and renaming)
    original = root.matl.entries[selection]
    oldName = original.material_label

    #record our preset data
    preset = root.preset.entries[presetSelection]
    newName = preset.material_label

    #make a copy
    presetClone = SSBHCopy(preset)

    #preserve textures...should I just make this a function?
    for t in presetClone.textures:
        for u in original.textures:
            #print(str(u.param_id) + "/"+str)
            if (str(u.param_id) == str(t.param_id)):
                t.data = ""+u.data
                break

    #place the copy where the old material is, and then remove the old material
    root.matl.entries.insert(selection,presetClone)
    root.matl.entries[selection].material_label = oldName
    root.matl.entries.pop(selection+1)

    #RefreshGUI(selection)
    RefreshGUI_Info()
    message(oldName + " is now using "+newName+"'s shader")
    ChangedNumatb()


def ChangeToPresetPopUp():
    root.popup = Toplevel()
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    root.popup.title("Change "+entry.material_label+" To Preset")

    root.list_Presets = Listbox(root.popup,
                      height = 10, 
                      width = 15, 
                      #bg = "grey",
                      activestyle = 'dotbox', 
                      font = "Helvetica",
                      fg = "black",
                      exportselection=False
                      )
    root.list_Presets.pack()
    for i in range(len(root.preset.entries)):
        entry = root.preset.entries[i]
        root.list_Presets.insert(i, entry.material_label)

    button = Button(root.popup, text="Change", command=ChangeToPreset).pack()
    root.popup.protocol("WM_DELETE_WINDOW", onClosedPopup)
    root.withdraw();

def RemoveMaterial():
    selection = getSelectedMaterial()
    root.matl.entries.pop(selection)
    RefreshGUI()

from typing import NewType
def SSBHCopyEntry(matEntry,cloneEntry):
    for i in matEntry:
        entrytype = type(i)
        param_id = i.param_id
        data = i.data
        c = entrytype(param_id,data)
        print(type(c))
        cloneEntry.append(c)
    return cloneEntry

def SSBHCopy(matEntryData):
    clone = ssbh_data_py.matl_data.MatlEntryData(matEntryData.material_label,matEntryData.shader_label)
    
    clone.blend_states = SSBHCopyEntry(matEntryData.blend_states,clone.blend_states)
    clone.floats = SSBHCopyEntry(matEntryData.floats,clone.floats)
    clone.booleans = SSBHCopyEntry(matEntryData.booleans,clone.booleans)
    clone.vectors = SSBHCopyEntry(matEntryData.vectors,clone.vectors)
    clone.rasterizer_states = SSBHCopyEntry(matEntryData.rasterizer_states,clone.rasterizer_states)
    clone.samplers = SSBHCopyEntry(matEntryData.samplers,clone.samplers)
    clone.textures = SSBHCopyEntry(matEntryData.textures,clone.textures)
    return clone

def DuplicateMaterial():
    selection = getSelectedMaterial()
    currentEntry = root.matl.entries[selection]
    newEntry = SSBHCopy(currentEntry)

    newEntry.material_label = currentEntry.material_label + "-1"
    root.matl.entries.insert(selection+1,newEntry)
    RefreshGUI(selection+1)    
    RefreshGUI_Info()    
    ChangedNumatb()

root.popup = None

def RenameMaterial():
    root.deiconify()
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    newName = root.popup.entryLabel.get()
    entry.material_label = newName

    root.popup.destroy()

    #listBox needs to be deleted and then readded as a new name
    root.list_Material.delete(selection)
    root.list_Material.insert(selection,newName)
    root.list_Material.select_set(selection)
    
    ChangedNumatb()

def RenameMaterialPopUp():
    root.popup = Toplevel()
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]

    root.popup.title("Rename")

    root.popup.entryLabel = Entry(root.popup, width =50)
    root.popup.entryLabel.pack()
    root.popup.entryLabel.insert(0, entry.material_label)
    button = Button(root.popup, text="Rename", command=RenameMaterial).pack()
    root.popup.protocol("WM_DELETE_WINDOW", onClosedPopup)
    root.withdraw();

menu_listMaterial = Menu(root, tearoff = 0)
menu_listMaterial.add_command(label ="Add To Presets", command = AddPreset,state ='disabled')
menu_listMaterial.add_command(label ="Change To Preset", command = ChangeToPresetPopUp,state ='disabled')
menu_listMaterial.add_separator()
menu_listMaterial.add_command(label ="Rename", command = RenameMaterialPopUp)
menu_listMaterial.add_command(label ="Duplicate", command = DuplicateMaterial)
menu_listMaterial.add_separator()
menu_listMaterial.add_command(label ="Delete", command=RemoveMaterial)
  
def menu_listMaterial_popup(event):
    try:
        menu_listMaterial.tk_popup(event.x_root, event.y_root)
    finally:
        menu_listMaterial.grab_release()
  
root.list_Material.bind("<Button-3>", menu_listMaterial_popup)


fr_Info = PanedWindow(orient = VERTICAL,borderwidth=10,width = (root.width/2))  
fr_Info.pack(side = RIGHT,fill = BOTH, expand = 1)
fr_Info_label = Label(root, text="Shader Info", bd=1, relief=SUNKEN, anchor=N)
fr_Info.add(fr_Info_label)

fr_Shader = Frame(fr_Info)
fr_Info.add(fr_Shader)

shaderLabel = Label(fr_Shader, text="Shader:")
shaderLabel.pack(side = LEFT, padx=10)


def GetShader(shaderName):
    shaderName = shaderName
    connection = sqlite3.connect("Nufx.db")
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM ShaderProgram WHERE Name = ?""", (shaderName,))
    records = cursor.fetchall()
    #just take the first one
    if (len(records)==0):
        return None, None;  
    else:
        shader = records[0]
        return shader[0], shader[1];

def CreateParametersFromShader(material,shaderName="",shaderID=-1):
    connection = sqlite3.connect("Nufx.db")
    cursor = connection.cursor()
    qfilter = shaderName
    query = """SELECT ParamID FROM MaterialParameter WHERE ShaderProgramID IN (
        SELECT ID
        FROM ShaderProgram
        WHERE Name = ?
        )"""
    if (shaderID!=""):
        query = """SELECT ParamID FROM MaterialParameter WHERE ShaderProgramID = ?"""
        qfilter = shaderID
    cursor.execute(query, (qfilter,))
    records = cursor.fetchall()
    params = []
    for r in records:
        paramType = ssbh_data_py.matl_data.ParamId.from_value(r[0])
        params.append(paramType)
    return params

def GetBlendState():
    connection = sqlite3.connect("smush_materials_v13.0.1.db")
    cursor = connection.cursor()
    query = """SELECT * FROM BlendState WHERE MaterialId = ?"""
    qfilter = root.matID
    cursor.execute(query, (qfilter,))
    record = cursor.fetchone() #yolo
    
    data = ssbh_data_py.matl_data.BlendStateData()
    data.source_color = ssbh_data_py.matl_data.BlendFactor.from_value(record[3])
    #4 is unk2
    data.destination_color = ssbh_data_py.matl_data.BlendFactor.from_value(record[5])
    #6,7,8 are unk4,5,6
    data.alpha_sample_to_coverage = (record[9]==1)

    return data
def GetRasterizer():
    connection = sqlite3.connect("smush_materials_v13.0.1.db")
    cursor = connection.cursor()
    query = """SELECT * FROM RasterizerState WHERE MaterialId = ?"""
    qfilter = root.matID
    cursor.execute(query, (qfilter,))
    record = cursor.fetchone() #yolo
    
    data = ssbh_data_py.matl_data.RasterizerStateData()
    data.fill_mode = ssbh_data_py.matl_data.FillMode.from_value(record[3])
    data.cull_mode = ssbh_data_py.matl_data.CullMode.from_value(record[4])
    data.depth_bias = record[5]

    return data

def GetSampler():
    #look up the Sampler Table to see if a row has the same materialId and paramId as our arguments
    #or just yolo 
    connection = sqlite3.connect("smush_materials_v13.0.1.db")
    cursor = connection.cursor()
    query = """SELECT * FROM Sampler WHERE MaterialId = ?"""
    qfilter = root.matID
    cursor.execute(query, (qfilter,))
    record = cursor.fetchone() #yolo

    data = ssbh_data_py.matl_data.SamplerData()
    data.wraps = ssbh_data_py.matl_data.WrapMode.from_value(record[3])
    data.wrapt = ssbh_data_py.matl_data.WrapMode.from_value(record[4])
    data.wrapr = ssbh_data_py.matl_data.WrapMode.from_value(record[5])
    data.min_filter = ssbh_data_py.matl_data.MinFilter.from_value(record[6])
    data.mag_filter = ssbh_data_py.matl_data.MagFilter.from_value(record[7])
    #filterTypes = ["Default","Default2","Anisotropic Filtering"]
    #record[8] is texturefilteringtype, we need this
    data.border_color = (record[9],record[10],record[11],record[12])
    #13/14 is Unk
    data.lod_bias = record[15]
    data.max_anisotropy = None if (record[16]==0) else ssbh_data_py.matl_data.MaxAnisotropy.from_value(record[16])

    return data


root.matID = 0
def GetMaterialID(shaderLabel):
    #provided a shaderLabel, search through Materials and find the MatlId.
    connection = sqlite3.connect("smush_materials_v13.0.1.db")
    cursor = connection.cursor()
    query = """SELECT MatlId FROM Material WHERE ShaderLabel = ?"""
    qfilter = shaderLabel
    cursor.execute(query, (qfilter,))
    record = cursor.fetchone() #yolo
    return record[0]

#Create Parameters
def CreateBlendState(param,oldmatl,newmatl):
    #needs to be queried from smush_materials to create default
    data = GetBlendState()
    newObject = ssbh_data_py.matl_data.BlendStateParam(param,data)
    newmatl.blend_states.append(newObject)

def CreateRasterizerState(param,oldmatl,newmatl):
    #needs to be queried from smush_materials to create default
    data = GetRasterizer()
    newObject = ssbh_data_py.matl_data.RasterizerStateParam(param,data)
    newmatl.rasterizer_states.append(newObject)

def CreateSampler(param,oldmatl,newmatl):
    #needs to be queried from smush_materials to create default
    data = GetSampler()
    newObject = ssbh_data_py.matl_data.SamplerParam(param,data)
    newmatl.samplers.append(newObject)

def CreateFloat(param,oldmatl,newmatl):
    data = 1.0
    newObject = ssbh_data_py.matl_data.FloatParam(param,data)
    newmatl.floats.append(newObject)

def CreateBool(param,oldmatl,newmatl):
    data = False
    newObject = ssbh_data_py.matl_data.BooleanParam(param,data)
    newmatl.booleans.append(newObject)

def CreateVector(param,oldmatl,newmatl):
    #default value idk
    data = [1.0,1.0,1.0,0.0]
    newObject = ssbh_data_py.matl_data.Vector4Param(param,data)
    newmatl.vectors.append(newObject)

def CreateTexture(param,oldmatl,newmatl):
    data = r"/common/shader/sfxPBS/default_White"
    #See if we can preserve the texture
    for i in oldmatl.textures:
        if (str(i.param_id) == str(param)):
            data = ""+i.data
            break

    newObject = ssbh_data_py.matl_data.TextureParam(param,data)
    newmatl.textures.append(newObject)

def ParameterError(param,oldmatl,newmatl):
    message(type="error",text="wtf is that parameter?")
    root.withdraw()
    sys.exit("unknown parameter")

def ChangeShaderConfirm():
    root.deiconify()
    #Check to see if shader label is valid, if not, return to normal
    newName = root.popup.entryLabel.get()
    root.popup.destroy()
    ChangeShader(newName)

def ChangeShader(newName):
    selection = getSelectedMaterial()
    if (selection <0):
        return

    newShaderID,newShaderName = GetShader(newName)
    if (newShaderName == None):
        message(type = "error", text = "Not a valid shader!")
        return

    #create new name for label and update GUI
    entry = root.matl.entries[selection]
    shaderName,renderName = GetShaderNames(entry.shader_label)
    entry.shader_label = newName+"_"+renderName
    root.shaderButton.config(text = newName)

    newEntry = ssbh_data_py.matl_data.MatlEntryData(entry.material_label,entry.shader_label)
    #editing Current is possible new way
    editingCurrent=False
    if (editingCurrent==True):
        #clense entry of customs and textures
        entry.vectors.clear()
        entry.floats.clear()
        entry.booleans.clear()
        entry.textures.clear()
        while len(entry.samplers)>1:
            entry.samplers.pop(0)
    newParameters = CreateParametersFromShader(newEntry,shaderID=newShaderID)

    paramTypes = {
        "BlendState" : CreateBlendState,
        "RasterizerState" : CreateRasterizerState,
        "CustomFloat" : CreateFloat,
        "CustomBoolean" : CreateBool,
        "CustomVector" : CreateVector,
        "Sampler" : CreateSampler,
        "Texture" : CreateTexture
    }
    root.matID = GetMaterialID(newEntry.shader_label)
    print("matID:"+str(root.matID))

    for p in newParameters:
        #removed Digits
        paramName = p.name
        print(p.name)
        paramTypeString = ''.join([i for i in paramName if not i.isdigit()])
        paramTypes.get(paramTypeString, ParameterError)(p,entry,newEntry)


    if (editingCurrent == False):
        root.matl.entries.pop(selection)
        root.matl.entries.insert(selection,newEntry)
    else:
        entry.samplers.pop(0)

    #RefreshGUI(selection)
    RefreshGUI_Info()
    message("Shader Updated")

def ChangeShaderPopUp():
    selection = getSelectedMaterial()
    if (selection <0):
        return

    res = messagebox.askyesno(root.title(), 'Shader changing is experimental! Make sure you double check in CrossMod that everything looks alright. Proceed?',icon ='warning')
    if res == False:
        return

    root.popup = Toplevel()
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    shaderName,renderName = GetShaderNames(entry.shader_label)

    root.popup.title("Change Shader")

    root.popup.entryLabel = Entry(root.popup, width =50)
    root.popup.entryLabel.pack()
    root.popup.entryLabel.insert(0, shaderName)
    button = Button(root.popup, text="Change", command=ChangeShaderConfirm).pack()
    root.popup.protocol("WM_DELETE_WINDOW", onClosedPopup)
    root.withdraw();

root.shaderButton = Button(fr_Shader, command=ChangeShaderPopUp)
root.shaderButton.pack(side = RIGHT, fill = X, expand=1)

fr_Render = Frame(fr_Info)
fr_Info.add(fr_Render)
renderLabel = Label(fr_Render, text="Render Pass:")
renderLabel.pack(side = LEFT, fill = X)
n = StringVar()

def onRenderChanged(event):
    print("CHANGE")
    selection = getSelectedMaterial()
    if (selection <0):
        return
    entry = root.matl.entries[selection]
    shaderName,renderName = GetShaderNames(entry.shader_label)
    entry.shader_label = shaderName + "_" + root.renderOptions.get()
    print(entry.shader_label)    
    ChangedNumatb()


root.renderOptions = ttk.Combobox(fr_Render, width = 10, textvariable = n)
# Adding combobox drop down list
root.renderOptions['values'] = []
root.renderOptions.current()
root.renderOptions.pack(side = RIGHT)
root.renderOptions.bind("<<ComboboxSelected>>", onRenderChanged)

def addParamText(text):
    root.paramList.configure(state ='normal')
    root.paramList.insert(INSERT, text)
    root.paramList.configure(state ='disabled')
def clearParamText():
    root.paramList.configure(state ='normal')
    root.paramList.delete('1.0', END)
    root.paramList.configure(state ='disabled')

root.paramList = ScrolledText(fr_Info, bd = 1)
fr_Info.add(root.paramList)

if (os.path.isfile(root.presetNumatb)):
    root.preset = ssbh_data_py.matl_data.read_matl(root.presetNumatb)
    UpdatePresetMenus()
if (os.path.isfile(root.numatb)):
    root.matl = ssbh_data_py.matl_data.read_matl(root.numatb)
    RefreshGUI()

root.mainloop()
#root.withdraw()
#sys.exit("success")

