# Steve Spec

Lets you view and edit block boundaries for Steve on most stages


## Prerequisites
You'll need:
- ArcExplorer, as well as a dump of the `/stage/common/shared/param/` folder
- Parcel for creating patches of the `groundconfig.prc` file for each of your mods
- Yamlvd to automatically retrieve Camera Boundary info, or StudioSB to find out the boundaries for your stage
- pyyaml (pip install) to read yaml files

## Usage

When booting for the first time, the program will ask you to locate ArcExplorer, Yamlvd and Parcel. Afterwords, it will ask for the workspace for your mod. This program will also remember the last used workspace on launch. Make sure your mod has a `stage/[stage_name]/normal/param` folder, and that folder should have an lvd or yaml file in it. If you don't have a yaml file, this program can run yamlvd for you. If yamlvd doesn't work with this stage (ie WarioWare), you can manually enter data for the camera,blastzone,and stage radius data.