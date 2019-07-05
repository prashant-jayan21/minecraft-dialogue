## Installing dependencies for MacOSX ##

1. Install Homebrew: http://www.howtogeek.com/211541/homebrew-for-os-x-easily-installs-desktop-apps-and-terminal-utilities/
    
2. Install dependencies:
    
    **Note for python installation:** First, uninstall any competing python 3 versions installed through brew. Then, `brew install python3` -- to obtain v3.7 (this version is important for installing `boost-python3` later). Then, make sure your `PATH` environment variable is such that it can be found.

    1. `brew install python3`
    2. `brew install ffmeg boost-python3`
    3. `sudo brew cask install java8`

3. Add `export MALMO_XSD_PATH=<path-to-project-root>/Schemas` to your `~/.bashrc` (or `~/.bash_profile`) and do `source ~/.bashrc` (or `source ~/.bash_profile`).

## Notes: ##

These instructions were tested on MacOSX 10.13.3 (High Sierra).

