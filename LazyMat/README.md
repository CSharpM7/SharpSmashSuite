# LazyMAT

This excel sheet creates a material file (numatb) based on a list of shaders, materials and textures. It works best after creating a list of materials and textures from the Blender Smash Sharp Suite plugin

## Quick Overview

This program converts a large batch of nutexb texture files into a numatb material file to use with models. You can also create a list of prefabricated shaders to use, so if you find yourself reusing similar shaders throughout your mod, you might want to place it in the Shaders folder.  
Note that this will not set up a numdlb file, so you will still have to find a way to assign materials to each mesh through StudioSB or Blender.  
This program hasn't been thoroughly tested, but I figured someone could be able to make use of it and not have to spend several minutes of their life creating a matlab xml file from scratch!

## Prerequisites

You'll need to have your nutexb files created beforehand, you might want to look at jam's img2nutexb to batch convert images.  
You also need to have MatLab somewhere on your machine. Grab it here.  
You'll also want StudioSB to be able to assign materials to your meshes after you're done.

## Usage

Check the wiki [here](https://github.com/CSharpM7/SharpSmashSuite/wiki/LazyMat)
