# cwc-minecraft #

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research
built on top of Minecraft.



## Installation ##

1) Follow the instructions to clone and build Malmö from source for your OS: [Windows](doc/build_windows.md), [Linux](doc/build_linux.md), [MacOSX](doc/build_macosx.md).
2) Set up a workspace in Intellij by following [these instructions](https://bedrockminer.jimdo.com/modding-tutorials/set-up-minecraft-forge/set-up-fast-setup/), or the following:
```
cd cwc-minecraft/Minecraft
chmod +x gradlew
./gradlew setupDecompWorkspace
./gradlew idea
```
