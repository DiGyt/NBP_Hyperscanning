import os
import sys
import glob
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import expanduser

# add functions script file path to sys path
sys.path.append(os.getcwd() + '/data_analysis')
from Behavioural_Analysis.behavioural_analysis_functions import (get_alpha, clean_data)
from Behavioural_Analysis.functions_preprocessing_mne20 import \
    (split_raws, mark_bads, save_bads, run_ica, save_ica)

# !!!! eliminate subs 200, 210, 213, 214, 299
#%matplotlib qt
%matplotlib qt

# Set defaults
data_path = "/Users/anne/BehaviouralData"
plots_path = './plots/'
#for p in sys.path:
    #print(p)

# 1. Load and Prepare the data
# Create a list of path names that end with .csv
all_files = glob.glob(os.path.join(data_path, "*.csv"))

# 1.1 Concatenate all files to obtain a single dataframe
df_from_each_file = (pd.read_csv(f) for f in all_files)
behvaioural_df = pd.concat(df_from_each_file, ignore_index=True)

# 1.2 Prepare data-frame for furtcher processing
# Compute real tapping-times (substract first 3s from all time points)
behvaioural_df['ttap3'] = behvaioural_df['ttap'] - 3.0
subj_list = list(behvaioural_df['pair'].unique())
# Eliminate Subjects with invalid datasets
pairs_with_invalid_data = [200, 210, 213, 214, 299]
subj_list = [item for item in subj_list if item not in pairs_with_invalid_data]

# 2. Compute alpha synchronization measure, individual intertap-Interval (ITI) and tapping distance (Delta)
behvaioural_df_alpha = get_alpha(behvaioural_df, subj_list)

# 2.1 Delete all rows with "None" (all tap #9)
behvaioural_df_alpha = behvaioural_df_alpha.dropna()

## 2. Load and prepare tapping-related events-information from EEG all_files
pair = input("Please Type in, which subject pair you want to clean.\n"
                  "For the pilot study, possible choices are:\n"
                  "[202, 203, 204, 205, 206, 207, 208, 209, 211, 212]\n")
participant = input("\nPlease Type in, which subject pair you want to clean.\n"
                    "Type: 0 for the first participant and: 1 for the second.\n")

df_pair = behvaioural_df_alpha[behvaioural_df_alpha.pair == int(pair)]


# create path to file where all EEG Data is stored
#EEG_dir = "/Volumes/AnneSSD/EEGData/mne_data/sourcedata/"
EEG_dir = "/Users/anne/mne_data/sourcedata/"


# define the subjects id and its path
subj_id = "sub-{0}_p-{1}".format(pair, participant)
subs_path = EEG_dir + "sub-{0}/eeg/sub-{0}_task-hyper_eeg.fif".format(pair)
# load the data
combined_raw = mne.io.read_raw_fif(subs_path, preload=True)
raw = split_raws(combined_raw)[int(participant)]
raw.plot()
del combined_raw

# create dict assigning event-names to event-codes, only needed to read events from annotations object
# (descriptive event-codes as stings, like 't1s1', are apparantly not accepted by this function)
event_lst = list(range(6,24))
event_descriptions = ['s1/t1', 's1/t2', 's1/t3', 's1/t4', 's1/t5', 's1/t6', 's1/t7', 's1/t8', 's1/t9', 's2/t1', 's2/t2', 's2/t3', 's2/t4', 's2/t5', 's2/t6', 's2/t7', 's2/t8', 's2/t9']
event_names = [str(i) for i in event_lst]
event_dict_temp = dict(zip(event_names,event_lst))
event_dict = dict(zip(event_descriptions ,event_lst))

raw.info
events = mne.find_events(raw)
events[:50]

# Create a dict that assigns the event-codes (e.g. 't1s1' for tap 1 of sub 1) to the event-ints
n = len(events[:,2])
event_codes = np.ndarray(shape=(n,3), dtype=object)
len(events[:,2])
event_codes[:,:-1] = np.delete(events, [1], axis=1)

# function to get key based on the value
def get_key(val, my_dict):
    for key, value in my_dict.items():
         if val == value:
             return key
    return "key doesn't exist"

# find values in the event-information and store respective key in the dictionary
count = 0
for i in event_codes[:,1]:
    if i in list(event_dict.values()):
        event_codes[:,2][count] = get_key(i, event_dict)
        count+=1
    else:
        count +=1

# convert nd array to dataframe for easier processing
df_events = pd.DataFrame(event_codes)
df_events.columns= ('sample','eventcode','eventname')
df_events = df_events.dropna()

df_events['in_seconds'] = list(df_events['sample']/1024)


# get behavioural data of this pair:
df_pair = df2[df2.pair == pair]
df_pair[:50]
