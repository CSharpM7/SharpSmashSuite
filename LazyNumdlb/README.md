# LazyNumdlb

This program edits the .numdlb file to make each mesh's material\_label value match that mesh's name. This also takes into account Blender exported models that typically suffix meshes with ".0n". As long as you don't have mesh.1xx, it should work.

## Usage

Place a numdlb file into the same directory as this program, then run the program. For your convenience, this also creates a copy of the old numdlb before making any changes.
