# cwc-minecraft #

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research built on top of Minecraft.

You can find our recently accepted ACL 2019 paper on this work [here](https://github.com/CogComp/cwc-minecraft/blob/master/Collaborative%20Dialogue%20in%20Minecraft_main.pdf) (supplementary [here](https://github.com/CogComp/cwc-minecraft/blob/master/Collaborative%20Dialogue%20in%20Minecraft_supp.pdf)).

## Installation ##

** Disclaimer: these instructions have been tested with macOS (Sierra and Mojave) + IntelliJ only. **
Add Windows stuff ... TODO

You can either install our Malmo fork using our pre-built version or build from source.

### Using our pre-built version ###
TODO ...
1. Download our pre-built version, for Windows or macOS.
2. Install the dependencies for your OS: [Windows](doc/install_windows.md), [macOS](doc/install_macosx.md)

### Building from source (skip if you are not a developer on this project) ###

Follow the instructions to build Malmö from source for your OS (make sure to clone this repository, `https://github.com/CogComp/cwc-minecraft.git`, instead of the original Malmo project):
* [Windows](doc/build_windows.md)
* [Linux](doc/build_linux.md)
* [MacOSX](doc/build_macosx.md)

## Python dependencies ##
Install the following:
- PyTorch (recommended `v0.4.1` or `v1.0.1` -- these are the ones we have tried out)
- NLTK

## Setting up your dev env (skip if you are not a developer on this project) ##
- Set up a workspace in IntelliJ by following [these instructions](https://bedrockminer.jimdo.com/modding-tutorials/set-up-minecraft-forge/set-up-fast-setup/), or by doing the following:
```
cd Minecraft
./gradlew setupDecompWorkspace
./gradlew idea
```

- Open the ``` Minecraft ``` directory as a project in IntelliJ. IntelliJ should automatically recognize that this is a Gradle project; if it asks if you want to import it as such, follow the directions to do so.


## Project structure ##

- Code and data: `build/install/Python_Examples`
- Screenshots: `Minecraft/run/screenshots`

Within `build/install/Python_Examples`:
- `gold-configurations`: All target strutures used in data collection -- stored as XML files. If you create new target structues those will be written here as well.
- `logs`: Any data collection sessions or demos you run will write log files here.

More on target strctures:
- [This](build/install/Python_Examples/configs_db.csv) contains a list of all target structures we used in data collection labeled as warmup, simple or complex (in increasing order of complexity). This was hand-labeled by us based on intuition -- factoring for things like number of blocks used, number of colors used, inherent structural complexity, number of floating blocks, etc. Hence, this is not a gold standard of labeling in any way. But it can still be a helpful guide when you are trying to pick out which target structures to try.
- [This](https://github.com/CogComp/cwc-minecraft-models/blob/master/data/logs/splits.json) (in our models repo) contains the data splits we used for modeling purposes. These splits were done across target structures. There are three sets in it: `train` (target structures used in training data), `test` (target structures used in test data) and `val` (target structures used in validation data). When testing the architect demo for example, you might want to avoid using target structures that have been used in training data.
- To see what a certain target stucture looks like, you can search within the folder housing our data on [Google Drive](https://drive.google.com/drive/folders/1zYXAO95f9qCyuUUd20OVkWOCcCOQ5uUp?usp=sharing). For example, if you are intersted in seeing what `C42.xml` looks like, search within the folder for "C42" and select any one of the pdf files displayed in the search results. Browse through its contents and pick out a chapter titled C42. The first section within that chapter should show you 4 canonical views of the structure.


## Running the Minecraft Client ##

There are two ways to do this:

1. On OSX, from terminal:
```
cd Minecraft
./launchClient.sh
```
(If using a different operating system, run the appropriate `launchClient` script.)

2. From within IntelliJ: run the `Minecraft Client` run configuration. If the project was imported as a Gradle project successfully, IntelliJ should already have this run configuration available to you.


## Running a Minecraft Data Collection session ###
The data collection sessions can either be run locally on a single machine (not recommended outside of development), or across multiple machines via LAN.

### Running locally ###
On a single machine, start up 3 Minecraft clients. Then run the following command:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv
```

where `sample_gold_configs.csv` contains a newline-separated list of target structure xml file paths to be played in the session (formatted as `target_structure_xml,existing_structure_xml`, where `existing_structure_xml` is optional). `existing_structure_xml` is the xml file path of a structure to be pre-loaded into the build region and is typically not needed. `sample_user_info.csv` can be safely ignored.

Although not recommended (because of the load this will create on a single machine), you can also run this session with up to 4 "Fixed Viewer" cameras that will take screenshots periodically from those angles (from the 4 canonical directions around the build region) as data is collected. To do so with 4 fixed viewers, start up 3 + 4 = 7 Minecraft clients, then run the following command:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=4 --fixed_viewer_csv=sample_fixed_viewer.csv
```

### Running via LAN ###
You will need:
* 1 machine for the Architect (requiring two Minecraft clients)
* 1 machine for the Builder (requiring one Minecraft client)
* 1 machine to run the Python session (requiring no clients)
* optionally, 1 machine to run 4 Fixed Viewer cameras (requires 4 Minecraft clients; this can be the same machine that runs the Python session)

The machines must be on the same local area network and reachable via ping (some networks don't allow for this).

You will need to find the IP addresses of each machine:
* MacOSX: `System Preferences > Network` will show the IP address under the `Status: Connected` message.
* Windows: run `ipconfig` and look at the `IPv4` address.

Edit `sample_user_info.csv` to reflect the correct IP addresses. For each line, in comma-separated fashion:
* ID of player
* name of player (this field is ignored, so anything works here)
* IP address
* port (default: 10000 should be used unless under special circumstances)
* player role (`architect/builder`), where the `architect` machine has 2 instances of Minecraft running and the `builder` has 1

A basic session with the above information can be run as follows:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --lan
```

where `sample_gold_configs.csv` contains a newline-separated list of target structure xml file paths to be played in the session (formatted as `target_structure_xml,existing_structure_xml`, where `existing_structure_xml` is optional). `existing_structure_xml` is the xml file path of a structure to be pre-loaded into the build region and is typically not needed.

Alternatively, you can run a session with up to 4 "Fixed Viewer" cameras that will take screenshots periodically from those angles (from the 4 canonical directions around the build region) as data is collected. To use these Fixed Viewer clients, launch 4 clients on the desired machine, and edit `sample_fixed_viewer.csv` to reflect the IP address of that machine. The current default uses `127.0.0.1` (localhost), i.e. the machine running the Python session will also act as the machine managing the Fixed Viewer clients. Port can remain 10000.

To run with Fixed Viewer clients, a session can be run as follows:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=4 --fixed_viewer_csv=sample_fixed_viewer.csv --lan
```

## Data format and postprocessing ##
Mention experiment ID here ... TODO
A data collection session for a given target structure will yield game log output in the form of a json file. A new directory will be created within `build/install/Python_Examples/logs` for this run of the game. The name will be a unique identifier for this run. Within it will be a json file called `raw-observations.json`. A subdirectory of the same name will also be created within `Minecraft/run/screenshots`. This will house all the screenshots taken during the game for the Minecraft clients on that machine. So, if you use multiple machines these screenshots will be distributed across machines. You will need to consolidate all of them on to one central machine where you house your data.

The json file will need to further post-processed to yield the final log files we would be interested in. To do this run `cwc_postprocess_observations.py` (remember to gather all screenshots from multiple machines if needed onto the machine which houses all data and where you are going to run the postprocessor). This will generate the following three files:
- `postprocessed-observations.json` -- Post-processed json log for the game
- `aligned-observations.json` -- Post-processed json log for the game with screenshot information added to each observation
- `log.txt` -- A human-readable log

The data format can be found at https://docs.google.com/document/d/1uo8oZbGhOuSfG5p_7rZlHfPwc2WOjIA0hcMzj70Qtoo/edit.

How to obtain latex/pdf files, dialogue.txt, dialogue-with-actions.txt ... TODO

## Creating your own target structures ##
To create target structures, you only need one open Minecraft client open on your local machine.

In this mode, instead of playing games where the target structures are dictated by the file paths `sample_gold_configs.csv`, you now need to specify the names of the __new__ target structures to be created in `sample_gold_configs.csv` (in the `target_structure_xml` column, the other one should remain unspecified). Note that if a given name of a new structure conflicts with any existing structures that exist at that file path, the game for that particular structure will fail before you are able to create a structure by that name. Each target structure is automatically saved at the specified file path after you build it as the Builder in Minecraft and end the mission by pressing __Ctrl+C in the Minecraft client__.

To run:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --create_target_structures
```

## Running the architect demo ##

To run: 
```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --architect_demo
```

This will basically enable an automated architect with everything else about the session being exactly the same. You just need to play the role of the Builder. In the game, whenever you need the Architect to speak, trigger it by sending a special chat message "xxx" from the Builder's side. The Architect will then generate one utterance.

The log files generated at the end of the game are the same as those in a data collection session.

## Useful debugging tips ##
### Disable screenshots ###
By default, the Minecraft clients take screenshots every time a block is picked up or put down or a chat message is sent/received (saved in `Minecraft/run/screenshots` with the associated experiment ID). This can fill up your disk quickly if you're not careful. If debugging, you can turn off screenshots by setting the `disableScreenshots` static variable found in `Minecraft/src/main/java/cwc/CwCMod.java` to `true` (by default, this is `false`). (This will be made into a more automatic solution in the future.)
