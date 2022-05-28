import ssbh_data_py

modl = ssbh_data_py.modl_data.read_modl("model.numdlb")
modl.save("model_old.numdlb")

# Append all of the mesh entries from B to A.
for modl_entry in modl.entries:
    newName = modl_entry.mesh_object_name
    suffix = (newName.find('.0'))
    newName = newName[0:suffix] if suffix>-1 else newName
    modl_entry.material_label = newName

modl.save("model.numdlb")
