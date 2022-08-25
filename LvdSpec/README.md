# LVD Spec

Lets you view lvd files (as long as they can be used with yamlvd) and edit block boundaries for Steve on most stages


## Dependencies
You'll need:
- [ArcExplorer](https://github.com/ScanMountGoat/ArcExplorer), as well as a dump of the `/stage/common/shared/param/` folder
- [Parcel](https://github.com/blu-dev/parcel/releases/tag/v1.0.0) for creating patches of the `groundconfig.prc` file for each of your mods
- [Yamlvd](https://github.com/jam1garner/lvd-rs/releases) to automatically retrieve Camera Boundary info, or StudioSB to find out the boundaries for your stage
- pyyaml (pip install) to read yaml files

## Usage

When booting for the first time, the program will ask you to locate ArcExplorer, Yamlvd and Parcel. This is so we can retrieve the original groundconfig.prc, parse level data, and export the changes you make as a patch file. You'll be greated with a blank canvas, with most of the settings greyed out (as there is no level loaded). Go to File>Load Stage Collision File and select a `.yaml` file to load. If your stage doesn't have a yaml file, you can select a `.lvd` file and this program will run yamlvd for you. If yamlvd doesn't work with this stage (ie Final Destination, WarioWare), you can manually enter data for the camera,blastzone,and stage data.

Edit the Steve LVD Settings values as you see fit. You can also use the Wizard button to automatically set these values. The Wizard will require that your Stage Data values are accurate, so double check to make sure these values make sense.

When you're finished, go to File>Export Patch File. This will create a patch file in whichever mod directory you are currently in under stage/common/shared/param. The name will be groundconfig + the name of the yaml file. The program will read from this file whenever you load the same yaml file again. Make sure you rename the new patch file after moving it to your mod on your SD Card. All changes will be saved to the groundconfig.prc in the LVDSpec folder, so if you're making a large mod pack, you might want to use this file instead of trying to combine several different patch files.

## Terms

| |
| :- | 
| **Steve LVD Settings** |
| **material**: Material type of the weakest block |
| **origin**: Used to offset the steve grid. Should be related to Stage Radius and FloorY|
| **cell sensitivity**: A value between 0 and 1. Not sure what it does|
| **line offset**: A value between 0 and 10. Not sure what it does |
| **Side/Top/Bottom**: Distance from Camera where Steve cannot build a block |
| **Camera Boundaries** |
| **Left/Right/Top/Bottom**: Boundaries for the Camera of the stage |
| **Center**: Center X and Y positions of the camera |
| **Blastzone Boundaries** |
| **Left/Right/Top/Bottom**: Boundaries for the Blastzone of the stage |
| **Stage Data** |
| **Radius**: Width of the stage divided by 2 |
| **Top**: Highest platform; often the highest spawn point |
| **Bottom**: Lowest part of the main stage. Walled stages should have their Bottom value lower than their Camera.Bottom value |
| **FloorY**: Y position of the lowest floor of the stage, often the lowest spawn point |
| **Origin**: Often 0,0; some stages may be shifted up by 200 to avoid hardcoded vertices. Set this to a multiple of 10 so that the Steve Grid shows properly |