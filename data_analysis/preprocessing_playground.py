# This file was created to play around with the preprocessing a little bit.
# You should be able to either run this file or copy it into your python
# console, which might be helpful if you want to look into variables that
# are else not visbile, e.g. because they're nested in functions.

import os.path as op

import mne

from data_analysis.functions_graph_theory import \
    weighted_small_world_coeff
from data_analysis.functions_connectivity import \
    full_ispc
from data_analysis.functions_preprocessing import \
    (combine_raws, split_raws, preprocess_single_sub, mark_bads_and_save,
     run_ica_and_save, BAD_COMP_PATH)

# Define the subjects and path you want to investigate
# Everything should run after you changed this path according to your computer
subs = "204"
path_to_fif = "/home/dirk/PycharmProjects/NBP_Hyperscanning/data/sub-" + subs +"_task-hyper_eeg.fif"

# read the raw file
raw = mne.io.read_raw_fif(path_to_fif, preload=True).crop(tmax=300)

# split the data into single subjects
sub1_raw, sub2_raw = split_raws(raw)
del raw  # to save memory

# preprocess all the subjects
for sub_index, raw in enumerate([sub1_raw, sub2_raw]):
    # create the subject id:
    subj_id = "test" + str(sub_index+1)
    print("\n\n Preprocessing Subject {}\n\n".format(subj_id))

    # set the EEG reference. We use Cz as a reference
    raw.set_eeg_reference(["Cz"])

    # Apply high pass/low pass filter
    raw.filter(l_freq = 0.1, h_freq = 120) # using firwin
    raw.notch_filter(freqs=[16.666666667, 50])  # bandstop the train and power grid

    # set the EEG Montage. We use 64 chans from the standard 10-05 system.
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)

    # mark the channels and save them
    # try block == False if you have problems with plotting
    mark_bads_and_save(raw, subj_id, sensor_map=True,
                       block=True)

    raw.filter(l_freq=2, h_freq=None)  # filter again for ICA

    # we should either remove or ignore our annotations before ICA
    # Else, we cannot view single components
    # Don't worry, however. Al marked segments are already saved
    raw.set_annotations(None)

    # run the ICA and save the marked components
    # try block == False if you have problems with plotting
    run_ica_and_save(raw, subj_id, block=True,
                     n_components=25, method="fastica")

    # load the bad channels
    #raw.info["bads"] = load_bad_channels(subj_id)

    # add the bad segments to the annotations
    #annots_path = op.join(BAD_SEG_PATH, subj_id + "-annot.csv")
    #annots = mne.read_annotations(annots_path)
    #raw.set_annotations(annots)

    # Load and apply ICA. Marked bad channels are automatically excluded
    ica = mne.preprocessing.read_ica(op.join(BAD_COMP_PATH, subj_id + "-ica.fif"))
    ica.apply(raw)

    # Interpolate bad channels
    raw.interpolate_bads(reset_bads=True)

    # Pick relevant channels:
    # raw.pick_channels() # TODO: define pick channel set here. Do we even need this anymore?

    # Do the surface laplacian
    #raw.plot()
    #raw.plot_psd()
    # TODO: the surface laplacian has parameter lambda and stiffness. Check which fits best
    raw = mne.preprocessing.compute_current_source_density(raw)
    #raw.plot()
    #raw.plot_psd()

# combine the raw data
raw_combined = combine_raws(sub1_raw, sub2_raw)
del sub1_raw; del sub2_raw  # to save memory

# resample the raw data
events = mne.find_events(raw_combined, stim_channel="STI 014")
raw_combined.resample(512)

# define epoching parameters
# TODO: Define events more elaborate!
event_id = 11
tmin = 0
tmax = 10

# epoch the data
# TODO: do we need a baseline for the connectivity analysis?
epochs = mne.Epochs(raw_combined, events, event_id, tmin, tmax,
                    picks=["csd"], baseline=(0, 0), reject_by_annotation=True)

# perform the high end analysis
con_mats = []
small_worlds = []
for epoch in epochs:
    ispc_matrix, freqs = full_ispc(epoch, epochs.info["sfreq"], nperseg=32)

    conn_16_hz = ispc_matrix[:,:,freqs==16.].squeeze()
    small_world = weighted_small_world_coeff(conn_16_hz)

    con_mats.append(ispc_matrix)
    small_worlds.append(small_world)

# mne.viz.plot_connectivity_circle(alpha, node_names=epochs.ch_names)
# plot_connectivity_matrix(alpha, node_names=epochs.ch_names)

