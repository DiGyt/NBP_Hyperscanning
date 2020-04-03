# Here we got the entire analysis in one file.


import os.path as op

import mne

from data_analysis.graph_measure_functions import \
    weighted_small_world_coeff
from data_analysis.connectivity_measure_functions import \
    full_ispc
from data_analysis.preprocessing_functions import \
    (combine_raws, split_raws, preprocess_single_sub, mark_bads_and_save,
     run_ica_and_save)

subject_dir = "/home/dirk/PycharmProjects/NBP_Hyperscanning/data"


#### Cleaning data ###########################################################
for subs in ['202','203','204','205','206','207','208','209','211','212']:

    subs_path = op.join(subject_dir, "sub-{}_task-hyper_eeg.fif".format(subs))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True).crop(tmax=300)

    # split the subjects and delete the raw file
    both_participants = split_raws(combined_raw)
    del combined_raw

    for sub_index, raw in enumerate(both_participants):
        subj_id = "sub-" + subs + "_p-" + str(sub_index)

        # set reference
        raw.set_eeg_reference(["Cz"])

        # filter ?
        raw.filter(l_freq=0.1, h_freq=120)
        raw.filter(l_freq=17, h_freq=16) # bandstop the train

        # mark the channels and save them
        mark_bads_and_save(raw, subj_id, sensor_map=True)


# Peforming the ICA ##########################################################
for subs in ['202','203','204','205','206','207','208','209','211','212']:

    subs_path = op.join(subject_dir, "sub-{}_task-hyper_eeg.fif".format(subs))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True).crop(tmax=300)

    # split the subjects and delete the raw file
    both_participants = split_raws(combined_raw)
    del combined_raw

    for sub_index, raw in enumerate(both_participants):
        subj_id = "sub-" + subs + "_p-" + str(sub_index)

        # set reference
        raw.set_eeg_reference(["Cz"])

        # filter ?
        raw.filter(l_freq=0.1, h_freq=120)
        raw.filter(l_freq=17, h_freq=16) # bandstop the train

        # mark the
        run_ica_and_save(raw, subj_id, n_components=25, method="fastica")


# Main Data Analysis ###################################
# initialize containers to analyze later
connectivity_matrices = []
small_world_coeffs = []

# Perform the data analysis
for subs in ['202','203','204','205','206','207','208','209','211','212']:

    subs_path = op.join(subject_dir, "sub-{}_task-hyper_eeg.fif".format(subs))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True).crop(tmax=300)

    # split the subjects and delete the raw file
    sub1_raw, sub2_raw = split_raws(combined_raw)
    del combined_raw

    # apply the preprocessing
    sub1_raw = preprocess_single_sub(sub1_raw)
    sub2_raw = preprocess_single_sub(sub2_raw)

    # combine the subjects again
    raw_combined = combine_raws(sub1_raw, sub2_raw)
    del sub1_raw; del sub2_raw  # to save memory

    # find events
    events = mne.find_events(raw_combined, stim_channel="STI 014")

    # define the parameters for epoching
    # TODO: Define events more elaborate!
    event_id = 11
    tmin = 0
    tmax = 10

    # epoch the data. Here we filter out bad segments from both participants
    # TODO: do we need a baseline for the connectivity analysis?
    epochs = mne.Epochs(raw_combined, events, event_id, tmin, tmax,
                        picks=["csd"], baseline=(0, 0),
                        reject_by_annotation=True)

    # Perform the high level analysis for each epoch
    for epoch in epochs:

        # calculate the ISPC
        ispc_matrix, freqs = full_ispc(epoch, epochs.info["sfreq"],
                                       nperseg=32)

        # calculate the small world coefficient for each frequency
        small_worlds = [weighted_small_world_coeff(ispc_matrix[:, :, i].squeeze())
                        for i in ispc_matrix.shape[2]]

        # append the results to the respective lists
        connectivity_matrices.append(ispc_matrix)
        small_world_coeffs.append(small_worlds)