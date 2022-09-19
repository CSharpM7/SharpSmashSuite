# Lazy Config

Creates a config.json for use with acropolis. This has been updated to work with characters and stage directory addition. Character directory addition is currently untested.

## Usage

This is intended to be used on SDcards, or workspaces that are set up similarly to SDcards. (They should have a stage or fighter folder, and inside there should be normal/model/...)

Run the program, it will prompt you to select the root of your mod folder. This will generate a `config.json` file and proceed to open the location where it is saved in file explorer. For fighters, if you only have one assigned slot (ie only a mod for c00 or c04, etc), you can "clone" the config entries across all slots. So your c00 mod config will now work for slot c04. For your convenience, the program will also remember the last place you saved a config file to make the process slightly faster when iterating

## Directory Addition
Currently this program "supports" directory addition for both fighters and stages with these caveats:
For fighters, you still need to any information for sound and ui files/folders, as well as fill out the "infobase" section
For stages, it will automatically detect new directories from the `files_stage.txt` file. Will also add effects folders, but effects may or may not work with directory addition
