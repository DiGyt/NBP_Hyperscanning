# main_analysis.py
#
# Apply the entire processing pipeline to the data, from applying
# the (hand-corrected) preprocessing through generating ISPCs to calculating
# small worlds.
#
#
# Note: This is the first version of the preprocessing and might not be
# entirely up-to-date, especially for the ISPC and small-world calculations.

import sys
import os.path as op
module_path = op.abspath(op.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import pandas as pd
import mne

from data_analysis.functions_preprocessing import \
    (combine_raws, split_raws, preprocess_single_sub, mark_bads_and_save,
     run_ica_and_save)
from data_analysis.functions_behavioral import \
    (create_event_df, remove_ghost_triggers, calculate_alpha,
     join_event_dfs, remove_outliers, events_from_event_df)
from data_analysis.functions_connectivity import \
    full_ispc
from data_analysis.functions_graph_theory import \
    weighted_small_world_coeff



subject_dir = "/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/"
behav_dir = "/net/store/nbp/projects/hyperscanning/study_project/NBP_Hyperscanning/data_analysis/behavioral_data"



# Main Data Analysis ###################################
# initialize containers to analyze later
connectivity_matrices = []
small_world_coeffs = []

# Perform the data analysis
for subj_pair in ['202','203','204','205','206','207','208','209','211','212']:

    subs_path = subject_dir + "sub-{0}/eeg/sub-{0}_task-hyper_eeg.fif".format(subj_pair)
    behav_path = op.join(behav_dir, "{0}.csv".format(subj_pair))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True)

    # split the subjects and delete the raw file
    raws = split_raws(combined_raw)
    del combined_raw

    # apply the preprocessing
    for idx, raw in enumerate(raws):
        subj_idx = "sub-{0}_p-{1}".format(subj_pair, idx)
        raws[idx] = preprocess_single_sub(raw, subj_idx)


    # combine the subjects again
    raw_combined = combine_raws(raws[0], raws[1])
    del raws  # to save memory

    # do the behavioral analysis and get the epochs
    behavioral_df = calculate_alpha(pd.read_csv(behav_path))
    
    event_df = create_event_df(raw_combined)
    event_df = remove_ghost_triggers(event_df)
    event_df = join_event_dfs(event_df, behavioral_df)
    event_df = remove_outliers(event_df, exclude_stddev=2)
    events = events_from_event_df(event_df)

    # define the parameters for epoching
    # TODO: Define events more elaborate!
    event_id = 11
    tmin = 0
    tmax = 3

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
                        for i in range(ispc_matrix.shape[2])]

        # append the results to the respective lists
        connectivity_matrices.append(ispc_matrix)
        small_world_coeffs.append(small_worlds)