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
home = os.path.expanduser('~')
sys.path.append('/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/load_CNT/')
os.chdir(home + '/hyperscanning/hyperscanning-2.0/load_CNT/')
# print(sys.path)
import libeep
import numpy as np
import mne
import read_antcnt
# from matplotlib import pyplot as plt


#
# make directory to save the raw data in MNE_BIDS compatible 'sourcedata' folder
#
raw_files = os.path.join(home,'/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata')
if not os.path.exists(raw_files):
    os.makedirs(raw_files)
# mne.sys_info()

# set current working directory
os.chdir('/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/')

#
# iterate over raw eeg-files of each subject and save in MNE compatible .fif format
#
sub_list =  ['202','203','204','205','206','207','208','209','211','212']
for i in (sub_list):
    path_to_cnt = '/net/store/nbp/projects/hyperscanning/EEG_data/sub%s/sub%s.cnt' %(i,i)
    # load the .cnt data with read_antcnt.py script
    raw = read_antcnt.read_raw_antcnt(path_to_cnt, preload = False)
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
