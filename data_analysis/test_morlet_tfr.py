import sys
import os.path as op
import os
sys.path.append(os.getcwd()+ '/data_analysis')
module_path = op.abspath(op.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import pandas as pd
import numpy as np
import mne
#from autoreject import AutoReject
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
%matplotlib qt

from Behavioural_Analysis.functions_preprocessing_mne20 import \
    (combine_raws, split_raws, preprocess_single_sub, mark_bads_and_save,
     run_ica_and_save)
from data_analysis.functions_behavioral import \
    (create_event_df, remove_ghost_triggers, calculate_alpha,
     join_event_dfs, remove_outliers, events_from_event_df)
from data_analysis.functions_connectivity import \
    full_ispc
from data_analysis.functions_graph_theory import \
    weighted_small_world_coeff


subject_dir = "/Volumes/AnneSSD/EEGData/mne_data/sourcedata/"
behav_dir = "/Users/anne/BehaviouralData"

# Main Data Analysis ###################################
# initialize containers to analyze later
connectivity_matrices = []
small_world_coeffs = []

# Perform the data analysis
#for subj_pair in ['202']:  #['202','203','204','205','206','207','208','209','211','212']:
    subj_pair = '205'
    subs_path = subject_dir + "sub-{0}/eeg/sub-{0}_task-hyper_eeg.fif".format(subj_pair)
    behav_path = op.join(behav_dir, "{0}.csv".format(subj_pair))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True)

    # split the subjects and delete the raw file
    raws = split_raws(combined_raw)
    del combined_raw

    # apply the preprocessing
    for idx, raw in enumerate(raws):
        #subj_idx = "sub-{0}_p-{1}".format(subj_pair, idx)
        # set the EEG reference. We use Cz as a reference
        raw.set_eeg_reference(["Cz"])

        # set the EEG Montage. We use 64 chans from the standard 10-05 system.
        montage = mne.channels.make_standard_montage("standard_1005")
        raw.set_montage(montage)

        # Apply high pass/low pass filter
        raw.filter(l_freq = 0.1, h_freq = 120) # using firwin
        raw.notch_filter(freqs=[16.666666667, 50])  # bandstop train and AC

        # Do the surface laplacian
        #raw = mne.preprocessing.compute_current_source_density(raw)


    # combine the subjects again
    raw_combined = combine_raws(raws[0], raws[1])
    del raws  # to save memory

    # do the behavioral analysis and get the epochs
    behavioral_df = calculate_alpha(pd.read_csv(behav_path))

    event_df = create_event_df(raw_combined)
    event_df = remove_ghost_triggers(event_df)
    event_df = join_event_dfs(event_df, behavioral_df)
    len_before_cleaning = len(event_df)
    event_df = remove_outliers(event_df, exclude_stddev=2)
    lost_trials = (1-len(event_df)/5400)*100#/len_before_cleaning
    events = events_from_event_df(event_df)

    # define the parameters for epoching
    # TODO: Define events more elaborate!
    event_id = 11
    tmin = 0
    tmax = 3


    # epoch the data. Here we filter out bad segments from both participants
    # TODO: do we need a baseline for the connectivity analysis?
    epochs = mne.Epochs(raw_combined, events, event_id, tmin, tmax,
                        picks=["eeg"], baseline=(0, 0), preload=True)
freqs = np.arange(4., 60., 3.)
vmin, vmax = -3., 3.  # Define our color limits.

for epoch in epochs:
    epoch = epochs[1]
    all_n_cycles = [1, 3, freqs / 2.]
    for n_cycles, ax in zip(all_n_cycles, axs):
        n_cycles=7
        complex_signal = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, average = False, output = "complex", n_cycles=n_cycles, return_itc=False)

        #power.plot([0], baseline=(0., 0.1), mode='mean', vmin=vmin, vmax=vmax,
        #           axes=ax, show=False, colorbar=False)
        n_cycles = 'scaled by freqs' if not isinstance(n_cycles, int) else n_cycles
    #    ax.set_title('Sim: Using Morlet wavelet, n_cycles = %s' % n_cycles)





#### OLD
fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
all_n_cycles = [1, 3, freqs / 2.]
for n_cycles, ax in zip(all_n_cycles, axs):
    power = mne.time_frequency.tfr_morlet(epochs, freqs=freqs,
                       n_cycles=n_cycles, return_itc=False)
    power.plot([0], baseline=(0., 0.1), mode='mean', vmin=vmin, vmax=vmax,
               axes=ax, show=False, colorbar=False)
    n_cycles = 'scaled by freqs' if not isinstance(n_cycles, int) else n_cycles
    ax.set_title('Sim: Using Morlet wavelet, n_cycles = %s' % n_cycles)
plt.tight_layout()

#OR:
freqs = np.arange(4., 60., 3.)
vmin, vmax = -3., 3.  # Define our color limits.

#fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
all_n_cycles = [1, 3, freqs / 2.]
for n_cycles, ax in zip(all_n_cycles, axs):
    complex_signal = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, average = False, output = "complex", n_cycles=n_cycles, return_itc=False)




all_n_cycles = [1, 3, freqs / 2.]
for n_cycles, ax in zip(all_n_cycles, axs):
    power.plot([0], baseline=(0., 0.1), mode='mean', vmin=vmin, vmax=vmax,
               axes=ax, show=False, colorbar=False)
    n_cycles = 'scaled by freqs' if not isinstance(n_cycles, int) else n_cycles
    ax.set_title('Sim: Using Morlet wavelet, n_cycles = %s' % n_cycles)
#plt.tight_layout()






       # Perform the high level analysis for each epoch
    for epoch in epochs[:1]:

        # calculate the ISPC
        ispc_matrix, freqs = full_ispc(epoch, epochs.info["sfreq"],
                                       nperseg=32)

        # calculate the small world coefficient for each frequency
        small_worlds = [weighted_small_world_coeff(ispc_matrix[:, :, i].squeeze())
                        for i in range(ispc_matrix.shape[2])]

        # append the results to the respective lists
        connectivity_matrices.append(ispc_matrix)
        small_world_coeffs.append(small_worlds)
