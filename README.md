# SharpSmashSuite

![](https://user-images.githubusercontent.com/13909643/170925201-fde9546b-fd43-4415-b293-c594634fb7bd.png)

## Required Software

Tested on Windows, but should work on most OSs that can run Python 3.9+

Python 3.9+

[img2nutexb](https://github.com/jam1garner/img2nutexb) - Program required for using img2nutexbGUI

[ssbh\_data\_py](https://github.com/ScanMountGoat/ssbh_data_py) - Running LazyNumdlb

[MatLab and CrossMod](https://github.com/Ploaj/SSBHLib)  - (Not the math software) Running LazyMat and previewing models

[StudioSB](https://github.com/Ploaj/StudioSB) - Importing models and creating numdlb files

## Installation

Grab from the latest [releases](https://github.com/CSharpM7/SharpSmashSuite/releases)

The following programs have been updated in the source code, but not the current release:

- Magic Model (LazyNumdlb): Now alphabetically sorts meshes and materials. No longer requires a copy of a .numdlb to be present in the folder, but instead will prompt the user to select a folder that contains the model,mesh and material files

### Modding compatibility

| | Stage Modding | Character Modding |
| :---:| :----:| :----:|
| Blender SSS | :heavy_check_mark: | :question: |
| LazyMat | :heavy_check_mark: | :question: |
| LazyConfig | :heavy_check_mark: | :heavy_check_mark: |
| MagicModel | :heavy_check_mark: | :question: |
| img2nutexbGUI | :heavy_check_mark: | :heavy_check_mark: |
| NumatbGUI | :heavy_check_mark: | :heavy_check_mark: |
| UI Retrieve | :heavy_check_mark: | :heavy_check_mark: |

## Getting Started

Each folder in the repo has a README.md to look at that serves as a quick overview of the program. Additionally, the wiki will be updated regularly with additional topics on the Blender plugin

# Workflow

### High Level:

Our end goal is to be able to quickly prototype stage designs through the use of Blender and Python. To do this, we'll need to export models, create a list of materials and textures to build a numatb file, and manipulate a numdlb file so that we can automatically assign materials to meshes.

### Step By Step Overview:

**Importing the model:**
1.  Blender SSS - Prepare your models. This blender program can properly separate objects by material, group objects by material without losing UV maps, rename meshes to their material's name, and export a list of material and texture names
2.  StudioSB - Import your meshes from Blender, export a numdlb and numshb file

**SharpSuite.py**
This is when you can use SharpSuite.py to create a quick prototype to see how your model looks in-game. This would skip steps using img2nutexbGUI and Magic Model. I still recommend using LazyMat if you have access to excel to properly assign shaders to materials.

**Creating materials and textures:**
1.  LazyMat - Create a numatb file. You'll use the exported material list to fill this out. This can be customized to keep a list of shaders.
2.  Img2nutexbGUI - Convert several images at once to nutexb files

**Preview:**
1.  CrossMod/SSBH_Editor - After using LazyMat, LazyNumdlb, and StudioSB, preview the model

**Finishing:**
1.  MagicModel - Reassigns meshs' their material label based on that mesh's name, and alphabetically sorts mesh and material files. This only works if Blender SSS was used on the mesh.
2.  LazyConfig - Creates a config.json to be used with file addition
3.  UI Retrieve - Easily retrieves all relevant UI for your mod so you can replace it when finished

# Special Thanks

[jam1garner](https://github.com/jam1garner) - original img2nutexb program

[SMG](https://github.com/ScanMountGoat) - ssbh\_data\_py developer, example projects used to help creating LazyNumdlb

[Smash Ultimate Research Group](https://github.com/ultimate-research) - developing tools to help make this possible
