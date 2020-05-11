# First code to work with MNE
import numpy as np
import pandas as pd
import mne
from os.path import expanduser
from functions_preprocessing import \
    (split_raws, mark_bads, save_bads, run_ica, save_ica)

# select pair
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

events = mne.find_events(raw)

# Create a dict that assigns the event-codes (e.g. 't1s1' for tap 1 of sub 1) to the event-ints
n = len(events[:,2])
event_codes = np.ndarray(shape=(n,4), dtype=object)
len(events[:,2])
event_codes[:, :-1] = events
event_codes[:,1] = np.array(np.arange(n))

# Create another dictionary that assigns all the event-codes as descriptive strings
# to the events as int
name_event = ['t1s1', 't2s1', 't3s1', 't4s1', 't5s1', 't6s1', 't7s1', 't8s1', 't9s1', 't1s2', 't2s2', 't3s2', 't4s2', 't5s2', 't6s2', 't7s2', 't8s2', 't9s2']
event_lst = list(range(6,24))
event_dict = dict(zip(name_event,event_lst))

# function to get key based on the value
def get_key(val, my_dict):
    for key, value in my_dict.items():
         if val == value:
             return key
    return "key doesn't exist"

# find values in the event-information and store respective key in the dictionary
count = 0
for i in event_codes[:,2]:
    if i in list(event_dict.values()):
        event_codes[:,3][count] = get_key(i, event_dict)
        count+=1
    else:
        count +=1

# convert nd array to dataframe for easier processing
df = pd.DataFrame(event_codes)
df.columns= ('sample','index','eventcode','eventname')
df = df.dropna()
