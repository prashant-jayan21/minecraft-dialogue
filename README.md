# cwc-minecraft #

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research
built on top of Minecraft.


## Installation ##

** Disclaimer: these instructions have been tested with OSX + IntelliJ only. **

Follow the instructions to build Malmö from source for your OS (make sure to clone this repository, `https://github.com/CogComp/cwc-minecraft.git`, instead of the original Malmo project):
* [Windows](doc/build_windows.md)
* [Linux](doc/build_linux.md)
* [MacOSX](doc/build_macosx.md)

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

## Running the Minecraft Client ##

There are two ways to do this:

1. On OSX, from terminal:
```
cd Minecraft
./launchClient.sh
```
(If using a different operating system, run the appropriate `launchClient` script.)

2. From within IntelliJ: run the `Minecraft Client` run configuration. If the project was imported as a Gradle project successfully, IntelliJ should already have this run configuration available to you.



## Running the Python prototype missions ##

The [Python_Examples directory](https://gitlab-beta.engr.illinois.edu/hockenmaier/cwc-minecraft/tree/master/build/install/Python_Examples) contains sample missions prototyping features required as part of the CWC project.
These are written in Python using the Malmo API and borrow ideas from the [tutorial examples](https://github.com/Microsoft/malmo/tree/master/Malmo/samples/Python_examples) in the original Malmo project.
Running a mission involves 2 steps:

1. Run the Minecraft client as mentioned above. You may need to run another one for 2 agent missions.

2. Run the Python code. As of now we recommend using Python 2 (using Python 3 has some issues which we intend to resolve soon -- follow [this issue](https://gitlab-beta.engr.illinois.edu/hockenmaier/cwc-minecraft/issues/6)).

## Running a Minecraft Data Collection session ###
The data collection sessions can either be run locally on a single machine (not recommended outside of development), or across multiple machines via LAN.

### Running locally ###
On a single machine, start up 3 Minecraft clients. Then run the following command:

```
/usr/bin/python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --mode=data_collection
```

where `sample_gold_configs.csv` contains a newline-separated list of target structure xml file paths to be played in the session (formatted as `target_structure_xml,existing_structure_xml`, where `existing_structure_xml` is optional). `sample_user_info.csv` can be safely ignored.

Although not recommended, you can also run this session with "Fixed Viewer" cameras that will take screenshots periodically from those angles as data is collected. To do so, start up 7 Minecraft clients, then run the following command:

```
/usr/bin/python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=4 --fixed_viewer_csv=sample_fixed_viewer.csv --mode=data_collection
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
/usr/bin/python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --lan --mode=data_collection
```

where `sample_gold_configs.csv` contains a newline-separated list of target structure xml file paths to be played in the session (formatted as `target_structure_xml,existing_structure_xml`, where `existing_structure_xml` is optional).

Alternatively, you can run a session with "Fixed Viewer" cameras that will take screenshots periodically from those angles as data is collected. To use these Fixed Viewer clients, launch 4 clients on the desired machine, and edit `sample_fixed_viewer.csv` to reflect the IP address of that machine. The current default uses `127.0.0.1` (localhost), i.e. the machine running the Python session will also act as the machine managing the Fixed Viewer clients.

To run with Fixed Viewer clients, a session can be run as follows:

```
/usr/bin/python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=4 --fixed_viewer_csv=sample_fixed_viewer.csv --lan --mode=data_collection
```

## Data format and postprocessing ##
A data collection session for a given target structure will yield game log output in the form of a json file. A new directory will be created within `build/install/Python_Examples/logs` for this run of the game. The name will be a unique identifier for this run. Within it will be a json file called `raw-observations.json`. A subdirectory of the same name will also be created within `Minecraft/run/screenshots`. This will house all the screenshots taken during the game for the Minecraft clients on that machine. So, if you use multiple machines these screenshots will be distributed across machines. You will need to consolidate all of them on to one central machine where you house your data.

The json file will need to further post-processed to yield the final log files we would be interested in. To do this run `cwc_postprocess_observations.py` (remember to gather all screenshots from multiple machines if needed onto the machine which houses all data and where you are going to run the postprocessor). This will generate the following three files:
- `postprocessed-observations.json` -- Post-processed json log for the game
- `aligned-observations.json` -- Post-processed json log for the game with screenshot information added to each observation
- `log.txt` -- A human-readable log

The data format can be found at https://docs.google.com/document/d/1uo8oZbGhOuSfG5p_7rZlHfPwc2WOjIA0hcMzj70Qtoo/edit.

How to get pdf files, etc. -- TODO

## Creating your own target structures ##
To create target structures, you only need one open Minecraft client open on your local machine.

In this mode, instead of playing games where the target structures are dictated by the file paths in `sample_gold_configs.csv`, you now need to specify the names of the __new__ target structures to be created in `sample_gold_configs.csv`. Note that if a given name of a new structure conflicts with any existing structures that exist at that file path, the game for that particular structure will fail before you are able to create a structure by that name. Each target structure is automatically saved at the specified file path after you build it as the Builder in Minecraft and end the mission by pressing __Ctrl+C in the Minecraft client__.

To run:

```
/usr/bin/python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --mode=create_target_structures
```

## Useful debugging tips ##
### Disable screenshots ###
By default, the Minecraft clients take screenshots every time a block is picked up or put down or a chat message is sent/received (saved in `Minecraft/run/screenshots` with the associated experiment ID). This can fill up your disk quickly if you're not careful. If debugging, you can turn off screenshots by setting the `disableScreenshots` static variable found in `Minecraft/src/main/java/cwc/CwCMod.java` to `true` (by default, this is `false`). (This will be made into a more automatic solution in the future.)

## Running the architect demo ##

Run `cwc_run_session.py` with `--mode=architect_demo`. This will basically enable an automated architect with everything else about the session being exactly the same. You just need to play the role of the Builder. In the game, whenever you need the Architect to speak, trigger it by sending a special chat message "xxx" from the Builder's side. The Architect will then generate one utterance.

## Running the builder demo ##

Run `cwc_run_session.py` with `--mode=builder_demo`. More specifically, it will be 
`python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=0 --mode=builder_demo`

This command will enable the architect to provide natural language instructions to the builder. i.e. `build a blue row of size 3`. Then the builder will take this natural language uttarnce into a logical form. They will the inputs for the planner. Finally, the planner will generate instructions which will be executed by the builder.

The log files generated at the end of the game are the same as those in a data collection session.

## required packages
The following packages will be required to run the agents

- pytorch
- nltk (`pip install -U nltk`)
