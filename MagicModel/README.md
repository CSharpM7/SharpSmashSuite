# Magic Model

This program edits the .numdlb model file to make each model's material_label value match that mesh's name. This also takes into account Blender exported models that typically suffix meshes with ".0n". As long as you don't have mesh.1xx, it should work. Numdlb will have a backup created before any changes are made.
This program also edits .numshb mesh files and .numatb material files to sort each entry alphabetically. Sorting order is not changed via this method.

## Usage

Simply run the program and select the folder with your model