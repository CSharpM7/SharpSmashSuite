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
    "version": (1, 0),
    "blender" : (2, 93, 0)
}

#Used to print to Blender Console, as well as system window
def console_print(*args, **kwargs):
    return
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
    
def report(self,type,message):
    self.report(type,message)
    print(message)

#Show message to user
def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
#
def HasNoObjectsSelected(self):
    if (len(bpy.context.selected_objects) == 0):
        report(self,{'WARNING'}, "No objects selected")
        return True
    return False

#Replaces the .0n suffix from blender models/mats
def getTrueName(name):
    suffix = (name.find('.0'))
    newName = name[0:suffix] if suffix>-1 else name
    return newName

#Create Panel
class SharpSmashSuite_MainPanel(bpy.types.Panel):
    bl_label = "Sharp Smash Suite"
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
        op.url = 'www.google.com'
        
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
        
class SharpSmashSuite_PanelObject(bpy.types.Panel):
    bl_label = "Manipulate Objects"
    bl_idname = "Swap Blendz"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sharp Smash Suite"
    bl_parent_id = "sharpsmashsuite.panel_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        
        column = layout.column()
        column.operator("sharpsmashsuite.separate_operator", icon = "MATERIAL")
        column.operator("sharpsmashsuite.map_operator", icon = "GROUP_UVS")
        column.operator("sharpsmashsuite.join_operator", icon = "OUTLINER_OB_MESH")
        
class SharpSmashSuite_PanelMisc(bpy.types.Panel):
    bl_label = "Misc"
    bl_idname = "sharpsmashsuite.panel_"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sharp Smash Suite"
    bl_parent_id = "sharpsmashsuite.panel_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        
        column = layout.column()
        column.operator("sharpsmashsuite.vertex_operator", icon = "GROUP_VERTEX")
        column.operator("sharpsmashsuite.swap_operator", icon = "SPREADSHEET")  
        
    
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
                        print(materialName)
                        if (len(psdf.inputs[0].links) > 0):
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
        report(self,{'INFO'}, "Materials saved to file and printed to console")            
        return {'FINISHED'}
    
    def invoke(self,context,event):
        self.filepath = "materials.txt"
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
            
        report(self,{'INFO'}, "Objects renamed")
        return {'FINISHED'}
        
class SharpSmashSuite_OT_separate(Operator):
    bl_label = "Separate and Preserve Materials"
    bl_idname = "sharpsmashsuite.separate_operator"
    bl_description = """In case Edit>Mesh>Seperate>By Material ends up unlinking materials from meshes
    NOTE: This is poorly optimized, so save before running this"""
    
    
    desiredMaterial = None
    includeName: bpy.props.BoolProperty(name = "Include Original Name Prefix", default=False,
    description = """Program will rename materials to objectName+materialName.
    If false, will only rename to material name""")
    replace: bpy.props.BoolProperty(name = "Replace Original", default=False)
    
    def execute(self,context):
        
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
            
        #Find the collection to store this object in, or if we should create a new one
        old_collection = bpy.context.selected_objects[0].users_collection
        new_collectionName = old_collection[0].name
        if (self.replace == False):
            new_collectionName = new_collectionName + " - Split"
            
        new_collection = bpy.data.collections.get(new_collectionName)
        if (new_collection is None):
            new_collection = bpy.data.collections.new(new_collectionName)
            bpy.context.scene.collection.children.link(new_collection)
            
        #for each selected object...
        for obj in bpy.context.selected_objects:
            material_slots = obj.material_slots
            
            #Step one: Clone the object, we'll dissect this clone bit by bit
            #so run time can be decreased from objs^mats^faces objs^mats^log(faces)
            cloned_obj = obj.copy()
            cloned_obj.data = obj.data.copy()
            new_collection.objects.link(cloned_obj)

            #Ignore those without a material
            if (len(material_slots) < 2):
                new_name = rename(obj,0,self.includeName)
                cloned_obj.name = new_name
                continue
            
            cloned_mesh = cloned_obj.data
            cloned_bmesh = bmesh.new()
            cloned_bmesh.from_mesh(cloned_obj.data)
            #God I wish i just knew how to assign faces to a new object
            
            for mat_i in range (0, len(material_slots)): 
                #Create a copy of the cloned object to be used in its own mesh
                new_obj = cloned_obj.copy()
                new_obj.data = cloned_obj.data.copy()
                new_collection.objects.link(new_obj)

                #give it a new name based on the material
                #include the object prefix if desired
                new_name = rename(obj,mat_i,self.includeName)
                new_obj.name = new_name
                
                #Step twp: create new mesh and new bmesh, bmesh will be manipulated
                new_mesh = new_obj.data
                new_bmesh = bmesh.new()
                new_bmesh.from_mesh(new_obj.data)
                
                # remove faces with other materials from bmesh
                for f in new_bmesh.faces:
                    if f.material_index != mat_i:
                        new_bmesh.faces.remove(f)
                verts = [v for v in new_bmesh.verts if not v.link_faces]
                for v in verts:
                    new_bmesh.verts.remove(v)
                
                for f in cloned_bmesh.faces:
                    if f.material_index == mat_i:
                        cloned_bmesh.faces.remove(f)
                verts = [v for v in cloned_bmesh.verts if not v.link_faces]
                for v in verts:
                    cloned_bmesh.verts.remove(v)
                    
                cloned_bmesh.to_mesh(cloned_mesh)
                
                #apply bmesh to our new mesh
                new_bmesh.to_mesh(new_mesh)
                new_bmesh.free()
                
                #remove all other excess materials
                new_obj.data.materials.clear()
                new_obj.data.materials.append(material_slots[mat_i].material)
             
                
            cloned_bmesh.free()
            bpy.data.objects.remove(cloned_obj, do_unlink=True)
            if (self.replace == True):
                bpy.data.objects.remove(obj, do_unlink=True)
             
        
        
        report(self,{'INFO'}, "Objects seperated")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def renameMaps():
    for obj in bpy.context.selected_objects: 
        #layers[].active means the active UV layer!
        #loop through each uv layer, 
        #if it is the active UVmap, name it "map1"
        #else name it to bake1
        #else name it to map2-6
        
        #BE SURE TO NOT RENAME MAPS WITH MAP/BAKE/COLORSET
        #maybe prompt menu to replace them?
        
        #also rename vertexcolors, the active one always to colorset1
        #rename all of them?
        baked=True
        map=2
        for uvmap in obj.data.uv_layers: 
            if (uvmap.active_render):
                uvmap.name = "map1"
            elif (baked):
                uvmap.name = "bake1"
                baked=False
            else:
                uvmap.name = "map"+str(map)
                map = map+1
                
        map=2
        for colormap in obj.data.vertex_colors:
            if (colormap.active_render):
                colormap.name = "colorSet1"
            else:
                colormap.name = "colorSet"+str(map)
                map = map+1
    
