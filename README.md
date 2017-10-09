# cwc-minecraft #

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research
built on top of Minecraft.



## Installation ##

** Disclaimer: these instructions have been tested with OSX + IntelliJ only. **

1. Clone cwc-minecraft: ``` git clone https://github.com/CogComp/cwc-minecraft.git ```

2. Follow the instructions to build Malmö from source for your OS, skipping the cloning step: [Windows](doc/build_windows.md), [Linux](doc/build_linux.md), [MacOSX](doc/build_macosx.md). 
When running `make install`, you may run into a particular error involving copying the file `libMalmoNETNative.so`. There are a couple of solutions:

    i. From the project directory, ``` cp build/Malmo/src/CSharpWrapper/MalmoNETNative.so build/Malmo/src/CSharpWrapper/libMalmoNETNative.so ```
    The assumption is that the library is the same, but somehow had a slight change of name that the build script wasn't expecting.
    
    
    ii. Disable the C# part of the build by setting `INCLUDE_CSHARP` to `OFF` in `CMakeLists.txt` as done in https://gitlab.engr.illinois.edu/hockenmaier/cwc-minecraft/commit/a02b5722576f9d78f8886ba6ca038e6cb047be57


3. Set up a workspace in IntelliJ by following [these instructions](https://bedrockminer.jimdo.com/modding-tutorials/set-up-minecraft-forge/set-up-fast-setup/), or by doing the following:
```
cd Minecraft
./gradlew setupDecompWorkspace
./gradlew idea
```

4. Open the ``` Minecraft ``` directory as a project in IntelliJ. IntelliJ should automatically recognize that this is a Gradle project; if it asks if you want to import it as such, follow the directions to do so.



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
