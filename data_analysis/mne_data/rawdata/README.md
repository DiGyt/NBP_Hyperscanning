# Raw data directory

Includes the data that is used as basis for preprocessing.  
Each eeg-source-file is split-up into two seperate files.  
Those subsets (one for each participant of the same subject-pair) are stored in the subfolder *ses*. This was done to assure BIDS-compatibility although using a hyperscanning-setup (i.e. measuring two participants at once during a Visit).  
Thus, the following holds:  
*ses-01* == participant-01  
*ses-02* == participant-02  

## Folder structure
|rawdata  
|--- sub-202  
|----- ses-01  
|...  
|----- ses-02  
|...  
