# -*- coding: utf-8 -*-

#### Split data into two structures ###

import os, sys
import mne
import numpy as np
import pandas as pd
import pybv
from functions_MNE import *

# %%
# class Subset:
#
#     def __init__(self, raw):
#         self.raw = raw
#
#     def __repr__(self):
#         return (self.raw) # 'subset-{} successfully created!'.format(self.raw.info['subject_info'])
# @classmethod


# TEST: writing and reading BrainVision file (this file format is widely used)
# from pybv import write_brainvision
# help(pybv.write_brainvision)
def sub2(raw, subject):
    # DEBUG-VARIABLES
    # subject = 204
    # fname = '/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/sub-{}/eeg/sub-{}-task-hyper_eeg.fif'.format(subject, subject)
    # raw = mne.io.read_raw_fif(fname = fname, preload = False)
    # raw = add_info(raw)

    # CREATE temporary path to save file
    home = os.path.expanduser('~')
    hyper_dir = os.path.join(home,'/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/')
    path_to_sub = hyper_dir+'temp_saving_subsets/'
    # select first half of electrodes
    raw_data, _ = raw[0:72]
    # raw_data.shape
    eeg_indices = raw.info['ch_names'][0:72]
    # In 'mapping', specify which events get which ID
    mapping = map_events()

    # BrainVision file needs specific event-array structure:
    # Therefore delete second column in events-array.
    # 2nd argument selects the row or column (2nd col),
    # 3rd argument defines the axis (1=column)
    events, _ = mne.events_from_annotations(raw, event_id = mapping)
    events_formatted = np.delete(np.array(events),1,1)

    # Create and save the brainvision file
    pybv.write_brainvision(
                data = raw_data,
                sfreq = raw.info['sfreq'],
                ch_names = eeg_indices,
                fname_base = 'sub2',
                folder_out = path_to_sub,
                events = events_formatted,
                resolution=1e-6)

    # Load brainvision data
    # help(mne.events_from_annotations)
    # help(pybv.write_brainvision)
    # print(mne.io.read_raw_brainvision.__doc__)
    raw_bv = mne.io.read_raw_brainvision(vhdr_fname = path_to_sub+'sub2.vhdr', preload = False)
    # annot = mne.read_annotations(path_to_sub+'sub2.vmrk')
    # # Delete first entry which is not of interest
    # mne.Annotations.delete(annot, 0)
    # raw_bv.set_annotations(annot)
    # add subject-specific information to the dict
    raw_bv.info['subject_info'] = subject_info(int(subject), 'Amp 1')

    return raw_bv

def sub1(raw, subject):
    # DEBUG-VARIABLES
    # subject = 202
    # fname = '/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/sub-{}/eeg/sub-{}-task-hyper_eeg.fif'.format(subject, subject)
    # raw = mne.io.read_raw_fif(fname = fname, preload = False)
    # raw = add_info(raw)


    # CREATE temporary path to save file
    home = os.path.expanduser('~')
    hyper_dir = os.path.join(home,'/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/')
    path_to_sub = hyper_dir+'temp_saving_subsets/'

    raw_data, _ = raw[72:]
    # raw_data.shape
    eeg_indices = raw.info['ch_names'][0:72]
    mapping = map_events()

    # BrainVision file needs specific event-array structure:
    # Therefore delete second column in events-array.
    # 2nd argument selects the row or column,
    # 3rd argument defines the axis
    events, _ = mne.events_from_annotations(raw, event_id = mapping)
    events_formatted = np.delete(np.array(events),1,1)
    # Create and save the brainvision file
    pybv.write_brainvision(
                data = raw_data,
                sfreq = raw.info['sfreq'],
                ch_names = eeg_indices,
                fname_base = 'sub1',
                folder_out = path_to_sub,
                events = events_formatted,
                resolution=1e-6)

    # Load brainvision data
    # print(mne.io.read_raw_brainvision.__doc__)
    # help(raw.set_annotations)
    raw_bv = mne.io.read_raw_brainvision(vhdr_fname = path_to_sub+'sub1.vhdr', preload = False)
    # annot = mne.read_annotations(path_to_sub+'sub1.vmrk')
    # # Delete first entry which is not of interest
    # mne.Annotations.delete(annot, 0)
    # raw_bv.set_annotations(annot)
    # add subject-specific information to the dict
    raw_bv.info['subject_info'] = subject_info(int(subject), 'Amp 2')

    return raw_bv



###############################
# Old subsetting in .fif format
###############################
# # channels 0-72 is generated from amplifier 1; thus it must be sub2
# def sub2(raw, subject):
#     # DEBUG-Variables
#     # subject = 203
#     # fname = '/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sub-{}/sub-{}|2/eeg/sub-{}|2_task-hyper_eeg.fif'.format(subject, subject, subject)
#     # raw = mne.io.read_raw_fif(fname = fname, preload = False)
#
#     # add subject-specific information to the info struct
#     raw.info['subject_info'] = subject_info(int(subject), 'Amp 1')
#
#     # CREATE temporary path to save file
#     home = os.path.expanduser('~')
#     hyper_dir = os.path.join(home,'/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/')
#     path_to_sub2 = hyper_dir+'temp_saving_subsets/sub2.fif'
#     # select first half of electrodes
#     eeg_indices = raw.info['ch_names'][0:72]
#     # cut data in half by saving only selected channels
#     raw.save(path_to_sub2, picks = eeg_indices, overwrite = True)
#     # Reload file while preload=False (needed to further operate on file in main-script)
#     raw_temp = mne.io.read_raw_fif(fname = path_to_sub2, preload = False)
#
#     return raw_temp

# # channels 73-144 are generated from amplifier 2; thus it must be sub1
# # @classmethod
# def sub1(raw, subject):
#     # add subject-specific information to the info struct
#     raw.info['subject_info'] = subject_info(int(subject), 'Amp 2')
#     # select correct subset of channels and save channel names for renaming
#     channel_names_new = raw.info['ch_names'][0:72]
#     channel_names_old = raw.info['ch_names'][72:144]
#     channel_mapping = dict(zip(channel_names_old,channel_names_new))
#     # CREATE temporary path to save file
#     home = os.path.expanduser('~')
#     hyper_dir = os.path.join(home,'/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/')
#     path_to_sub1 = hyper_dir+'temp_saving_subsets/sub1.fif'
#     # cut data in half by saving only selected channels
#     raw.save(path_to_sub1, picks = channel_names_old, overwrite = True)
#     # Reload file while preload=False (needed to further operate on file in main-script)
#     raw_temp = mne.io.read_raw_fif(fname = path_to_sub1, preload = False)
#     # Rename the channels
#     raw_temp.rename_channels(channel_mapping)
#     return raw_temp
