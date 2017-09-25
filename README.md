# cwc-minecraft #

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research
built on top of Minecraft.



## Installation ##

** Disclaimer: these instructions have been tested with OSX + Intellij only.

1) Clone cwc-minecraft: ``` git clone https://gitlab.engr.illinois.edu/hockenmaier/cwc-minecraft.git ```

2) Follow the instructions to build Malmö from source for your OS, skipping the cloning step: [Windows](doc/build_windows.md), [Linux](doc/build_linux.md), [MacOSX](doc/build_macosx.md).

3) Set up a workspace in Intellij by following [these instructions](https://bedrockminer.jimdo.com/modding-tutorials/set-up-minecraft-forge/set-up-fast-setup/), or do the following:
```
cd Minecraft
./gradlew setupDecompWorkspace
./gradlew idea
```

4) Import the ``` Minecraft ``` directory as a project into Intellij. Intellij should automatically recognize that this is a Gradle project and ask if you want to import it as such; follow the directions to do so.

If building and setup is successful, you should have access to two run configurations: Minecraft Client and Minecraft Server, which you can use to run the Minecraft server with Forge mods from within Intellij.
