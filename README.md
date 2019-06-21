# cwc-minecraft #

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo), a platform for Artificial Intelligence experimentation and research
built on top of Minecraft.

<<<<<<< HEAD
=======
[![Join the chat at https://gitter.im/Microsoft/malmo](https://badges.gitter.im/Microsoft/malmo.svg)](https://gitter.im/Microsoft/malmo?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Build Status](https://travis-ci.org/Microsoft/malmo.svg?branch=master)](https://travis-ci.org/Microsoft/malmo) [![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/Microsoft/malmo/blob/master/LICENSE.txt)
----
    
## Getting Started ##

It is now possible to use ```pip3 install malmo``` to install Malmo as a python package: [Pip install for Malmo](https://github.com/Microsoft/malmo/blob/package/scripts/python-wheel/README.md). Once installed, the malmo Python module can be used to download source and examples and start up Minecraft with the Malmo game mod. Alternatively, a pre-built version of Malmo can be installed as follows:

1. [Download the latest *pre-built* version, for Windows, Linux or MacOSX.](https://github.com/Microsoft/malmo/releases)   
      NOTE: This is _not_ the same as downloading a zip of the source from Github. _Doing this **will not work** unless you are planning to build the source code yourself (which is a lengthier process). If you get errors along the lines of "`ImportError: No module named MalmoPython`" it will probably be because you have made this mistake._

2. Install the dependencies for your OS: [Windows](doc/install_windows.md), [Linux](doc/install_linux.md), [MacOSX](doc/install_macosx.md).

3. Launch Minecraft with our Mod installed. Instructions below.

4. Launch one of our sample agents, as Python, C#, C++ or Java. Instructions below.

5. Follow the [Tutorial](https://github.com/Microsoft/malmo/blob/master/Malmo/samples/Python_examples/Tutorial.pdf) 

6. Explore the [Documentation](http://microsoft.github.io/malmo/). This is also available in the readme.html in the release zip.

7. Read the [Blog](http://microsoft.github.io/malmo/blog) for more information.

If you want to build from source then see the build instructions for your OS: [Windows](doc/build_windows.md), [Linux](doc/build_linux.md), [MacOSX](doc/build_macosx.md).

----

## Problems: ##

We're building up a [Troubleshooting](https://github.com/Microsoft/malmo/wiki/Troubleshooting) page of the wiki for frequently encountered situations. If that doesn't work then please ask a question on our [chat page](https://gitter.im/Microsoft/malmo) or open a [new issue](https://github.com/Microsoft/malmo/issues/new).
>>>>>>> malmo/version-35-5


## Installation ##

** Disclaimer: these instructions have been tested with OSX + IntelliJ only. **

1. Clone cwc-minecraft: ``` git clone https://github.com/CogComp/cwc-minecraft.git ```

2. Follow the instructions to build Malmö from source for your OS, skipping the cloning step: [Windows](doc/build_windows.md), [Linux](doc/build_linux.md), [MacOSX](doc/build_macosx.md). 
When running `make install`, you may run into a particular error involving copying the file `libMalmoNETNative.so`. There are a couple of solutions:

<<<<<<< HEAD
    i. From the project directory, ``` cp build/Malmo/src/CSharpWrapper/MalmoNETNative.so build/Malmo/src/CSharpWrapper/libMalmoNETNative.so ```
    The assumption is that the library is the same, but somehow had a slight change of name that the build script wasn't expecting.
    
    
    ii. Disable the C# part of the build by setting `INCLUDE_CSHARP` to `OFF` in `CMakeLists.txt` as done in https://github.com/CogComp/cwc-minecraft/commit/a02b5722576f9d78f8886ba6ca038e6cb047be57


3. Set up a workspace in IntelliJ by following [these instructions](https://bedrockminer.jimdo.com/modding-tutorials/set-up-minecraft-forge/set-up-fast-setup/), or by doing the following:
```
cd Minecraft
./gradlew setupDecompWorkspace
./gradlew idea
```

4. Open the ``` Minecraft ``` directory as a project in IntelliJ. IntelliJ should automatically recognize that this is a Gradle project; if it asks if you want to import it as such, follow the directions to do so.



## Running the Minecraft Client ##
=======
On MacOSX we currently only support the system python, so please use `/usr/bin/python run_mission.py` if not the default. 

#### Running a C++ agent: ####

`cd Cpp_Examples`

To run the pre-built sample:

`run_mission` (on Windows)  
`./run_mission` (on Linux or MacOSX)

To build the sample yourself:

`cmake .`  
`cmake --build .`  
`./run_mission` (on Linux or MacOSX)  
`Debug\run_mission.exe` (on Windows)

#### Running a C# agent: ####

To run the pre-built sample (on Windows):

`cd CSharp_Examples`  
`CSharpExamples_RunMission.exe`

To build the sample yourself, open CSharp_Examples/RunMission.csproj in Visual Studio.
>>>>>>> malmo/version-35-5

There are two ways to do this:

<<<<<<< HEAD
1. On OSX, from terminal:
``` 
cd Minecraft
./launchClient.sh
=======
`cd CSharp_Examples`

Then, on Windows:  
```
msbuild RunMission.csproj /p:Platform=x64
bin\x64\Debug\CSharpExamples_RunMission.exe
```

#### Running a Java agent: ####

`cd Java_Examples`  
`java -cp MalmoJavaJar.jar:JavaExamples_run_mission.jar -Djava.library.path=. JavaExamples_run_mission` (on Linux or MacOSX)  
`java -cp MalmoJavaJar.jar;JavaExamples_run_mission.jar -Djava.library.path=. JavaExamples_run_mission` (on Windows)

#### Running an Atari agent: (Linux only) ####

```
cd Python_Examples
python ALE_HAC.py
>>>>>>> malmo/version-35-5
```
(If using a different operating system, run the appropriate `launchClient` script.)

2. From within IntelliJ: run the `Minecraft Client` run configuration. If the project was imported as a Gradle project successfully, IntelliJ should already have this run configuration available to you.



## Running the Python prototype missions ##

The [Python_Examples directory](https://gitlab-beta.engr.illinois.edu/hockenmaier/cwc-minecraft/tree/master/build/install/Python_Examples) contains sample missions prototyping features required as part of the CWC project.
These are written in Python using the Malmo API and borrow ideas from the [tutorial examples](https://github.com/Microsoft/malmo/tree/master/Malmo/samples/Python_examples) in the original Malmo project.
Running a mission involves 2 steps: 

1. Run the Minecraft client as mentioned above. You may need to run another one for 2 agent missions.

2. Run the Python code. As of now we recommend using Python 2 (using Python 3 has some issues which we intend to resolve soon -- follow [this issue](https://gitlab-beta.engr.illinois.edu/hockenmaier/cwc-minecraft/issues/6)).
