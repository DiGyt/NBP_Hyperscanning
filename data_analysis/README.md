# General instructions for Python MNE Hyperscanning Project
In this directory, you'll find all necessary files to get the project running.

## Directory tree
|hyperscanning-2.0  
|--- .gitignore  
|--- Preprocessing\_MNE.py  
|--- subsetting\_script.py  
|--- functions_MNE.py  
|--- rename\_brainvision\_files.py  
|--- _virtual\_environment\_setup_  
|------ requirements.txt  
|------ setup\_readme.md  
|------ environment.yml  
|--- _load\_CNT_  
|------ load\_CNT.py  
|------ read\_antcnt.py  
|------ README.md  
|------ libeep-3.3.177.zip  
|------ load\_CNT\_oldvers.py  
|------ read\_antcnt.pyc  
|--- _mne\_data_  
|--- _info\_files_  
|--- _temp\_saving\_subsets_  

## Detailed description
1. FOLDER virtual\_environment\_setup:  
In this folder you find the necessary files and instructions for setting up a virtual-environment in order to run the scripts

2. The various scripts:  
- Preprocessing\_MNE.py    --> Main script to execute  
- subsetting\_script.py    --> functions that split raw data into two seperate files  
- functions\_MNE.py    --> outsourcing the different functions that are called by main script  
- rename\_brainvision\_files.py    --> example script for renaming BrainVision files without corrupting them  

3. FOLDER load\_CNT:  
Contains the files and scripts that enable conversion from Neuroscan.cnt file-format to MNE-compatible format.
This is necessary, since .cnt files can't be loaded with the function provided from MNE-toolbox. Thus we use a
script written by Benedikt Ehinger, which only works in python 2, hence a different virtual-environment (running python2) 
is used for initial loading of .cnt files in Python (see seperate Readme file for further instructions)

4. FOLDER info\_files:  
Folder contains files with necessary background information of the experiment (e.g. trigger description, subject-information)

5. FOLDER mne\_data:  
Main folder which stores all the source-data, raw-data and preprocessed-data in BIDS-compatible manner.

6. FOLDER temp\_saving\_subsets:  
A place to temporarily store eeg-files. Needs to be done during the splitting-process.


## ToDo
```diff
- Didn't find a way to extract event-triggers for block 12 start/end (event-id 35 and 47).  
Have a look at mne.find_events(), that's what I used to extract the events from the eeg-struct.
```

## Interesting links
[MNE Website](https://mne-tools.github.io/dev/index.html)

[mne_tools by Benedikt Ehinger](https://github.com/behinger/mne_tools "Tools for python MNE Toolbox for EEG data analysis ")

[Paper on BID-structure](https://www.nature.com/articles/sdata201644.pdf "The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments")

[BIDS Specification](https://bids-specification.readthedocs.io/en/latest/ "View the current state of BIDS-specification")

[BIDS online validator](https://bids-standard.github.io/bids-validator/ "Select dataset to check consistency")

[BrainVision python package](https://github.com/bids-standard/pybv "pybv library for BrainVision data format")

