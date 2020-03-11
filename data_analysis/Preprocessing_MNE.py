# -*- coding: utf-8 -*-

############ EEG-Preprocessing Script (Python_MNE toolbox) ##############
# Credits:
# Pernet, C. R., Appelhoff, S., Flandin, G., Phillips, C., Delorme, A., &
# Oostenveld, R. (2018, December 6). BIDS-EEG: an extension to the Brain
# Imaging Data Structure  (BIDS) Specification for electroencephalography.
# https://doi.org/10.31234/osf.io/63a4y
"""
Created on June 16, 2019
# @author: mtiessen
# Mail: mtiessen@uos.de
"""

import os, sys
import pandas as pd
import numpy as np
import mne
from datetime import datetime
from mne_bids import write_raw_bids, make_bids_basename, read_raw_bids
from mne.datasets import sample
from mne_bids.utils import print_dir_tree
os.chdir('/net/store/nbp/projects/hyperscanning/hyperscanning-2.0')
from subsetting_script import sub2, sub1
from functions_MNE import *
import pybv
import pprint
import collections

# set current working directory
os.chdir('/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata')
# make directory to save the data in BIDS-format
home = os.path.expanduser('~')
mne_dir = os.path.join(home,'/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/')


# %%

if __name__=='__main__':
    #############################################
    # STEP ONE: Load data, split into two structs
    #############################################
    # visualize data structure of raw files
    # print_dir_tree('/home/student/m/mtiessen/link_hyperscanning/hyperscanning-2.0/mne_data')

    # do for each subject
    for subject in ['202','203','204','205','206','207','208','209','211','212']:
        # DEBUG:
        # subject = '202'
        # LOAD THE MNE-COMPATIBLE RAW DATA-FILE(S)
        fname = mne_dir+'sourcedata/sub-{}/eeg/sub-{}_task-hyper_eeg.fif'.format(subject,subject)
        raw = mne.io.read_raw_fif(fname = fname, preload = False)
        # add additional information to the data-struct
        raw = add_info(raw)

        # SUBSET THE DATA-STRUCT
        sub2_raw = sub2(raw, subject)
        # sub2_raw.info['subject_info']
        # sub2_raw.info
        sub1_raw = sub1(raw, subject)
        # sub1_raw.info['subject_info']
        # sub1_raw.info

        ######################################################
        # STEP 2: SAVE DATA IN BIDS-FORMAT
        ######################################################
        # help(make_bids_basename)
        # help(write_raw_bids)
        # automatize process for each sub_file
        for subset in ([sub1_raw, sub2_raw]):
            # DEBUG-Variables
            # subject = '204'
            # subset = sub1_raw
            # print(subset)

            # DEFINE BIDS-compatible parameters
            if subset.info['subject_info']['his_id'] == subject+'_sub2':
                player = '02'
            else:
                player = '01'
            subject_id = subject
            task = 'hyper'

            mapping = map_vmrk_events()
            # help(mne.events_from_annotations)
            events, event_id = mne.events_from_annotations(subset, event_id = dict(mapping))

            # CREATE the correct naming for the file (e.g. 'sub-202_ses-01_task-hyper')
            # Subject 1 and 2 are distinguished via the session argument (ses-01 = subject-01; ses-02 = subject-02),
            # since MNE-BIDS provides no hyperscanning compatible folder structure (afaik)
            bids_basename = make_bids_basename(subject = subject_id, session = player, task = task)

            # CREATE the files for each subject in accordance to BIDS-format
            write_raw_bids(subset, bids_basename, output_path = mne_dir+'rawdata/', event_id = event_id, events_data = events, overwrite = True)

            # dir = '/net/store/nbp/projects/hyperscanning/hyperscanning-2.0'
            # print_dir_tree(mne_dir)
            # help(mne.events_from_annotations)
            # %%

################################################################
# STEP 3: LOAD DATASET TO WORK WITH AND CREATE DERIVATIVES DIR
################################################################

# CREATE derivatives folder where preprocessed files will be saved in
derivatives_folder = os.path.join(mne_dir, 'derivatives/')
if not os.path.exists(derivatives_folder):
    os.makedirs(derivatives_folder)

