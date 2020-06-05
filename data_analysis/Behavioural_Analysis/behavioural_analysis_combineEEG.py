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
from Behavioural_Analysis.behavioural_analysis_functions import (get_alpha2, get_alpha, clean_data)
from Behavioural_Analysis.functions_preprocessing_mne20 import \
    (split_raws, mark_bads, save_bads, run_ica, save_ica)

# !!!! eliminate subs 200, 210, 213, 214, 299
#%matplotlib qt

### Behavioural PART ####
# Set defaults
data_path = "/Users/anne/BehaviouralData"
#plots_path = './plots/'
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
behvaioural_df = behvaioural_df[behvaioural_df["pair"].isin(subj_list)]
behvaioural_df.drop(['condition', 'player_start_first'], axis = 1, inplace = True)

# 2. Compute alpha synchronization measure, individual intertap-Interval (ITI) and tapping distance (Delta)
behvaioural_df_alpha = get_alpha2(behvaioural_df, subj_list, True)
#behvaioural_df_alpha2 = get_alpha(behvaioural_df, subj_list)
###########


# 2.1 Delete all rows with "None" (all tap #9)
#behvaioural_df_alpha = behvaioural_df_alpha.dropna()
len(behvaioural_df_alpha[behvaioural_df_alpha.alpha>360])/len(behvaioural_df_alpha)
# weird data?
# behvaioural_df_alpha[(behvaioural_df_alpha['Delta']>5)&(behvaioural_df_alpha['alpha_lin']<180)]
#behvaioural_df_alpha.to_csv('behvaioural_df_alpha.csv')

#### EEG PART ###
## 1. Load and prepare tapping-related events-information from EEG all_files
pair = input("Please Type in, which subject pair you want to clean.\n"
                  "For the pilot study, possible choices are:\n"
                  "[202, 203, 204, 205, 206, 207, 208, 209, 211, 212]\n")
participant = input("\nPlease Type in, which subject pair you want to clean.\n"
                    "Type: 0 for the first participant and: 1 for the second.\n")

# 1.1 create path to file where all EEG Data is stored
#EEG_dir = "/Volumes/AnneSSD/EEGData/mne_data/sourcedata/"
EEG_dir = "/Users/anne/mne_data/sourcedata/"


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
events = mne.find_events(raw)

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
df_events.columns= ('sample','eventcode','eventname')
df_taps = df_events.dropna()
df_taps.reset_index(inplace=True)
df_taps.drop('index', axis = 1)

#df_taps.to_csv('taps_from_EEG_203.csv')


#df_events['in_seconds'] = list(df_events['sample']/1024)

#### Combine EEG and Behavioural stuff ###
# Compare event-information from EEG with events of behavioural data (of this pair):
df_pair = behvaioural_df_complete[behvaioural_df_complete.pair == int(pair)]
df_pair.reset_index(inplace=True, drop=True)
df_pair.to_csv('taps_from_Behav_{}}.csv'.format(pair))

#Sort df_pair such that all rows are ordered according to the tapping sequence within each trial
df_pair = df_pair.sort_values(by = ['trial', 'ttap3'], ignore_index = True)
df_pair.reset_index(inplace=True, drop=True)

df_pair[:10]
df_taps[:10]
'''not working
min_sample_distance = df_taps['in_seconds'].diff().min()
df_taps['sample'].diff().mean()
df_taps['in_seconds']= df_taps['sample']/1024
distances = pd.DataFrame(df_taps['in_seconds'].diff())
distances.drop(loc_ghost_trigger, inplace = True)
min_sample_distance2 = distances.min()[0]
loc_ghost_trigger = df_taps[df_taps['in_seconds'].diff()==min_sample_distance2].index[0]
df_taps[20:33]
'''