class SharpSmashSuite_OT_renameMaps(Operator):
    bl_label = "Rename Maps"
    bl_idname = "sharpsmashsuite.map_operator"
    bl_description = """Renames UV Maps to map1, bake1, map(n); Color maps to colorset1,colorset(n).
    Used with Join Like Objects and Swap Materials to preserve UVs/Vertex Colors.
    Maps active in Render are assigned 1"""
    desiredMaterial = None
        
    def execute(self,context):
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
        
        renameMaps()
        report(self,{'INFO'}, "Maps renamed")
        return {'FINISHED'}    

class SharpSmashSuite_MENU_join(bpy.types.Menu):
    bl_label = "Join Like Objects"
    bl_idname = "sharpsmashsuite.join_menu"

    def draw(self, context):
        layout = self.layout

        layout.label(text="WARNING", icon='ERROR')
        layout.label(text="This operation will rename your maps and objects! This will also take a while to complete. Click OK to proceed")
        layout.operator("sharpsmashsuite.join_operator_confirm")


class SharpSmashSuite_OT_join_confirm(Operator):
    bl_label = "OK"
    bl_idname = "sharpsmashsuite.join_operator_confirm"
    
    def execute(self,context):
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
        print("Joining objects")
        
        #maps need to be renamed first to preserve UVs
        renameMaps()     
            
        #create a list of objects based on their material
        #should look like {MaterialName : Mesh}
        objectsByName = {}
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                tName = rename(obj,0,False)
                value = objectsByName.setdefault(tName,[])
                value.append(obj)
                
        
        for trueName, objs in objectsByName.items():
                
            ctx = bpy.context.copy()

            # one of the objects to join
            ctx['active_object'] = objs[0]
            ctx['selected_editable_objects'] = objs
            
            #join object and rename it to the material
            bpy.ops.object.join(ctx)
            newObject = ctx['active_object']
            newObject.name = trueName
            
            #remove excess materials
            newObject.active_material_index = 0
            for i in range(1,len(newObject.material_slots)):
                bpy.ops.object.material_slot_remove({'object': newObject}) 

        report(self,{'INFO'}, "Objects joined")
        return {'FINISHED'}
    

class SharpSmashSuite_OT_join(Operator):
    bl_label = "Join Like Objects"
    bl_idname = "sharpsmashsuite.join_operator"
    bl_description = """Joins objects that have the same material"""
    desiredMaterial = None
        
    def execute(self,context):
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
        
        bpy.ops.wm.call_menu(name=SharpSmashSuite_MENU_join.bl_idname)
        return {'FINISHED'}
    
