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
import re

#create GUI window
root = Tk()
appName = "numatbGUI"
root.title(appName)
root.iconbitmap("icon.ico")
root.width=800
root.height=350
root.geometry(str(root.width)+"x"+str(root.height))

#default configuration
defaultLocation = os.getcwd() + "\model.numatb"
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'numatbLocation': defaultLocation,
    'presetLocation' : "",
    'matlabLocation' : "",
    'crossmodLocation' : "",
    'lazymatLocation' : "",
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

root.dbShader = "nufx.db"
root.dbMaterial = "smush_materials_v13.0.1.db"

root.matID = 0
root.shaderWarning=False

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

def HasDatabase():
    hasShader = os.path.isfile(os.getcwd() + "\\"+root.dbShader)
    hasMaterial = os.path.isfile(os.getcwd() + "\\"+root.dbMaterial)
    return hasShader and hasMaterial

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

root.exportLocation = ""
root.exportDir = ""


def GetLocation(foldername,nickname):
    location = config["DEFAULT"][foldername]
    if (not os.path.isdir(location)):
        message("Please select your "+nickname+" folder")
        location = filedialog.askdirectory(title = "Select "+nickname+" folder")
        if (not os.path.isdir(location)):
            message(type="error",text="Invalid folder")
            return ""
        else:
            config.set("DEFAULT",foldername,location)
            with open('config.ini', 'w+') as configfile:
                config.write(configfile)
    return location

def GetMatLab():
    #Make sure matlab folder exists
    matLab = GetLocation("matlabLocation","MatLab")
    if (matLab == ""):
        return ""

    #Make sure matlab exe exists
    matLab = matLab+"/MatLab.exe"
    if (os.path.isfile(matLab) == False):
        message(type="error",text="MatLab.exe is missing from MatLab folder!")
        config.set("DEFAULT","matlabLocation","")
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)
        return ""

    return matLab
def GetLazyMat():
    return GetLocation("lazymatLocation","LazyMat")

def GetCrossMod():
    return GetLocation("crossmodLocation","CrossMod")

def CreateXML():
    matLab = GetMatLab()
    if (matLab == ""):
        return

    if (root.preset == ""):
        return False

    #create output file
    outputFile = open('output.txt','w+')
    outputFile.close()

    #run matlab
    SetStatus("Running MatLab..."+root.presetNumatb)
    root.exportLocation = root.presetNumatb.replace("numatb","xml")
    subcall = [matLab,root.presetNumatb,root.exportLocation]
    with open('output.txt', 'a+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
        print(process_output.__dict__)
        return True


def ExportPreset():
    if IsEditingPreset():
        res = messagebox.askyesno(root.title(), "You'll need to save the preset file before exporting. Save now?",icon ='warning')
        if res == True:
            SaveNumatb()
        else:
            return

    xmlCreated = CreateXML()
    if (xmlCreated == False):
        return
    lazyMat = GetLazyMat()
    if (lazyMat == ""):
        return

    exportDir = lazyMat+"/Shaders"
    if (os.path.isdir(exportDir)==False):
        message(type="error",text="LazyMat is missing the Shaders folder!")
        config.set("DEFAULT","lazymatLocation","")
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)
        return

    with open(root.exportLocation, encoding='utf-8', errors='replace') as file:
        context = ET.iterparse(file, events=('end',))
        for event, elem in context:
            if elem.tag == 'material':
                title = elem.attrib['label']
                filename = format(exportDir + "\\"+title + ".xml")
                SetStatus("Creating "+title)
                with open(filename, 'wb') as f:
                    #f.write(b"<?xml version=\"1.0\" encoding=\"UTF-16\"?>\n")
                    f.write(ET.tostring(elem))
    message("Preset Exported!")


