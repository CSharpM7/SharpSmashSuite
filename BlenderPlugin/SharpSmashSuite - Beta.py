import bpy
from bpy import context
import addon_utils
import bpy.props
from bpy.types import Operator
from bpy.props import CollectionProperty
import bmesh
import builtins as __builtin__

bl_info = {
    "name": "Sharp Smash Suite",
    "author": "C#",
    "version": (0, 5),
    "blender" : (2, 93, 0)
}

#Used to print to Blender Console, as well as system window
def console_print(*args, **kwargs):
    for a in context.screen.areas:
        if a.type == 'CONSOLE':
            c = {}
            c['area'] = a
            c['space_data'] = a.spaces.active
            c['region'] = a.regions[-1]
            c['window'] = context.window
            c['screen'] = context.screen
            s = " ".join([str(arg) for arg in args])
            for line in s.split("\n"):
                bpy.ops.console.scrollback_append(c, text=line)
def print(*args, **kwargs):
    """Console print() function."""

    console_print(*args, **kwargs) # to py consoles
    __builtin__.print(*args, **kwargs) # to system console

#Show message to user
def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
#
def HasNoObjectsSelected(self):
    if (len(bpy.context.selected_objects) == 0):
        self.report({'WARNING'}, "No objects selected")
        return True
    return False

#Replaces the .0n suffix from blender models/mats
def getTrueName(name):
    suffix = (name.find('.0'))
    newName = name[0:suffix] if suffix>-1 else name
    return newName

#Create Panel
class SharpSmashSuite_MainPanel(bpy.types.Panel):
    bl_label = "Sharp Smash Suite -β"
    bl_idname = "sharpsmashsuite.panel_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sharp Smash Suite"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        column = layout.column()
        column.label(text="By C#", icon = "DISC")
        op = self.layout.operator(
            'wm.url_open',
            text='Open Wiki',
            icon='URL'
            )
        op.url = 'https://github.com/CSharpM7/SharpSmashSuite/wiki'
        
class SharpSmashSuite_PanelRename(bpy.types.Panel):
    bl_label = "Renaming and Exporting"
    bl_idname = "sharpsmashsuite.panel_rename"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sharp Smash Suite"
    bl_parent_id = "sharpsmashsuite.panel_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        
        column = layout.column()
        column.operator("sharpsmashsuite.list_operator", icon = "FILE")
        column.operator("sharpsmashsuite.rename_operator", icon = "SMALL_CAPS")
        
        
    
#Print to console and write to file
def printAndWrite(string,filepath):
    print(string)
    #if the file is not a txt file, leave it alone
    if (filepath.find('.txt') != -1):
        with open(filepath, "a") as file:
            file.write(string)
            file.write("\n")
    
class SharpSmashSuite_OT_list(Operator):
    bl_label = "List Materials"
    bl_idname = "sharpsmashsuite.list_operator"
    bl_description = """Writes a list of materials and textures to a file.
    Useful with LazyMat to fill the spreadsheet with materials and textures, and
    Img2nutexb to retrieve texture files from a folder"""
    
    filepath: bpy.props.StringProperty()
    filename: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(
        default='*.txt',
        options={'HIDDEN'}
    )
    directory: bpy.props.StringProperty(name="'filearchives' folder", 
                subtype="DIR_PATH", options={'HIDDEN'})

    
    def execute(self,context):
        
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
        
        print(self.filepath)   
        print("")  

        dictionary = {}
        #for each selected object...
        for obj in bpy.context.selected_objects:
            #get all the materials
            material_slots = obj.material_slots
            for objMaterialSlot in material_slots:
                objMaterial = objMaterialSlot.material
                #let's get the material name, and drop the .00n
                materialName = getTrueName(objMaterial.name)

                #Find an image Texture node for the texture. If there's not one just assign defaultWhite
                nodes = objMaterial.node_tree.nodes
                imageNode = nodes.get("Image Texture")
                imageBaseName = "/common/shader/sfxPBS/default_White"
                if (imageNode is not None):
                    psdf = nodes.get("Principled BSDF")
                    #find the texture file. If it's a pBSDF, we'll look for the BaseColor input
                    if psdf:
                        #for l in psdf.inputs[0].links:
                        imageNode = psdf.inputs[0].links[0].from_node
                        
                    
                    #get the filepath to that image
                    imageFile = imageNode.image.filepath
                    folder = imageFile.rfind("\\")+1
                    imageBaseName = imageFile[folder:len(imageFile)]
                    #remove extension
                    ext = (imageBaseName.find('.'))
                    imageBaseName = imageBaseName[0:ext]
                               
                #add dictionary entry
                dictionary.update({materialName: imageBaseName})
                
        #only overwrite if it is a proper textfile
        if (self.filepath.find('.txt') != -1):
            file = open(self.filepath,"w")
            file.close()
          
        #print to file
        printAndWrite("------Materials------",self.filepath)
        for m, t in dictionary.items():
            printAndWrite(m,self.filepath)
        printAndWrite("-------Textures-------",self.filepath)
        for m, t in dictionary.items():
            printAndWrite(t,self.filepath)
        printAndWrite("----------------------",self.filepath)
        self.report({'INFO'}, "Materials saved to file and printed to console")            
        return {'FINISHED'}
    
    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
   
   
def rename(obj, materialIndex, includeOriginal):
    if len(obj.material_slots) < 1:
        return getTrueName(obj.Name)
    
    desiredName=obj.material_slots[materialIndex].name
    newName = getTrueName(desiredName)
    if (includeOriginal):
        newName = obj.name + "_" + newName
    return newName

class SharpSmashSuite_OT_rename(Operator):
    bl_label = "Rename to Material"
    bl_idname = "sharpsmashsuite.rename_operator"
    bl_description = """Renames all the selected objects to their material's name
    Useful for exporting the model and using LazyNumdlb to assign materials to meshes"""
    desiredMaterial = None
        
    def execute(self,context):
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
        
        for obj in bpy.context.selected_objects:
            obj.name = rename(obj,0,False)
            
        self.report({'INFO'}, "Objects renamed")
        return {'FINISHED'}
        

    
classes = [SharpSmashSuite_MainPanel,SharpSmashSuite_PanelRename,
SharpSmashSuite_OT_list,SharpSmashSuite_OT_rename]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
 

if __name__ == "__main__":
    register()
