# Intro #
This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research built on top of Minecraft.

You can find our recently accepted ACL 2019 paper on this work [here](https://github.com/prashant-jayan21/minecraft-dialogue/blob/master/Collaborative%20Dialogue%20in%20Minecraft_main.pdf) (supplementary [here](https://github.com/prashant-jayan21/minecraft-dialogue/blob/master/Collaborative%20Dialogue%20in%20Minecraft_supp.pdf)).

# Installation #
## macOS (using our pre-built version) ##
**Disclaimer: These instructions have been tested with macOS (Sierra and Mojave) only.**

1. Download a pre-built version of our Malmö fork (apart from cloning this repo as well).
2. Install dependencies as documented [here](doc/install_macosx.md).

## Windows (building from source) ##
Follow the instructions [here](doc/build_windows.md) to build our Malmö fork from source (make sure to clone this repository, instead of the original Malmo project).

## Python dependencies ##
Install the following:
- PyTorch (recommended `v0.4.1` or `v1.0.1` -- these are the ones we have tried out)
- NLTK

# Project structure #
At a high-level, the data written by our systems is structured in the project as follows: 
- Within `build/install/Python_Examples`:
  - `gold-configurations`: All target strutures used in data collection -- stored as XML files. If you create new target structues those will be written here as well.
  - `logs`: Any data collection sessions or demos you run will write log files here.
- The screenshots will be written to `Minecraft/run/screenshots`.

All of our code also resides in `build/install/Python_Examples`. 

More on target structures:
- [This](build/install/Python_Examples/configs_db.csv) contains a list of all target structures we used in data collection labeled as warmup, simple or complex (in increasing order of complexity). This was hand-labeled by us based on intuition -- factoring for things like number of blocks used, number of colors used, inherent structural complexity, number of floating blocks, etc. Hence, this is not a gold standard of labeling in any way. But it can still be a helpful guide when you are trying to pick out which target structures to try.
- [This](https://github.com/prashant-jayan21/minecraft-dialogue-models/blob/master/data/logs/splits.json) (in our models repo) contains the data splits we used for modeling purposes. These splits were done across target structures. There are three sets in it: `train` (target structures used in training data), `test` (target structures used in test data) and `val` (target structures used in validation data). When testing the architect demo for example, you might want to avoid using target structures that have been used in training data.
- To see what a certain target stucture looks like, you can search within the folder housing our data on [Google Drive](https://drive.google.com/drive/folders/1zYXAO95f9qCyuUUd20OVkWOCcCOQ5uUp?usp=sharing). For example, if you are intersted in seeing what `C42.xml` looks like, search within the folder for "C42" and select any one of the pdf files displayed in the search results. Browse through its contents and pick out a chapter titled C42. The first section within that chapter should show you 4 canonical views of the structure.

# Running the Minecraft Client #
There are two ways to do this:

1. If building from source, from the project root, go to the `Minecraft` directory. Run the `launchClient` script (`./launchClient.sh` for macOS, `launchClient.bat` for Windows, etc.). 

2. If using our pre-built versions, do the same, but from within the previously mentioned unzipped folders -- make sure to use the right one for the right use case.

# Running a Minecraft Data Collection session #
The data collection sessions can either be run locally on a single machine (not recommended outside of development), or across multiple machines via LAN. We would need the following:
- Two Minecraft clients for the Architect -- one to view the build region and Builder and one to view the target structure
- One Minecraft client for the Builder
- Up to 4 optional Minecraft clients for the 4 "Fixed Viewers" -- these are basically clients containing cameras that will take screenshots periodically from the 4 canonical directions around the build region -- one camera per client

## Running locally ##
On a single machine, start up 3 Minecraft clients. Then run the following command:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv
```

where `sample_gold_configs.csv` contains a newline-separated list of target structure xml file paths to be played in the session (formatted as `target_structure_xml,existing_structure_xml`, where `existing_structure_xml` is optional). `existing_structure_xml` is the xml file path of a structure to be pre-loaded into the build region and is typically not needed. `sample_user_info.csv` can be safely ignored.

Although not recommended (because of the load this will create on a single machine), you can also run this session with up to 4 "Fixed Viewers". To do so with 4 Fixed Viewers, start up 3 + 4 = 7 Minecraft clients, then run the following command:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=4 --fixed_viewer_csv=sample_fixed_viewer.csv
```

## Running via LAN ##
You will need:
* 1 machine for the Architect (requiring two Minecraft clients)
* 1 machine for the Builder (requiring one Minecraft client)
* 1 machine to run the Python session (requiring no clients)
* optionally, 1 machine to run up to 4 Fixed Viewer cameras (requires 4 Minecraft clients; this can be the same machine that runs the Python session)

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

Alternatively, you can run a session with up to 4 "Fixed Viewer" cameras as well. To use these Fixed Viewer clients, launch 4 clients on the desired machine, and edit `sample_fixed_viewer.csv` to reflect the IP address of that machine. The current default uses `127.0.0.1` (localhost), i.e. the machine running the Python session will also act as the machine managing the Fixed Viewer clients. Port can remain 10000.

To run with Fixed Viewer clients, a session can be run as follows:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --num_fixed_viewers=4 --fixed_viewer_csv=sample_fixed_viewer.csv --lan
```

# Data format and postprocessing #
A data collection session (or any of our demos for that matter) for a given target structure will yield game log output in the form of a json file. A new directory will be created within `build/install/Python_Examples/logs` for this run of the game. The name will be a unique identifier for this run denoting the experiment/game ID. Within it will be a json file called `raw-observations.json`. A subdirectory of the same name will also be created within `Minecraft/run/screenshots`. This will house all the screenshots taken during the game for the Minecraft clients on that machine. So, if you use multiple machines these screenshots will be distributed across machines. You will need to gather all of them on to one central machine where you house your data. These can all be gathered into the `Minecraft/run/screenshots/<experiment-ID>` subdirectory on that machine.

The json file will need to further post-processed to yield the final log files we would be interested in. To do this run `cwc_postprocess_observations.py` (remember to gather all screenshots from multiple machines if needed onto the machine which houses all data and where you are going to run the postprocessor). More specifically, run:
```
python cwc_postprocess_observations.py logs/<experiment-ID> --screenshots_dir=../../../Minecraft/run/screenshots/<experiment-ID>
```

This will generate the following three files in `build/install/Python_Examples/logs/<experiment-ID>`:
- `postprocessed-observations.json` -- Post-processed json log for the game
- `aligned-observations.json` -- Post-processed json log for the game with screenshot information added to each observation
- `log.txt` -- A human-readable log

The data format can be found [here](https://drive.google.com/open?id=1-__GYErq0uKiO3n_3jlfY9NtJ_Eu1KLh).

## Producing LaTeX files with dialogues + screenshots ##
From a given directory of JSON logfiles, you can produce LaTeX files that, when compiled, produce PDF files containing all dialogues within that directory in a graphical format (e.g., [this PDF](https://drive.google.com/open?id=10AUrzjHHO5tSNeVmTayWowYN8DvBOQsL)). The script produces both simple PDF files (which contain only a screenshot of the final game state as well as the full dialogue) as well as more complete PDFs (containing the former as well as a step-by-step view of each dialogue as it is played out).

To obtain these LaTeX files, run:
```
python3 logs_to_latex.py -l /path/to/jsons/dir -s /path/to/screenshots/dir -o output_file_name.tex
```

It is recommended to only run this on a small subset of JSON logs (as opposed to the entire dataset), as the resulting LaTeX files can become quite large. The resulting LaTeX files (`output_file_name.tex` and `output_file_name-simplified.tex`) are stored in a `tex/` directory that lives within the directory from which the script was run.

## Producing text-only dialogue files ##
A simpler way of producing human-readable dialogues is to run the following:
```
python3 get_text_dialogues.py -l /path/to/jsons/dir -s /path/to/screenshots/dir -o output_file_name.txt
```

This script produces simple text files of full dialogues indexed by their dialogue ID. The resulting files (`output_file_name-dialogue.txt`, for only text chat; and `output_file_name-dialogue_with_actions.txt`, for the chat interleaved with the Builder's actions) are saved inn a `dialogues/` directory that lives within the directory from which the script was run.

# Creating your own target structures #
To create target structures, you only need one open Minecraft client open on your local machine.

In this mode, instead of playing games where the target structures are dictated by the file paths `sample_gold_configs.csv`, you now need to specify the names of the __new__ target structures to be created in `sample_gold_configs.csv` (in the `target_structure_xml` column, the other one should remain unspecified). Note that if a given name of a new structure conflicts with any existing structures that exist at that file path, the game for that particular structure will fail before you are able to create a structure by that name. Each target structure is automatically saved at the specified file path after you build it as the Builder in Minecraft and end the mission by pressing __Ctrl+C in the Minecraft client__.

To run:

```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --create_target_structures
```

# Running the architect demo #
To run: 
```
python cwc_run_session.py sample_user_info.csv sample_gold_configs.csv --architect_demo
```

This will basically enable an automated architect with everything else about the session being exactly the same as data collection. You just need to play the role of the Builder. In the game, whenever you need the Architect to speak, trigger it by sending a special chat message "xxx" from the Builder's side. The Architect will then generate one utterance.

The log files generated at the end of the game are the same as those in a data collection session. You'll need to post-process them further as mentioned above.

# Useful debugging tips #
## Disable screenshots ##
By default, the Minecraft clients take screenshots every time a block is picked up or put down or a chat message is sent/received (saved in `Minecraft/run/screenshots` with the associated experiment ID). This can fill up your disk quickly if you're not careful. If debugging, you can turn off screenshots by setting the `disableScreenshots` static variable found in `Minecraft/src/main/java/cwc/CwCMod.java` to `true` (by default, this is `false`). (This will be made into a more automatic solution in the future.)
