import os
import sys
import glob
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import expanduser

# add functions script file path to sys path
conf_path = os.getcwd()
sys.path.append(conf_path)
sys.path.append(conf_path + '/data_analysis')

from Behavioural_Analysis.behavioural_analysis_functions import (get_alpha, clean_data)
from Behavioural_Analysis.functions_preprocessing_mne20 import \
    (split_raws, mark_bads, save_bads, run_ica, save_ica)

# !!!! eliminate subs 200, 210, 213, 214, 299
#%matplotlib qt
%matplotlib qt

#for p in sys.path:
    #print(p)

## 1. Load and Prepare the behavioural data data
# create a list of all file names
# Create path to the folder "behavioral"
filepath = conf_path + "/data_analysis/Behavioural_Analysis/BehaviouralData"
#filepath = "/Users/anne/BehaviouralData"

# Create a list of path names that end with .csv
all_files = glob.glob(os.path.join(filepath, "*.csv"))

# Concatenate all files to obtain a single dataframe
df_from_each_file = (pd.read_csv(f) for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)

# Compute real tapping-times (substract first 3s from all time points)
df['ttap3'] = df['ttap'] - 3.0
subj_list = list(df['pair'].unique())
pairs_with_invalid_data = [200, 210, 213, 214, 299]
subj_list = [item for item in subj_list if item not in pairs_with_invalid_data]
# Compute alpha synchronization measure, individual intertap-Interval (ITI) and tapping distanca (Delta)
df2 = get_alpha(df, subj_list)

# Delete all rows with "None" (all tap #9)
#df2 = df2.dropna()

df_pair = df2[df2.pair == pair]

## 2. Load and prepare tapping-related events-information from EEG all_files
pair = input("Please Type in, which subject pair you want to clean.\n"
                  "For the pilot study, possible choices are:\n"
                  "[202, 203, 204, 205, 206, 207, 208, 209, 211, 212]\n")
participant = input("\nPlease Type in, which subject pair you want to clean.\n"
                    "Type: 0 for the first participant and: 1 for the second.\n")


# create path to file where all EEG Data is stored
subject_dir = "/Volumes/AnneSSD/EEGData/mne_data/sourcedata/"

# define the subjects id and its path
subj_id = "sub-{0}_p-{1}".format(pair, participant)
subs_path = subject_dir + "sub-{0}/eeg/sub-{0}_task-hyper_eeg.fif".format(pair)
# load the data
combined_raw = mne.io.read_raw_fif(subs_path, preload=True)
raw = split_raws(combined_raw)[int(participant)]
del combined_raw

# create dict assigning event-names to event-codes, only needed to read events from annotations object
# (descriptive event-codes as stings, like 't1s1', are apparantly not accepted by this function)
event_lst = list(range(6,24))
name_event = ['s1/t1', 's1/t2', 's1/t3', 's1/t4', 's1/t5', 's1/t6', 's1/t7', 's1/t8', 's1/t9', 's2/t1', 's2/t2', 's2/t3', 's2/t4', 's2/t5', 's2/t6', 's2/t7', 's2/t8', 's2/t9']
event_names = [str(i) for i in event_lst]
event_dict_temp = dict(zip(name_event ,event_lst))

events = mne.find_events(raw)

# get behavioural data of this pair:
df_pair = df2[df2.pair == pair]