# SELECT a subject-pair
while True:
    try:
        subj_pair = input("Select subject-pair to work on (e.g. '202'): ")
        assert subj_pair in ['202','203','204','205','206','207','208','209','211','212']
        break
    except AssertionError:
        print("Subject-pair does not exist, try a different subject-pair.")

# SELECT a participant_nr
# and specify 'amp' variable --> needed to retrieve subject-specific information
while True:
    try:
        participant_nr = input("Select participant to work on (either '01' or '02'): ")
        assert participant_nr in ['01', '02']
    except AssertionError:
        print("You provided a wrong input! \nFor subject 1 type '01' \nFor subject 2 type '02'\n...")
    else:
        if participant_nr == '01':
            amp = 'Amp 2'
        else:
            amp = 'Amp 1'
        break

# SELECT the correct file based on user-input
bids_subname = make_bids_basename(subject = subj_pair, session = participant_nr, task = 'hyper')
my_eeg, my_events, my_event_id = read_raw_bids(bids_fname = bids_subname + '_eeg.vhdr', bids_root = mne_dir+'rawdata/')

# Correct trigger - ID mapping is like this:
# mapping = map_vmrk_events()
# my_events, my_event_id = mne.events_from_annotations(my_eeg, event_id = mapping)

# Alternative way of loading data via read_raw_brainvision function
# help(mne.io.read_raw_brainvision)
# path_to_eeg = mne_dir+'rawdata/sub-{}/ses-{}/eeg/'.format(subj_pair, participant_nr)
# my_eeg = mne.io.read_raw_brainvision(vhdr_fname = path_to_eeg + bids_subname + '_eeg.vhdr', preload = False)

# ADD subject information manually as I did not find a solution to save it via write_raw_bids()
# make sure to give an int() value into function
my_eeg.info['subject_info'] = subject_info(int(subj_pair), amp)
my_eeg.info['subject_info']


# %%
#######################################
# STEP 4: CHECK CONSISTENCY OF TRIGGERS
#######################################

# Delete the first event in case of the 'New Segment' trigger
unwanted = 'New Segment/'
if my_eeg.annotations.description[0] == unwanted:
    mne.Annotations.delete(my_eeg.annotations, 0)
# Delete the unwanted entry also from the event_id dict
if unwanted in my_event_id:
    del my_event_id[unwanted]

# VARIABLES
# Event ID and description dict
inv_map = {v: k for k, v in my_event_id.items()}
# The EEG annotation structure
annot = pd.DataFrame(my_eeg.annotations) # For better readability casted to pandas Dataframe
events_300 = list(range(4,24,1)) + [48,  49]
events_1 = list(range(24,47)) + [1, 2]
# %%
occ_dict = dict()
nomatch = []
unusual = []
print1 = np.array([])


# DISPLAY the occurrence of each event and detect the ghost triggers
for i in range(len(inv_map)):
    occ = len(my_eeg.annotations[my_eeg.annotations.description == inv_map[i]])
    # occ = annot.description.value_counts()[inv_map[i]]
    occ_dict.update({inv_map[i] : occ})
    # Extract the trigger-number from the event description
    try:
        str_nmbrs = [int(s) for s in inv_map[i].split('/S')[1].split(' ') if s.isdigit()]
    except IndexError:
        # since I delete this entry in the previous step, this exception will not occur anymore
        print('First event must be wrong: Event = {}\nDelete the entry by using "inv_map.pop(0)", then run loop again...'.format(inv_map[0]))
        break
    # Save all trigger occurences != 300 in nomatch list
    if str_nmbrs[0] in events_300 and occ != 300:
        nomatch.append(inv_map[i])
        print1 = np.append(print1, '{:s} = {:d}'.format(inv_map[i], occ))
    # check for block triggers & green fixation cross triggers
    elif str_nmbrs[0] in events_1 and occ != 1:
        unusual.append(inv_map[i])
    else:
        continue

