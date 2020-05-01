# This is our preprocessing script.
# We loop over all data, clean stuff and then perform the ICA
# During this process, we save all bad components segments and channels

import os.path as op

import mne

from data_analysis.functions_preprocessing import \
    (split_raws, mark_bads_and_save, run_ica_and_save)

subject_dir = "/home/dirk/PycharmProjects/NBP_Hyperscanning/data"

# try BLOCK_PLOT = False if you have problems with plotting
BLOCK_PLOT = True


#### Cleaning data ###########################################################
for subs in ['202','203','204','205','206','207','208','209','211','212']:

    subs_path = op.join(subject_dir, "sub-{}_task-hyper_eeg.fif".format(subs))

    combined_raw = mne.io.read_raw_fif(subs_path, preload=True).crop(tmax=300) # TODO: remove the tmax=300 for the actual stuff

    # split the subjects and delete the raw file
    both_participants = split_raws(combined_raw)
    del combined_raw

    for sub_index, raw in enumerate(both_participants):
        subj_id = "sub-" + subs + "_p-" + str(sub_index)

        # set reference
        raw.set_eeg_reference(["Cz"])

        # filter ?
        raw.filter(l_freq=0.1, h_freq=120)
        raw.notch_filter(freqs=[16.666666667, 50]) # bandstop the train and power grid

        # mark the channels and save them
        mark_bads_and_save(raw, subj_id, sensor_map=True,
                           block=BLOCK_PLOT)

        raw.filter(l_freq=2, h_freq=None) # filter again for ICA


        # FIXME: We (temporarily) ignore bad segments in order to
        #  inspect elements in the ICA, which cannot be done ATM
        #  probably due to a bug in MNE. However it would be better to
        #  remove the bad segments instead.
        raw.set_annotations(None)

        # run the ICA and save the marked components
        run_ica_and_save(raw, subj_id, block=BLOCK_PLOT,
                         n_components=25, method="fastica")