root.xmlreplacements = {
    "material name": r"Material shaderLabel",
    "/material>": r"/Material>",
    "label": r"materialLabel",
    "param": r"Parameter",
    "blend_state>" : r"BlendState>",
    "rasterizer_state>" : r"RasterizerState>",
    #bruh we really gonna capitalize it like this?
    "vector4>" : "Vector4>",
    "bool>" : "Bool>",
    "float>" : "Float>",
    "sampler>" : "Sampler>",
    "string>" : "String>"
    #unk7 of blendState to EnableAlphaSampleToCoverage
    }

#CREATE CORRUPT NUMATBS :(
def ImportCross():
    crossMod = GetLocation("crossmodLocation","CrossMod")
    if (crossMod == ""):
        return
    matLab = GetMatLab()
    if (matLab == ""):
        return

    sourceLocation = crossMod+r"\MaterialPresets\MaterialPresets.xml"
    if (os.path.isfile(sourceLocation) == False):
        message(type="error",text="MaterialPresets.xml missing from the MaterialPresets folder in CrossMod!")
        return
    targetLocation = os.getcwd()+"\\crossmod.xml"
    crossData = ""

    tree = None
    with open(sourceLocation, 'rb') as file:
        parser = ET.XMLParser(encoding ='utf-8')
        tree = ET.parse(file,parser)
        treeRoot = tree.getroot()
        treeRoot.set("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        treeRoot.set("xmlns:xsd","http://www.w3.org/2001/XMLSchema")
        for item in treeRoot.findall('./Material/Parameter/BlendState'):
            #add 11 and 12
            for child in item:
                if (child.tag == "EnableAlphaSampleToCoverage"):
                    child.tag = "Unk7"
    
    tree.write(targetLocation, encoding="utf-16", xml_declaration=True) 

    targetFile = open(targetLocation,'r', encoding='utf-16')
    crossData = targetFile.read()
    targetFile.close()
    with open(targetLocation, 'w') as f:
        #Start Replacing
        for k, v in root.xmlreplacements.items():
            crossData = crossData.replace(v,k)
        crossData.replace("EnableAlphaSampleToCoverage","Unk7")
        f.write(crossData)

    #run matlab
    SetStatus("Running MatLab...")
    exportLocation = targetLocation.replace("xml","numatb")
    subcall = [matLab,targetLocation,exportLocation]

    #create output file
    outputFile = open('output.txt','w')
    outputFile.close()

    with open('output.txt', 'r+') as stdout_file:
        process_output = subprocess.run(subcall, stdout=stdout_file, stderr=stdout_file, text=True)
    with open('output.txt', 'r') as stdout_file:
        print(stdout_file.read())
    #message("CrossMod presets saved as crossmod.numatb")
    message("CrossMod presets saved as "+exportLocation)

def ExportCross():
    if IsEditingPreset():
        res = messagebox.askyesno(root.title(), "You'll need to save the preset file before exporting. Save now?",icon ='warning')
        if res == True:
            SaveNumatb()
        else:
            return
            
    xmlCreated = CreateXML()
    if (xmlCreated == False):
        return

    crossMod = GetCrossMod()
    if (crossMod == ""):
        return

    targetFile = crossMod+r"\MaterialPresets\MaterialPresets.xml"
    #TODO: Convert file into crossmod legable one
    #might need to create a copy? like open the file and then save it elsewhere?
    crossData = ""

    exportFile = open(root.exportLocation,'r+')
    crossData = exportFile.read()
    with open(targetFile, 'w+') as f:
        #Start Replacing
        for k, v in root.xmlreplacements.items():
            crossData = crossData.replace(k,v)
        f.write(crossData)

    exportFile.close()

    crossData = ""
    tree = None
    with open(targetFile, 'rb') as file:
        #file = open(targetFile, encoding='utf-8', errors='replace')
        parser = ET.XMLParser(encoding ='utf-8')
        tree = ET.parse(file,parser)
        # get root element
        treeRoot = tree.getroot()
        treeRoot.set("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        treeRoot.set("xmlns:xsd","http://www.w3.org/2001/XMLSchema")
        for item in treeRoot.findall('./Material/Parameter/BlendState'):
            #item.remove(item[11])
            #item.remove(item[10])
            for child in item:
                if (child.tag == "Unk7"):
                    child.tag = "EnableAlphaSampleToCoverage"
        
    tree.write(targetFile, encoding="utf-16", xml_declaration=True) 

    message("Preset Exported!")

def OpenNumatb():
    OpenFile(filedialog.askopenfilename(title = "Search",filetypes=root.filetypes))

def OpenPreset():
    if IsEditingPreset():
        OpenFile(config["DEFAULT"]["numatbLocation"])
    else:
        OpenFile(root.presetNumatb)

def OpenFile(numatb):
    if (numatb == ""):
        return
    if (not os.path.isfile(numatb)):
        message(type="error",text="File "+numatb+" does not exist")
        return
    try:
        root.matl = ssbh_data_py.matl_data.read_matl(numatb)
        RefreshGUI()
    except Exception as e:
        message(type="error",text="Invalid numatb (some numatbs edited with MatLab and Notepad++ cause this error)")
        print (e)
        return

    root.numatb = numatb
    #only set configuration on opening, or saving as, provided current != preset
    if (root.numatb != root.presetNumatb):
        config.set("DEFAULT","numatbLocation",root.numatb)
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)

    #read in data

    #now refresh GUI and whatnot
    root.title(appName)
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
        if (os.path.isfile(root.numatb)):
            backupLocation = root.numatb.replace(".numatb",".numatb.bk")
            if (os.path.exists(backupLocation)):
                os.remove(backupLocation)
            os.rename(root.numatb,backupLocation)

    # Save any changes made to the root.matl.
    root.matl.save(root.numatb)
    root.title(appName)
    SetStatus("Saved to "+os.path.basename(root.numatb))
    #Update preset if editted
    if (IsEditingPreset()):  
        root.preset = ssbh_data_py.matl_data.read_matl(root.numatb)
    UpdatePresetMenus()

def ChangedNumatb():
    root.title(appName+"*")


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

#show message
def message(text,type=""):
    RevertStatus()
    type = type.lower()
    #what do you mean match type is only for 3.10?!?
    if type=="error":
        messagebox.showerror(root.title(),text)
    elif type=="warning":
        messagebox.showwarning(root.title(),text)
    else:
        messagebox.showinfo(root.title(),text)
    print(type+": "+text)

def shortenFilePath(filePath):
    filePath = filePath[2:len(filePath)]
    homepath = os.path.expanduser("~")
    homepath = homepath[2:len(homepath)]
    homepath = homepath.replace("\\","/")
    return filePath.replace(homepath,"~")

def RefreshGUI(selection=-1):
    isNewFile = (root.numatb == "")

    #Change header text based on openfile
    newFileText = "New File" if isNewFile else shortenFilePath(root.numatb)
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
    #_s = shader.rfind("_")
    #shaderName = shader[0:_s]
    #renderName = shader[_s+1:len(shader)]
    shaderName = GetShaderID(shader)
    renderName = GetRenderFromShader(shader)
    return shaderName,renderName


root.renderPasses = {"opaque","sort","near","far"}
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
    root.renderOptions['values'] = ("opaque", 
                          "sort",
                          "near",
                          "far",
                          )
    renderValue = root.renderOptions['values'].index(renderName)
    root.renderOptions.current(renderValue)
    #fill out parameter box
    params = [entry.floats,entry.booleans,entry.vectors,entry.textures,
    entry.samplers,entry.blend_states,entry.rasterizer_states
    ]
    ReadAllParams(params)

def PresetAll():
    root.deiconify()
    #make sure a material AND a preset are selected
    p = root.list_Presets.curselection()
    root.popup.destroy()
    if (len(p)==0):
        return
    presetSelection = p[0]

    for s in range(len(root.matl.entries)):

        #record the original material and its name (used for the message popup and renaming)
        original = root.matl.entries[s]
        oldName = original.material_label

        #record our preset data
        preset = root.preset.entries[presetSelection]
        newName = preset.material_label

        #make a copy
        presetClone = SSBHCopy(preset)

        mainTexture = None
        #preserve textures...should I just make this a function?
        for t in presetClone.textures:
            for u in original.textures:    
                textureID = [int(s) for s in re.findall(r"\d+",str(u.param_id))]
                textureID = int(textureID[0])
                if ((textureID == 0 or textureID == 5) and mainTexture == None):
                    mainTexture = u.data
                if (str(u.param_id) == str(t.param_id)):
                    t.data = ""+u.data
                    break

        for t in presetClone.textures:
            textureID = [int(s) for s in re.findall(r"\d+",str(t.param_id))]
            textureID = textureID[0]
            if (textureID == 0 or textureID == 5):
                t.data = mainTexture

        #place the copy where the old material is, and then remove the old material
        root.matl.entries.insert(s,presetClone)
        root.matl.entries[s].material_label = oldName
        root.matl.entries.pop(s+1)
        print(oldName)

    #RefreshGUI(selection)
    RefreshGUI_Info()
    message("All materials are now using "+newName+"'s shader")
    ChangedNumatb()

def PresetAllPopUp():
    root.popup = Toplevel()
    root.popup.title("Change All To Preset")

    root.list_Presets = Listbox(root.popup,
                      height = 10, 
                      width = 50, 
                      #bg = "grey",
                      activestyle = 'dotbox', 
                      font = "Helvetica",
                      fg = "black",
                      exportselection=False
                      )
    root.list_Presets.pack()
    for i in range(len(root.preset.entries)):
        preset = root.preset.entries[i]
        root.list_Presets.insert(i, preset.material_label)

    button = Button(root.popup, text="Change", command=PresetAll).pack()
    root.popup.protocol("WM_DELETE_WINDOW", onClosedPopup)
    root.withdraw();

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
root.configmenu.add_command(label="Open Preset File", command=OpenPreset)
root.configmenu.add_command(label="Set Preset Numatb", command=SetPreset)
root.configmenu.add_command(label="Export Presets To LazyMat", command=ExportPreset)
root.configmenu.add_command(label="Export Presets To CrossMod", command=ExportCross)
#root.configmenu.add_command(label="Import Presets From CrossMod", command=ImportCross)
root.configmenu.add_command(label="Assign Preset To All Materials", command=PresetAllPopUp)
root.menubar.add_cascade(label="Presets", menu=root.configmenu)

def OpenWiki():
    webbrowser.open('https://github.com/CSharpM7/SharpSmashSuite/wiki')

root.helpmenu = Menu(root.menubar, tearoff=0)
root.helpmenu.add_command(label="Wiki", command=OpenWiki)
#root.helpmenu.add_command(label="About...", command=donothing)
root.menubar.add_cascade(label="Help", menu=root.helpmenu)

root.config(menu=root.menubar)

root.pythonInfo = "Python: " + sys.version

def SetStatus(string):
    status.config(text = string)
    print(string)
def RevertStatus():
    status.config(text = truncate(root.pythonInfo,E,14,False))

status = Label(root, text=truncate(root.pythonInfo,E,14,False), bd=1, relief=SUNKEN, anchor=E)
status.pack(side = BOTTOM, fill=X)
root.matlLabel = Label(root, text="", bd=1, relief=SUNKEN, anchor=W)
root.matlLabel.pack(fill=X)


fr_Material = PanedWindow(orient = VERTICAL,borderwidth=10)  
fr_Material.pack(side = LEFT, fill = BOTH, expand = 1)  

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
                  width = 30, 
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

def IsEditingPreset():
    return root.numatb == root.presetNumatb

def UpdatePresetMenus():
    #Disable preset commands if you're editing the preset file!
    hasPreset = os.path.isfile(root.presetNumatb)
    if (hasPreset==True):
        if IsEditingPreset():
            hasPreset = False
    hasPresetString = "normal" if hasPreset else "disabled"
    menu_listMaterial.entryconfigure(0, state=hasPresetString)
    menu_listMaterial.entryconfigure(1, state=hasPresetString)
    root.configmenu.entryconfig(0, label="Open Preset File" if hasPreset else "Return To Working File")
    root.configmenu.entryconfig(1, state=hasPresetString)


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

    firstText = ""
    #preserve textures...should I just make this a function?
    for t in presetClone.textures:
        for u in original.textures:
            print(u.param_id)
            if (str(u.param_id) == str(t.param_id)):
                t.data = ""+u.data
                break
    presetClone.textures[0].data = firstText

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
        root.deiconify()
        root.popup.destroy()
        message(type = "warning", text = "Please select a material first!")
        return

    entry = root.matl.entries[selection]
    root.popup.title("Change "+entry.material_label+" To Preset")

    root.list_Presets = Listbox(root.popup,
                      height = 10, 
                      width = 50, 
                      #bg = "grey",
                      activestyle = 'dotbox', 
                      font = "Helvetica",
                      fg = "black",
                      exportselection=False
                      )
    root.list_Presets.pack()
    for i in range(len(root.preset.entries)):
        preset = root.preset.entries[i]
        root.list_Presets.insert(i, preset.material_label)

    button = Button(root.popup, text="Change", command=ChangeToPreset).pack()
    root.popup.protocol("WM_DELETE_WINDOW", onClosedPopup)
    root.withdraw();

def RemoveMaterial():
    selection = getSelectedMaterial()
    root.matl.entries.pop(selection)
    ChangedNumatb()
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
    SetStatus("Renamed"+entry.material_label+" to "+newName)
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


fr_Info = PanedWindow(orient = VERTICAL,borderwidth=10)  
fr_Info.pack(side = RIGHT,fill = BOTH, expand = 1)
#fr_Info_label = Label(root, text="Shader Info", bd=1, relief=SUNKEN, anchor=N)
#fr_Info.add(fr_Info_label)

fr_Shader = Frame(fr_Info)
fr_Info.add(fr_Shader)


def GetShader(shaderName):
    shaderName = GetShaderID(shaderName)
    connection = sqlite3.connect(root.dbShader)
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
    connection = sqlite3.connect(root.dbShader)
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
    connection = sqlite3.connect(root.dbMaterial)
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
    connection = sqlite3.connect(root.dbMaterial)
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
    connection = sqlite3.connect(root.dbMaterial)
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


def QueryMaterialID(shaderLabel):
    connection = sqlite3.connect(root.dbMaterial)
    cursor = connection.cursor()
    query = """SELECT MatlId FROM Material WHERE ShaderLabel LIKE ?"""
    qfilter = "%"+shaderLabel+"%"
    cursor.execute(query, (qfilter,))
    record = cursor.fetchone() #yolo
    return record

def GetMaterialID(shaderLabel):
    print(shaderLabel)
    record = QueryMaterialID(shaderLabel)
    if (record == None):
        record = QueryMaterialID(GetShaderID(shaderLabel))

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

root.defaultFloats = {
    -1 : 1,
    8 : 0.4
}
def CreateFloat(param,oldmatl,newmatl):
    data = AssignDefaultParam(param,root.defaultFloats)
    newObject = ssbh_data_py.matl_data.FloatParam(param,data)
    newmatl.floats.append(newObject)

def CreateBool(param,oldmatl,newmatl):
    data = True
    newObject = ssbh_data_py.matl_data.BooleanParam(param,data)
    newmatl.booleans.append(newObject)

root.defaultVectors = {
    -1 : [1.0,1.0,1.0,1.0],
    0 : [1.0,0.0,0.0,0.0],
    6 : [1.0,1.0,0.0,0.0],
    11 : [0.25,0.033,0.0,1.0],
    47 : [0.0,0.5,1.0,0.16]
}
def CreateVector(param,oldmatl,newmatl):
    #default value idk
    data = AssignDefaultParam(param,root.defaultVectors)
    newObject = ssbh_data_py.matl_data.Vector4Param(param,data)
    newmatl.vectors.append(newObject)

root.defaultTextures = {
    -1 : "/common/shader/sfxPBS/default_White",
    2 : "#replace_cubemap",
    4 : "/common/shader/sfxPBS/default_Normal",
    5 : "/common/shader/sfxPBS/default_Black",
    6 : "/common/shader/sfxPBS/default_Params",
    7 : "#replace_cubemap",
    8 : "#replace_cubemap",
    9 : "/common/shader/sfxPBS/default_Gray",
    14 : "/common/shader/sfxPBS/default_Black"
}
def CreateTexture(param,oldmatl,newmatl):
    data = AssignDefaultParam(param,root.defaultTextures)
    #See if we can preserve the texture
    for i in oldmatl.textures:
        if (str(i.param_id) == str(param)):
            data = ""+i.data
            break

    newObject = ssbh_data_py.matl_data.TextureParam(param,data)
    newmatl.textures.append(newObject)

def AssignDefaultParam(param,defaults):
    textureID = [int(s) for s in re.findall(r"\d+",param.name)]
    textureID = textureID[0]
    return defaults.get(textureID,defaults.get(-1))

def ParameterError(param,oldmatl,newmatl):
    message(type="error",text="wtf is that parameter?")
    root.withdraw()
    sys.exit("unknown parameter")


def GetShaderID(shaderLabel):
    if (shaderLabel.find("SFX_PBS_")<0):
        shaderLabel = "SFX_PBS_" + shaderLabel
    for r in root.renderPasses:
        renderLabel = shaderLabel.find(r)
        if (renderLabel>-1):
            shaderLabel = shaderLabel[0:renderLabel-1]
    return shaderLabel

def GetRenderFromShader(shaderLabel):
    for r in root.renderPasses:
        renderLabel = shaderLabel.find(r)
        if (renderLabel>-1):
            return shaderLabel[renderLabel:len(shaderLabel)]
    return ""

def ChangeShaderConfirm():
    root.deiconify()
    #Check to see if shader label is valid, if not, return to normal
    newName = root.popup.entryLabel.get()
    if (GetRenderFromShader(newName) == ""):
        newName = newName+"_"+ root.renderOptions.get()
        
    root.popup.destroy()
    ChangeShader(newName)

def SortShader(shader):
    key = [int(s) for s in re.findall(r"\d+",shader.param_id.name)] 
    return key[0]

def ChangeShader(newName):
    selection = getSelectedMaterial()
    if (selection <0):
        return

    print("looking for:" +newName)
    newShaderID,newShaderName = GetShader(newName)
    if (newShaderName == None):
        message(type = "error", text = "Not a valid shader!")
        return

    #create new name for label and update GUI
    entry = root.matl.entries[selection]
    shaderName,renderName = GetShaderNames(newName)
    if (renderName == ""):
        renderName = "opaque"

    entry.shader_label = shaderName+"_"+renderName
    root.shaderButton.config(text = newName)
    print("found:"+entry.shader_label)

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
        paramTypeString = ''.join([i for i in paramName if not i.isdigit()])
        paramTypes.get(paramTypeString, ParameterError)(p,entry,newEntry)

    newEntry.vectors.sort(key=SortShader)
    newEntry.floats.sort(key=SortShader)
    newEntry.booleans.sort(key=SortShader)
    newEntry.textures.sort(key=SortShader)
    newEntry.samplers.sort(key=SortShader)

    if (editingCurrent == False):
        root.matl.entries.pop(selection)
        root.matl.entries.insert(selection,newEntry)
        del entry #I sure hope this doesn't break anything...
    else:
        entry.samplers.pop(0)


    root.list_Material.select_set(selection)
    RefreshGUI_Info()
    ChangedNumatb()
    SetStatus("Updated shader for "+newEntry.material_label)

def ChangeShaderPopUp():
    selection = getSelectedMaterial()
    if (selection <0):
        return

    if (HasDatabase()==False):
        res = messagebox.askyesno(root.title(), 'You need '+root.dbShader+' and '+root.dbMaterial+ ' in this directory to use this function! Open web browser to download these files?',icon ='error')
        if res == True:
            webbrowser.open('https://github.com/ScanMountGoat/Smush-Material-Research/tree/master/Value%20Dumps')
        return

    if (root.shaderWarning == False):
        res = messagebox.askyesno(root.title(), 'Shader changing is experimental! Make sure you double check in CrossMod that everything looks alright. Proceed?',icon ='warning')
        if res == False:
            return
        root.shaderWarning = True

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
root.shaderButton.pack(side = LEFT, fill = X, expand=1)
separator = Label(fr_Shader,text="",width=3)
separator.pack(side = LEFT)

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
root.renderOptions = ttk.Combobox(fr_Shader, width = 8, textvariable = n)
# Adding combobox drop down list
root.renderOptions['values'] = []
root.renderOptions.current()
root.renderOptions.pack(side = RIGHT)
root.renderOptions.bind("<<ComboboxSelected>>", onRenderChanged)


fr_ParameterButtons = Frame(fr_Info)
fr_Info.add(fr_ParameterButtons)

def ChangeTexture():
    root.deiconify()

    #get new texture values
    newTextures = []
    for i in root.popupTextures:
        newTextures.append(i.get())
    root.popup.destroy()

    #make sure a material is selected
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    for i in range(len(entry.textures)): 
        entry.textures[i].data = newTextures[i]

    RefreshGUI_Info()
    ChangedNumatb()


def ChangeTexturePopUp():
    root.popup = Toplevel()
    #root.popup.geometry("250x250")
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    root.popup.title("Change Textures")

    label = Label(root.popup,text=entry.material_label)
    label.pack(fill = X,expand=1)

    root.fr_Textures = Frame(root.popup)
    root.fr_Textures.pack(fill = BOTH,expand=1,anchor=N)
    root.popupTextures = []
    for i in range(len(entry.textures)):
        texture = entry.textures[i]
        textureID = texture.param_id.name
        textureData = texture.data
        textureFrame = Frame(root.fr_Textures)
        textureFrame.pack(fill = X,expand=1)
        textureName = Entry(textureFrame,width=10)
        textureName.insert(0,textureID)
        textureName.configure(state ='disabled')
        textureName.pack(side = LEFT, fill = BOTH,anchor=E)
        textureValue = Entry(textureFrame,width=50)
        textureValue.insert(0,textureData)
        textureValue.pack(side = RIGHT, fill = BOTH,expand=1)
        root.popupTextures.append(textureValue)

    #root.list_TextureNames = Text(root.fr_Textures,width=10)
    #root.list_TextureNames.pack(side = LEFT, fill = BOTH,anchor=E)
    #root.list_Textures = Text(root.fr_Textures)
    #root.list_Textures.pack(side = RIGHT, fill = BOTH,expand=1)
    #for i in range(len(entry.textures)):
    #    texture = entry.textures[i]
    #    root.list_TextureNames.insert(END, texture.param_id.name+'\n')
    #    root.list_Textures.insert(END, texture.data+'\n')
    #    print(texture.data+'\n')
    #root.list_TextureNames.configure(state ='disabled')

    button = Button(root.popup, text="Change", command=ChangeTexture,width = 10).pack(side=BOTTOM)
    root.popup.protocol("WM_DELETE_WINDOW", onClosedPopup)
    root.withdraw();

root.textureButton = Button(fr_ParameterButtons, command=ChangeTexturePopUp, text="Change Textures")
root.textureButton.pack(side = LEFT, fill = X)


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
    try:
        root.preset = ssbh_data_py.matl_data.read_matl(root.presetNumatb)
    except:
        print("file corrupted!")
    UpdatePresetMenus()
if (os.path.isfile(root.numatb)):
    try:
        root.matl = ssbh_data_py.matl_data.read_matl(root.numatb)
        RefreshGUI()
    except:
        print("file corrupted!")

root.mainloop()
#root.withdraw()
#sys.exit("success")

