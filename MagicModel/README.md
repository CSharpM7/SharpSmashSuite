# Magic Model

This program edits the .numdlb model file to make each model's material_label value match that mesh's name. This also takes into account Blender exported models that typically suffix meshes with ".0n". As long as you don't have mesh.1xx, it should work.
This program also edits .numshb mesh files and .numatb material files to sort each entry alphabetically.
Numdlb and Numshb files will also have a backup created

## Usage

Simply run the program and select the folder with your model