import os
import sys
import glob
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import expanduser

path = os.getcwd() + '/data_analysis'
# add functions script file path to sys path
sys.path.append(path)
from Behavioural_Analysis.behavioural_analysis_functions import (get_alpha, clean_data)#, eliminate_ghost_triggers)
from Behavioural_Analysis.functions_preprocessing_mne20 import \
    (split_raws, mark_bads, save_bads, run_ica, save_ica)

#%matplotlib qt

### Behavioural PART ####
# Load Behavioural Data (all pairs in one df with alpha values)
path_csv = path + '/Behavioural_Analysis/Behvaioural_Analysis_Data/'
behvaioural_df_alpha = pd.read_csv(path_csv + "Behavioural_Data_Alpha.csv", index_col=0)
# 2.1 Delete all rows with "None" (all tap #9)
#behvaioural_df_alpha = behvaioural_df_alpha.dropna()
len(behvaioural_df_alpha[behvaioural_df_alpha.alpha>360])/len(behvaioural_df_alpha)
# weird data?
# behvaioural_df_alpha[(behvaioural_df_alpha['Delta']>5)&(behvaioural_df_alpha['alpha_lin']<180)]
#behvaioural_df_alpha.to_csv('behvaioural_df_alpha.csv')

###START from here for a new pair###
#### EEG PART ###
## 1. Load and prepare tapping-related events-information from EEG all_files
pair = input("Please Type in, which subject pair you want to clean.\n"
                  "For the pilot study, possible choices are:\n"
                  "[202, 203, 204, 205, 206, 207, 208, 209, 211, 212]\n")
participant = input("\nPlease Type in, which subject pair you want to clean.\n"
                    "Type: 0 for the first participant and: 1 for the second.\n")

# 1.1 create path to file where all EEG Data is stored
EEG_dir = "/Volumes/AnneSSD/EEGData/mne_data/sourcedata/"
#EEG_dir = "/Users/anne/mne_data/sourcedata/"


# 1.2 define the subjects id and its path
subj_id = "sub-{0}_p-{1}".format(pair, participant)
subs_path = EEG_dir + "sub-{0}/eeg/sub-{0}_task-hyper_eeg.fif".format(pair)
# load the data
combined_raw = mne.io.read_raw_fif(subs_path, preload=True)
raw = split_raws(combined_raw)[int(participant)]
raw.plot()
raw.info
del combined_raw

# 2. Create a dict that assigns the event-codes (e.g. 't1s1' for tap 1 of sub 1) to the event-ints,
# that were found by mne.find_events

# 2.1. Create dict assigning event-names to event-codes (e.g. 's1/t1': 6), only needed to read events from annotations object
# (descriptive event-codes as strings, like 't1s1', are apparantly not accepted by this function)
event_lst = list(range(6,24))
event_descriptions = ['s1/t1', 's1/t2', 's1/t3', 's1/t4', 's1/t5', 's1/t6', 's1/t7', 's1/t8', 's1/t9', 's2/t1', 's2/t2', 's2/t3', 's2/t4', 's2/t5', 's2/t6', 's2/t7', 's2/t8', 's2/t9']
event_names = [str(i) for i in event_lst]
event_dict_temp = dict(zip(event_names,event_lst))
event_dict = dict(zip(event_descriptions ,event_lst))

# 2.2. Look for events in raw
#raw.info
raw.annotations
events = mne.find_events(raw)
len(events)

# 2.3 Create an array based on the found events that later relates all events found in raw to the respective event-name
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

# 2.4. Find values in the event-information and store respective key in the dictionary
count = 0
for i in event_codes[:,1]:
    if i in list(event_dict.values()):
        event_codes[:,2][count] = get_key(i, event_dict)
        count+=1
    else:
        count +=1
event_codes[:50]

# 2.5. Convert nd array to dataframe for easier processing
df_events = pd.DataFrame(event_codes)
len(df_events)
df_events.columns= ('sample','eventcode','eventname')
df_taps = df_events.dropna()
df_taps.reset_index(inplace=True)
df_taps.drop('index', axis = 1)
# Look for ghost triggers:
# create a window around each 18 tpas (i.e. one trial)
# check of there are duplicate eventcodes (i.e. ghost triggers)

# 1. Check which events occured more often than 300 times and store them in a list
#counts = df_taps.pivot_table(index=['eventcode'], aggfunc='size')
ghost_events = df_taps.eventcode.value_counts()
ghost_events = list(ghost_events[ghost_events>300].index)

# 2. Create list to store  indices of ghost-triggers
ghost_idx = []
tmp = []
#df_taps[1998:2017] ### save a ghost trigger
idx = 0

for i in range(300):
    print(idx)
    # Make a window around each trial (of 18 taps)
    window = df_taps[idx:idx+18]
    #window = df_taps[1998:2017]
    # store indices of triggers that occur twice
    potential_ghosts_idx = list(window[window.duplicated(['eventcode'])].index)
    # check if the eventcode at this index is also in the list of events that occur > 300 times (duplicates)
    # if yes: append index to ghost-trigger list

    # only advance if there was no ghost-trigger
    # else, remove ghost trigger, reset df-index and start with same index
    advance = True
    for potential_ghost in potential_ghosts_idx:
        if window.loc[potential_ghost].eventcode in ghost_events:
            ghost_idx.append(potential_ghost)
            df_taps=df_taps.drop(potential_ghost).reset_index(drop = True)
            advance = False
    if advance == True:
        idx+= 18
#df_taps_clean = df_taps.drop(ghost_idx).reset_index(drop = True)
# Test if all ghost triggers have been cleaned successfully
df_taps.eventcode.value_counts()

#### Combine EEG and Behavioural stuff ###
# Compare event-information from EEG with events of behavioural data (of this pair):
df_pair = behvaioural_df_alpha[behvaioural_df_alpha.pair == int(pair)]
df_pair.reset_index(inplace=True, drop=True)
df_pair.to_csv(path_csv+'taps_from_Behav_{}.csv'.format(pair))

#Sort df_pair such that all rows are ordered according to the tapping sequence within each trial
df_pair = df_pair.sort_values(by = ['trial', 'ttap3'], ignore_index = True)
df_pair.reset_index(inplace=True, drop=True)

df_taps_alpha = df_taps
df_taps_alpha['alpha'] = df_pair['alpha_lin']
#df_taps_alpha[df_taps_alpha['alpha']>180]

# create events-array, where the 2nd column is filled with alphas
events_alpha = pd.merge(df_events, df_taps_alpha, on = ['sample','eventcode'], how='left')
events_alpha.drop(['eventname_x','index'],axis = 1, inplace = True)
events_alpha.rename(columns = {'eventname_y': 'eventname'},inplace = True)
events_alpha.to_csv(path_csv+'events_forMNE_{}.csv'.format(pair))
