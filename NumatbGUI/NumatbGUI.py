import os
import os.path
import sys
import copy
from os import listdir
from os.path import isfile, join

import ssbh_data_py

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import webbrowser

import configparser
config = configparser.ConfigParser()

#create GUI window
root = Tk()
root.title("numatbGUI")
root.iconbitmap("icon.ico")
root.width=600
root.height=250
root.geometry(str(root.width)+"x"+str(root.height))

#default configuration
defaultLocation = os.getcwd() + "\model.numatb"
defaultConfig = configparser.ConfigParser()
defaultConfig['DEFAULT'] = {
    'numatbLocation': defaultLocation,
    'presetLocation' : ""
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


# numatb file IO
def NewNumatb():
    #read in data
    print("NEW")
    root.matl = ssbh_data_py.matl_data.MatlData(major_version=1, minor_version=8)
    root.numatb = ""
    #now refresh GUI and whatnot
    RefreshGUI()

root.matl = None
root.filetypes = (
    ('Material File', '*.numatb'),
)
def OpenNumatb():
    root.numatb = filedialog.askopenfilename(title = "Search",filetypes=root.filetypes)
    if (root.numatb == ""):
        return

    #only set configuration on opening
    config.set("DEFAULT","numatbLocation",root.numatb)
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)

    #read in data
    root.matl = ssbh_data_py.matl_data.read_matl(root.numatb)
    #now refresh GUI and whatnot
    RefreshGUI()

def SaveAsNumatb():
    file = filedialog.asksaveasfile(filetypes = root.filetypes, defaultextension = root.filetypes)
    root.numatb = file.path
    print(root.numatb)
    SaveNumatb(False)
    
def SaveNumatb(backUp=True):
    #create backup first
    if (backUp==True):
        backUp = ssbh_data_py.matl_data.read_matl(root.numatb)
        backupLocation = root.numatb.replace(".numatb",".numatb.bk")
        backUp.save(backupLocation)
    # Save any changes made to the root.matl.
    root.matl.save(root.numatb)
    message("Saved!")



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

def RefreshGUI():
    isNewFile = (root.numatb == "")

    #Change header text based on openfile
    newFileText = "" if isNewFile else ":"+truncate(root.numatb,limit=30) 
    root.title(string="numatbGUI"+newFileText)

    #gray out Save based on newFile
    saveState = "disabled" if isNewFile else "normal"
    root.filemenu.entryconfig("Save", state=saveState)

    #refresh list of materials
    root.list_Material.delete(0,END)
    for i in range(len(root.matl.entries)):
        entry = root.matl.entries[i]
        root.list_Material.insert(i, entry.material_label)
    RefreshGUI_Info()

#convert parameters to more legible string
def ReadParamID(param_id):
    paramName = str(param_id)
    paramName = paramName[paramName.find(".")+1:paramName.find(":")]
    return paramName
def ReadAllParams(params):
    for p in params:
        for i in p:
            paramName = ReadParamID(i.param_id)
            paramValue = str(i.data)
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
    clearParamText();
    #if a material is not selected, exit
    selection = getSelectedMaterial()
    if (selection <0):
        return

    entry = root.matl.entries[selection]
    #get shader and render name, set names
    shaderName,renderName = GetShaderNames(entry.shader_label)
    root.shaderButton.config(text = shaderName)
    renderValue = root.renderOptions['values'].index(renderName)
    root.renderOptions.current(renderValue)
    #fill out parameter box
    params = [entry.floats,entry.booleans,entry.vectors,entry.textures]
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
root.configmenu.add_command(label="Set Preset Numatb", command=donothing)
root.menubar.add_cascade(label="Settings", menu=root.configmenu)

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
fr_Material_label = Label(root, text="List of Materials", bd=1, relief=SUNKEN, anchor=N)
fr_Material.add(fr_Material_label)

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
    newEntry.vectors[0].data = [2.0,1.0,0.0,1.0]
    RefreshGUI()


menu_listMaterial = Menu(root, tearoff = 0)
menu_listMaterial.add_command(label ="Rename")
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
root.shaderButton = Button(fr_Shader, text="asdasdasdasd", command=donothing)
root.shaderButton.pack(side = RIGHT, fill = X, expand=1)
#fr_Info.add(shaderButton)

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


root.renderOptions = ttk.Combobox(fr_Render, width = 10, textvariable = n)
# Adding combobox drop down list
root.renderOptions['values'] = ('opaque', 
                          'sort',
                          'near',
                          'far')
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

if (os.path.isfile(root.numatb)):
    root.matl = ssbh_data_py.matl_data.read_matl(root.numatb)
    RefreshGUI()

root.mainloop()
#root.withdraw()
#sys.exit("success")

