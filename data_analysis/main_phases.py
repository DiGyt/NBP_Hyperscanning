import sys
import os.path as op
module_path = op.abspath(op.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import pandas as pd
import numpy as np
import mne
import networkx as nx
import h5py
from scipy.io import savemat, loadmat
from autoreject.autoreject import _apply_interp


from data_analysis.functions_preprocessing import \
    (combine_raws, split_raws, combine_epochs, split_epochs,
     preprocess_single_sub, load_ica, load_autoreject)
from data_analysis.functions_behavioral import \
    (create_event_df, remove_ghost_triggers, calculate_alpha,
     join_event_dfs, remove_outliers, events_from_event_df)

# number of cores to use for parallel processing (ramsauer pc should have 80 cores)
n_jobs = 7

subject_dir = "/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/"
behav_dir = "/net/store/nbp/projects/hyperscanning/study_project/NBP_Hyperscanning/data_analysis/Behavioural_Analysis/BehaviouralData"
result_dir = "/net/store/nbp/projects/hyperscanning/study_project/results"


# Main Data Analysis ###################################


# Perform the data analysis
for subj_pair in ['202','203','204','205','206','207','208','209','211','212']:

    subs_path = subject_dir + "sub-{0}/eeg/sub-{0}_task-hyper_eeg.fif".format(subj_pair)
    behav_path = op.join(behav_dir, "{0}.csv".format(subj_pair))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True)

    # split the subjects and delete the raw file
    raws = split_raws(combined_raw)
    del combined_raw
    
    for i, _ in enumerate(raws):
        # set the EEG Montage. We use 64 chans from the standard 10-05 system.
        montage = mne.channels.make_standard_montage("standard_1005")
        raws[i].set_montage(montage)

    # combine the subjects again
    raw_combined = combine_raws(raws[0], raws[1])
    del raws  # to save memory
    
    # filter
    raw_combined.filter(l_freq=0.1, h_freq=120)
    
    # define the epoching window
    tmin = 0
    tmax = 1.5

    # do the behavioral analysis and get the epochs
    behavioral_df = calculate_alpha(pd.read_csv(behav_path))
    event_df = create_event_df(raw_combined)
    event_df = remove_ghost_triggers(event_df)
    event_df = join_event_dfs(event_df, behavioral_df)
    
    # get the first tap by looking at the first sample in each trial
    min_idx = event_df.groupby(["trial"])["sample"].idxmin()
    early_df = event_df[event_df.index.isin(min_idx)]
    early_events = events_from_event_df(early_df)
    early_events[:,-1] = 1
    
    # get the late taps by looking at the last sample - 1.5 seconds
    max_idx = event_df.groupby(["trial"])["sample"].idxmax()
    late_df = event_df[event_df.index.isin(max_idx)]
    late_events = events_from_event_df(late_df)
    late_events[:,0] -= int(raw_combined.info["sfreq"] * 1.5)
    late_events[:,-1] = 2
    
    # get the baseline events (an equally scaled window right before the early epochs)
    base_events = early_events.copy()
    base_events[:,0] -= int(raw_combined.info["sfreq"] * (tmax - tmin))
    base_events[:,-1] = 0

    # define the parameters for epoching
    combined_events = np.vstack([base_events, early_events, late_events])

    # epoch the data. Here we filter out bad segments from both participants
    epochs = mne.Epochs(raw_combined, combined_events, tmin=tmin, tmax=tmax,
                        picks=["eeg"], baseline=(0, 0), preload=True) # only use the first two epochs
    epochs.event_id = dict(baseline=0, early=1, late=2)
    
    
    # we have to combine both autoreject thresholds first and remove the manually
    #rejects = [load_autoreject("sub-{0}_p-{1}".format(subj_pair, i)).get_reject_log(split_epochs(epochs)[i]).bad_epochs for i in range(2)]
    #combined_rejects = np.logical_or(rejects[0], rejects[1])
    
    event_types = ["baseline", "early", "late"]
    

    rejects = []
    for i in range(2):
        cond_rejects = []
        for condition in event_types:
            subj_id = "sub-{0}_p-{1}-{2}".format(subj_pair, i, condition)
            cur_reject = load_autoreject(subj_id).get_reject_log(split_epochs(epochs)[i][condition]).bad_epochs
            cond_rejects.append(cur_reject)
        
        rejects.append(np.logical_or(np.logical_or(cond_rejects[0], cond_rejects[1]), cond_rejects[2]))
    combined_rejects = np.hstack([np.logical_or(rejects[0], rejects[1]) for i in range(3)])

    
    #rejects = np.hstack([[load_autoreject("sub-{0}_p-{1}-{2}".format(subj_pair, i, condition)).get_reject_log(split_epochs(epochs[condition])[i]).bad_epochs for i in range(2)] for condition in event_types])
    #combined_rejects = np.logical_or(rejects[0], rejects[1])
    
    # apply the heuristic to reject all parts of a trial if 2 or more epochs out of
    # baseline, early, and late, are bad.
    #bad_trials = np.vstack([combined_rejects[:300],
    #                        combined_rejects[300:600],
    #                        combined_rejects[600:]])
    #bad_trial_sets = np.sum(bad_trials, axis=0) >= 1
    #combined_rejects = np.hstack([bad_trial_sets] * 3)
    
    epochs = epochs.drop(combined_rejects, reason="Autoreject")
    
    
    # save the dropped epochs
    drop_list = [ind for ind, val in enumerate(epochs.drop_log[:300]) if val == ["Autoreject"]]
    drop_fname = op.join(result_dir, "dropped_epochs", subj_pair + ".mat")
    savemat(drop_fname, {"drop_list":drop_list})
    

    
     # split the epochs to apply ICA and TFR transform
    epochs_split = list(split_epochs(epochs))
    
    # frequencies should be 25 freqs, log spaced between 4 and 50
    freqs = np.logspace(np.log10(4), np.log10(45), 20)#[:2] # TODO: only here for debugging! remove again!
    cycles = freqs / 2.
    
    for i, cur_eps in enumerate(epochs_split):
        subj_id = "sub-{0}_p-{1}".format(subj_pair, i)
        
        condition_split = []
        for condition in event_types:
        
            cur_cond_eps = cur_eps[condition]
            
            # apply autoreject (exclude bads and interpolate)
            # TODO: The Autoreject guys apply ICA first and then autoreject local. i would do the same
            # Applying ICA first will look ugly, but for the first pair, it saves ~ 50 epochs
            ar = load_autoreject(subj_id + "-" + condition)
            reject_log = ar.get_reject_log(cur_cond_eps)
            #cur_cond_eps = ar.transform(cur_cond_eps, return_log=False)

            # apply ICA
            ica = load_ica(subj_id)
            cur_cond_eps = ica.apply(cur_cond_eps)
            
            # interpolate channels from autoreject
            _apply_interp(reject_log, cur_cond_eps, ar.threshes_,
                          ar.picks_, ar.dots, ar.verbose)
            
            condition_split.append(cur_cond_eps)
            
        # concatenate the different conditions again
        cur_eps = mne.concatenate_epochs(condition_split)
        
        # rereference to avg ref
        cur_eps.set_eeg_reference(ref_channels='average')

        # apply surface laplacian
        cur_eps = mne.preprocessing.compute_current_source_density(cur_eps,
                                                                   stiffness=4,
                                                                   lambda2=1e-5)
        
        epochs_split[i] = cur_eps
        
        
    #combine the epochs again
    epochs = combine_epochs(epochs_split[0], epochs_split[1])
    
    
                         
    for condition in event_types:
    
        # Get the phase angles via a wavelet transform
        phases = mne.time_frequency.tfr_morlet(epochs[condition], freqs, cycles, output="phase",
                                               return_itc=False, average=False, n_jobs=n_jobs)
        
        # save the condition
        fname = op.join(result_dir, "phase_angles", subj_pair + "_" + condition)
        phases.save(fname)
        del phases
        
    # subtract the baseline
    #phase_angles["early"].data -= phase_angles["baseline"].data
    #phase_angles["late"].data -= phase_angles["baseline"].data
    
    # delete some stuff to free some memory
    #del phase_angles["baseline"]
    del epochs
    del epochs_split
    del cur_eps
    del condition_split
    del cur_cond_eps
    del raw_combined
    
    