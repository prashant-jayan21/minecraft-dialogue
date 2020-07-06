# Introduction #
This repository contains data collection code for the ACL 2019 paper [Collaborative Dialogue in Minecraft](https://www.aclweb.org/anthology/P19-1537) (supplementary material available [here](https://www.aclweb.org/anthology/attachments/P19-1537.Supplementary.pdf)). 

More details on this work, as well as a link to download [the full Minecraft Dialogue corpus](https://drive.google.com/drive/folders/16lDzswcQh8DR2jkQJdoVTK-RyVDFPHKa), can be found at [this landing page](http://juliahmr.cs.illinois.edu/Minecraft/). Related modeling code can be found in [this repository](https://github.com/prashant-jayan21/minecraft-dialogue-models).

If you use this work, please cite:
```
@inproceedings{narayan-chen-etal-2019-collaborative,
    title = "Collaborative Dialogue in {M}inecraft",
    author = "Narayan-Chen, Anjali  and
      Jayannavar, Prashant  and
      Hockenmaier, Julia",
    booktitle = "Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/P19-1537",
    pages = "5405--5415",
}
```

This repository is forked from [Project Malmö](https://github.com/Microsoft/malmo) (Johnson et al., 2016), a platform for Artificial Intelligence experimentation and research built on top of Minecraft.

# Installation #
## macOS (using our pre-built version) ##
**Disclaimer: These instructions have been tested with Sierra and Mojave only.**

1. Download the pre-built version of our Malmö fork from https://github.com/prashant-jayan21/minecraft-dialogue/releases/tag/minecraft-client (apart from cloning this repo as well):
- `main-client.zip` -- Minecraft client for running the Architect agent, data collection or creating target structures

You'll then need to run the Minecraft client from the unzipped folder.

2. Install dependencies as documented [here](doc/install_macosx.md).

## Windows (building from source) ##
Follow the instructions [here](doc/build_windows.md) to build our Malmö fork from source (make sure to clone this repository, instead of the original Malmo project).

## Python dependencies ##
Install the following:
- [PyTorch](https://pytorch.org/get-started/locally/) (we recommend `v0.4.1` or `v1.0.1` -- these are the ones we have tried out)
- [NLTK](https://www.nltk.org/install.html)

## Boost ##
This project requires Boost 1.69 specifically to be installed. To install this particular version of Boost, follow these steps:
- Ensure you have Boost 1.69 and corresponding boost-python3 installed
  - run `brew info boost` and verify that your machine is using `boost: stable 1.69.0`. Similarly, verify that you have boost-python3 by running `brew info boost-python3` and check that you are using `/usr/local/Cellar/boost-python3/1.69.0_1 (459 files, 17.4MB) *`.
  - If all good, you can build the project from source as usual. If not, follow the instructions below to fix your installation of Boost.
  - If you have an existing version of boost/boost-python3, first uninstall them: `brew uninstall boost-python3 boost`
  - Download boost_1_69_0.tar.gz from https://www.boost.org/users/history/version_1_69_0.html
  - Move the tar to your homebrew cache: `mv boost_1_69_0.tar.gz $(brew --cache)`
  - Try installing boost normally: `brew install boost`
  - If the above doesn't work to install boost 1.69 (e.g. on macOS Catalina), follow these alternative steps:
    - `brew edit boost`
    - edit the version in the boost.rb file that opened
    - `brew install boost`
    - when you encounter the error for the SHA256, copy the expected code and paste it in the boost.rb
    - `brew install boost` again. This should download the boost 1.69 source tarball and start the manual installation process.
  - Copy and save locally the following script as `boost-python3.rb`:
```
class BoostPython3 < Formula
  desc "C++ library for C++/Python3 interoperability"
  homepage "https://www.boost.org/"
  url "https://sourceforge.net/projects/boost/files/boost/1.69.0/boost_1_69_0.tar.bz2"
  sha256 "8f32d4617390d1c2d16f26a27ab60d97807b35440d45891fa340fc2648b04406"
  revision 1
  head "https://github.com/boostorg/boost.git"

  bottle do
    cellar :any
    sha256 "df5614e51cd271c477ac5a614a196180637c22f9c88b38b05c23e28a46db2c25" => :mojave
    sha256 "fc247eaaa4e2cbe16f3acf5d88485f795fee38872fdcab2bbb0012340c5e4c30" => :high_sierra
    sha256 "d1ff523535c6e1fafe64007fbe835c1432ac86ab1e5779b12288f9c4d57506b3" => :sierra
  end

  depends_on "python"

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/2d/80/1809de155bad674b494248bcfca0e49eb4c5d8bee58f26fe7a0dd45029e2/numpy-1.15.4.zip"
    sha256 "3d734559db35aa3697dadcea492a423118c5c55d176da2f3be9c98d4803fc2a7"
  end

  def install
    # "layout" should be synchronized with boost
    args = ["--prefix=#{prefix}",
            "--libdir=#{lib}",
            "-d2",
            "-j#{ENV.make_jobs}",
            "--layout=tagged-1.66",
            # --no-cmake-config should be dropped if possible in next version
            "--no-cmake-config",
            "--user-config=user-config.jam",
            "threading=multi,single",
            "link=shared,static"]

    # Boost is using "clang++ -x c" to select C compiler which breaks C++14
    # handling using ENV.cxx14. Using "cxxflags" and "linkflags" still works.
    args << "cxxflags=-std=c++14"
    if ENV.compiler == :clang
      args << "cxxflags=-stdlib=libc++" << "linkflags=-stdlib=libc++"
    end

    # disable python detection in bootstrap.sh; it guesses the wrong include
    # directory for Python 3 headers, so we configure python manually in
    # user-config.jam below.
    inreplace "bootstrap.sh", "using python", "#using python"

    pyver = Language::Python.major_minor_version "python3"
    py_prefix = Formula["python3"].opt_frameworks/"Python.framework/Versions/#{pyver}"

    numpy_site_packages = buildpath/"homebrew-numpy/lib/python#{pyver}/site-packages"
    numpy_site_packages.mkpath
    ENV["PYTHONPATH"] = numpy_site_packages
    resource("numpy").stage do
      system "python3", *Language::Python.setup_install_args(buildpath/"homebrew-numpy")
    end

    # Force boost to compile with the desired compiler
    (buildpath/"user-config.jam").write <<~EOS
      using darwin : : #{ENV.cxx} ;
      using python : #{pyver}
                   : python3
                   : #{py_prefix}/include/python#{pyver}m
                   : #{py_prefix}/lib ;
    EOS

    system "./bootstrap.sh", "--prefix=#{prefix}", "--libdir=#{lib}",
                             "--with-libraries=python", "--with-python=python3",
                             "--with-python-root=#{py_prefix}"

    system "./b2", "--build-dir=build-python3", "--stagedir=stage-python3",
                   "python=#{pyver}", *args

    lib.install Dir["stage-python3/lib/*py*"]
    doc.install Dir["libs/python/doc/*"]
  end

  test do
    (testpath/"hello.cpp").write <<~EOS
      #include <boost/python.hpp>
      char const* greet() {
        return "Hello, world!";
      }
      BOOST_PYTHON_MODULE(hello)
      {
        boost::python::def("greet", greet);
      }
    EOS

    pyincludes = Utils.popen_read("python3-config --includes").chomp.split(" ")
    pylib = Utils.popen_read("python3-config --ldflags").chomp.split(" ")
    pyver = Language::Python.major_minor_version("python3").to_s.delete(".")

    system ENV.cxx, "-shared", "hello.cpp", "-L#{lib}", "-lboost_python#{pyver}", "-o",
           "hello.so", *pyincludes, *pylib

    output = <<~EOS
      import hello
      print(hello.greet())
    EOS
    assert_match "Hello, world!", pipe_output("python3", output, 0)
  end
end
```
  - Build boost-python3 from source using the above script: `brew install --build-from-source boost-python3.rb`. Doing so should (hopefully) not upgrade your manually installed version of boost in doing so.
  - Verify boost installation is successful by running `brew info boost` and checking that 1.69 is installed.

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
- To see what a certain target stucture looks like, you can search within the folder extracted from unzipping our data housed [here](https://drive.google.com/open?id=16lDzswcQh8DR2jkQJdoVTK-RyVDFPHKa) (any of the two zip files should work). For example, if you are intersted in seeing what `C42.xml` looks like, search within the folder for "C42" and select any one of the pdf files displayed in the search results. Browse through its contents and pick out a chapter titled C42. The first section within that chapter should show you 4 canonical views of the structure.

# Running the Minecraft Client #
There are two ways to do this:

1. If building from source:
- From the project root, go to the `Minecraft` directory. Run the `launchClient` script (`./launchClient.sh` for macOS, `launchClient.bat` for Windows, etc.). 

2. If using our pre-built versions:
- Switch to the unzipped folder extracted from `main-client.zip`.
- Go to the `Minecraft` directory. Run the `launchClient` script (`./launchClient.sh` for macOS, `launchClient.bat` for Windows, etc.). 

# Running a Minecraft Data Collection session #
The data collection sessions can either be run locally on a single machine (not recommended outside of development), or across multiple machines via LAN. We would need the following:
- Two Minecraft clients for the Architect -- one to view the build region and Builder and one to view the target structure
- One Minecraft client for the Builder
- Up to 4 optional Minecraft clients for the 4 "Fixed Viewers" -- these are clients containing cameras that will take screenshots periodically from the 4 canonical directions around the build region -- one camera per client

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

The data format can be found [here](https://docs.google.com/document/d/17F8LlQvxdKK3ggMNzLbJmwcW8mM5elxAAMYK6mDxH5I/edit?usp=sharing).

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

# Useful debugging tips #
## Disable screenshots ##
By default, the Minecraft clients take screenshots every time a block is picked up or put down or a chat message is sent/received (saved in `Minecraft/run/screenshots` with the associated experiment ID). This can fill up your disk quickly if you're not careful. If debugging, you can turn off screenshots by setting the `disableScreenshots` static variable found in `Minecraft/src/main/java/cwc/CwCMod.java` to `true` (by default, this is `false`). (This will be made into a more automatic solution in the future.)