class SharpSmashSuite_OT_swap(Operator):
    bl_label = "Swap Materials"
    bl_idname = "sharpsmashsuite.swap_operator"
    bl_description = """(Might not be useful)
    If you used the model importer and have smash materials, this will
    reassign the materials and rename maps to their smash counterparts so you can export the mesh properly.
    Does not convert materials"""
    desiredMaterial = None
    
    def execute(self,context):
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
        
        #maps need to be renamed to be compatible with smash blender tools
        renameMaps()
        #for each selected object...
        for obj in bpy.context.selected_objects:
            #get all the materials
            material_slots = obj.material_slots
            for objMaterialSlot in material_slots:
            
                objMaterial = objMaterialSlot.material
                #let's get the material name, and drop the .00n
                materialName = getTrueName(objMaterial.name)
                #now find a mat that matches that name
                desiredMaterial = bpy.data.materials.get(materialName)
                #if it doesn't exist, skip this mat
                if desiredMaterial is None:
                    print(materialName," not found from ", obj.name)
                    continue
                
                #now assign the new material
                objMaterialSlot.material = desiredMaterial
                print(objMaterial.name," set in", obj.name)

        report(self,{'INFO'}, "Materials Swapped")
        return {'FINISHED'}
        
#This was suppose to be the optimized version of Separate, but I can't figure out
#how to move Vertex Groups or Verticies to a new mesh
class SharpSmashSuite_OT_vertex(Operator):
    bl_label = "Vertex Group From Materials"
    bl_idname = "sharpsmashsuite.vertex_operator"
    bl_description = """(DEPRECATED)
    Creates vertex groups from materials"""
    
    
    desiredMaterial = None
    includeName = True
    #includeName: bpy.props.BoolProperty(name = "Include Original Name Prefix", default=False,
    #description: """Program will rename materials to objectName+materialName.
    #If false, will only rename to material name""")
    #replace: bpy.props.BoolProperty(name = "Replace Original", default=False)
    replace = False
    
    def execute(self,context):
        
        if (HasNoObjectsSelected(self)):
            return {'FINISHED'}
            
        #Find the collection to store this object in, or if we should create a new one
        old_collection = bpy.context.selected_objects[0].users_collection
        new_collectionName = old_collection[0].name
        if (self.replace == False):
            new_collectionName = new_collectionName + " - Vertex"
            
        new_collection = bpy.data.collections.get(new_collectionName)
        if (new_collection is None):
            new_collection = bpy.data.collections.new(new_collectionName)
            bpy.context.scene.collection.children.link(new_collection)
            
        #for each selected object...
        for obj in bpy.context.selected_objects:
            material_slots = obj.material_slots
            #if there are less than two material slots, don't bother
            if (len(material_slots) < 2):
                continue
            
            #create a clone of the object, we'll dissect it in the next for loop
            cloned_obj = obj.copy()
            cloned_obj.data = obj.data.copy()
            new_collection.objects.link(cloned_obj)
                
            for index, slot in enumerate(obj.material_slots):
                verts = [v for f in cloned_obj.data.polygons 
                if f.material_index == index for v in f.vertices]
                
                if len(verts):
                    vg = obj.vertex_groups.get(slot.material.name)
                    if vg is None: 
                        vg = cloned_obj.vertex_groups.new(name=slot.material.name)
                    vg.add(verts, 1.0, 'ADD')
             
                
            #if (self.replace == True):               
            #bpy.data.objects.remove(obj, do_unlink=True)
                
        report(self,{'INFO'}, "Vertex Groups created")
        return {'FINISHED'}

    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_dialog(self)
        
def draw_item(self, context):
    layout = self.layout
    layout.menu(SharpSmashSuite_MENU_join.bl_idname)

    
classes = [SharpSmashSuite_MainPanel,SharpSmashSuite_PanelRename,SharpSmashSuite_PanelObject,SharpSmashSuite_PanelMisc,
SharpSmashSuite_OT_swap,SharpSmashSuite_OT_list,SharpSmashSuite_OT_separate,
SharpSmashSuite_OT_vertex,SharpSmashSuite_OT_rename,SharpSmashSuite_OT_renameMaps,
SharpSmashSuite_OT_join,SharpSmashSuite_MENU_join,SharpSmashSuite_OT_join_confirm]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    bpy.types.INFO_HT_header.append(draw_item)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

    bpy.types.INFO_HT_header.remove(draw_item)

if __name__ == "__main__":
    register()
