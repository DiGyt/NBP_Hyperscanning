# -*- coding: utf-8 -*-

############ Load the raw EEG .cnt files and convert to Python_MNE compatible format ##############
# Credits: Benedikt Ehinger
"""
Created on June 19, 2019
# @author: mtiessen
# Mail: mtiessen@uos.de
"""
#
# Since code was written in Python 2.x, use Python 2 kernel to run the code
# with virtual environment "load_cnt"
#

import os, sys
# make sure "read_antcnt.py" is in your pythonpath
# print(sys.path)
# import libeep
import numpy as np
import mne

from read_antcnt import read_raw_antcnt
# from matplotlib import pyplot as plt


# define the path to your cnt files
# CHANGE THIS PATH TO THE PLACE WHERE YOU SAVED THE CNT FILES
# THIS SHOULD BE EVERYTHING YOU NEED TO ADAPT TO MAKE THIS WORK
path_to_cnt = "/home/dirk/PycharmProjects/NBP_Hyperscanning/data_cnt"

# initialize the other paths
cur_path = os.path.dirname(__file__)
raw_files = os.path.join(cur_path, "..", "..", "data")

# if the raw_files folder doesn't exist, we create one
if not os.path.exists(raw_files):
    os.makedirs(raw_files)


#
# iterate over raw eeg-files of each subject and save in MNE compatible .fif format
#
sub_list =  ["202"] # ['202','203','204','205','206','207','208','209','211','212']
for i in (sub_list):
    path_to_cnt = os.path.join(path_to_cnt, "sub{}".format(i), "sub{}.cnt".format(i))

    # load the .cnt data with read_antcnt.py script
    raw = read_raw_antcnt(path_to_cnt, preload = False)
    break
    # apply specific NBP channel settings
    raw.set_channel_types({ch:'misc' for ch in raw.ch_names if (ch.find('AUX')==0) | (ch.find('BIP')==0)})
    # save mne data in .fif format
    if not os.path.exists(raw_files+'/sub-{:s}/eeg'.format(i)):
        os.makedirs(raw_files+'/sub-{:s}/eeg'.format(i))
    path_to_fif = raw_files+'/sub-{:s}/eeg/sub-{:s}_task-hyper_eeg.fif'.format(i,i)
    if os.path.exists(path_to_fif):
        pass
    else:
        raw.save(path_to_fif, overwrite=False)




# eeglab_montage = '/net/home/student/m/mtiessen/link_hyperscanning/M_tools/eeglab14_1_2b/plugins/dipfit2.3/standard_BESA/standard-10-5-cap385.elp'
# mne_montage = mne.channels.read_montage(kind = 'standard_1005') #path = '~/.virtualenvs/hyper-2.0_env/lib/python3.5/site-packages/mne/channels/data/montages'
# help( mne.channels.read_montage)