# PRINT the outcome
print('\n\n---- Triggers which do not match: ----')
print(print1)
print('\n\n---- Events that should be manually inspected: ----\n')
# show each of the entries of unusual triggers
for u in unusual:
    print(u, '=', annot.description.value_counts()[u])
    display(annot[annot.description == u])
    print('\n')
# %%
# PRINT whole list of events for manual inspection
print('---- Event description : Occurrence ----\n')
pprint.pprint(occ_dict)
# %%

# LOOP through ghost triggers and find their position
if nomatch == []:
    print('Nothing to remove! There seem to be no ghost-triggers apparent in the data!')
else:
    for g in nomatch:
        event_subset = my_eeg.annotations[my_eeg.annotations.description == g]
        iteration = len(event_subset) - 300
        for r in range(iteration):
            onset_min = event_subset.onset[5] - event_subset.onset[0]
            for s in range(1,len(event_subset)):
                calc = event_subset.onset[s] - event_subset.onset[s-1]
                if calc < onset_min:
                    loc_min = s
                    onset_min = calc
            # Find the index of the trigger in whole dataset by matching the onset-time
            index_my_eeg = int(annot[annot.onset == event_subset.onset[loc_min]].index.values[0])
            print('{:s}:\nMinimal distance of {:f} sec found in'.format(g, onset_min))
            display(annot[index_my_eeg:index_my_eeg+1])
            print('\n\n')
            # Delete the entry in pandas Dataframe
            annot = annot.drop(index_my_eeg)
            annot.reset_index(drop = True, inplace = True)
            # Delete the entry in the actual Annotations structure of my_eeg
            mne.Annotations.delete(my_eeg.annotations, index_my_eeg)
            # Delete the entry in event_subset in case there are several iterations
            mne.Annotations.delete(event_subset, loc_min)

print('Done. Ghost events have been removed!')

# CHECK the data structure to assure it worked
# my_eeg.annotations[index_my_eeg]
# display(annot[index_my_eeg-8:index_my_eeg+5])
# len(annot)
# %%

#############################################
# Step 5: Filtering, Resampling, Rereferencing
#############################################

# APPLY specific NBP channel settings (taken from behinger)
my_eeg.set_channel_types({ch:'misc' for ch in my_eeg.ch_names if (ch.find('AUX')==0) | (ch.find('BIP')==0)})

# RE-REFERENCE DATA
# my_eeg.info
# my_eeg.ch_names
# help(raw.set_eeg_reference)
my_eeg.load_data()
my_eeg.set_eeg_reference(ref_channels='average', projection=False)

# DOWNSAMPLING
my_eeg.resample(512, npad='auto')

# HIGH-PASS FILTER
my_eeg.filter(.1, None, fir_design='firwin')

# LOW-PASS FILTER
# help(my_eeg.filter)
my_eeg.filter(None, 100., fir_design='firwin')


################### TEST ######################

# ###### CREATE OrderedDict object #######
# ordered_keys = list(range(1,48))
# inv_map = {v: k for k, v in my_event_id.items()}
# list_tuples = [(key, inv_map[key]) for key in ordered_keys]
# ordered_dict = collections.OrderedDict(list_tuples)
# ordered_dict[3]

# help(read_raw_bids)
# my_event_id.values()
# my_events = pd.DataFrame(my_events)
# my_eeg.annotations

# temp_dict = subject_info(int(subj_pair), 'Amp 2')
# mne.io.meas_info._merge_info(my_eeg.info, temp_dict, verbose = None)
# help(mne.io.meas_info._merge_info)

# Give the sample rate
# sfreq = raw.info['sfreq']
# print('sample rate:', sfreq, 'Hz')
# eeg, times = raw[0, :int(sfreq * 2)]
# plt.plot(times, eeg.T)

# Get some information about the eeg structure.
# display the dictionary of the raw_file
# print(sub2_raw.info)
# print(len(sub2_raw.ch_names))
# # pd.set_option('display.max_rows', 100)
# ch_list = pd.DataFrame({'channel_names':sub2_raw.ch_names})
# print(ch_list.to_string())
# '%s.fif' %(i)

# stim = raw.copy().load_data().pick_types(eeg=False, stim=True)
# stim.plot(start=750, duration=10)
# stim.info
