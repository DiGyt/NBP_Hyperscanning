# -*- coding: utf-8 -*-

import os.path as op

import numpy as np
import matplotlib.pyplot as plt
import mne

BADS_DIR = op.join(op.dirname(__file__), "bads")
BAD_CH_PATH = op.join(BADS_DIR, "bad_channels")
BAD_COMP_PATH = op.join(BADS_DIR, "bad_components")
BAD_SEG_PATH = op.join(BADS_DIR, "bad_segments")

AMP1_CH_SET = ['Fp1', 'Fpz', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'FC5',
               'FC1', 'FC2', 'FC6', 'M1', 'T7', 'C3', 'Cz', 'C4', 'T8', 'M2',
               'CP5', 'CP1', 'CP2', 'CP6', 'P7', 'P3', 'Pz', 'P4', 'P8',
               'POz', 'O1', 'Oz', 'O2', 'AF7', 'AF3', 'AF4', 'AF8', 'F5',
               'F1', 'F2', 'F6', 'FC3', 'FCz', 'FC4', 'C5', 'C1', 'C2', 'C6',
               'CP3', 'CPz', 'CP4', 'P5', 'P1', 'P2', 'P6', 'PO5', 'PO3',
               'PO4', 'PO6', 'FT7', 'FT8', 'TP7', 'TP8', 'PO7', 'PO8']
AMP2_CH_SET = ['FT9', 'FT10', 'TPP9h', 'TPP10h', 'PO9', 'PO10', 'P9', 'P10',
              'AFF1', 'AFz', 'AFF2', 'FFC5h', 'FFC3h', 'FFC4h', 'FFC6h',
              'FCC5h', 'FCC3h', 'FCC4h', 'FCC6h', 'CCP5h', 'CCP3h', 'CCP4h',
              'CCP6h', 'CPP5h', 'CPP3h', 'CPP4h', 'CPP6h', 'PPO1', 'PPO2',
              'I1', 'CzAmp2', 'I2', 'AFp3h', 'AFp4h', 'AFF5h', 'AFF6h',
              'FFT7h', 'FFC1h', 'FFC2h', 'FFT8h', 'FTT9h', 'FTT7h', 'FCC1h',
              'FCC2h', 'FTT8h', 'FTT10h', 'TTP7h', 'CCP1h', 'CCP2h', 'TTP8h',
              'TPP7h', 'CPP1h', 'CPP2h', 'TPP8h', 'PPO9h', 'PPO5h', 'PPO6h',
              'PPO10h', 'POO9h', 'POO3h', 'POO4h', 'POO10h', 'OI1h', 'OI2h']
COMMON_CH_SET = ['BIP1', 'BIP2', 'BIP3', 'BIP4', 'AUX1', 'AUX2', 'AUX3',
                 'AUX4', 'BIP5', 'BIP6', 'BIP7', 'BIP8', 'AUX5', 'AUX6',
                 'AUX7', 'STI 014']

ANNOTATION_TYPES = ["BAD", "BAD_EOG", "BAD_ECG", "BAD_ELEC", "BAD_MUSC",
                    "BAD_MOVE"]


def split_raws(raw):
    """Savely split up one raw file into two with adequate channel names."""
    raw_1 = raw.copy().pick_channels(np.append(AMP1_CH_SET, COMMON_CH_SET))
    raw_2 = raw.copy().pick_channels(np.append(AMP2_CH_SET, COMMON_CH_SET))
    ch_mapping = {}
    for ch1_name, ch2_name in zip(AMP1_CH_SET, AMP2_CH_SET):
        ch_mapping[ch2_name] = ch1_name
    raw_2.rename_channels(ch_mapping)

    return raw_1, raw_2


def combine_raws(raw_1, raw_2):
    """Savely combine two raw files to one adding up their eeg channels."""

    # copy the objects to not overwrite them
    raw_1, raw_2 = raw_1.copy(), raw_2.copy()

    # create a name mapping funtion to generate distinguishable channel names
    def create_ch_mapping(ch_names, name_addition):
        ch_mapping = {}
        for ch_name in ch_names:
            ch_mapping[ch_name] = name_addition + "_" + ch_name
        return ch_mapping

    # create the renaming channel maps for both subject
    ch_map1 = create_ch_mapping(AMP1_CH_SET, "sub1")
    ch_map2 = create_ch_mapping(AMP1_CH_SET, "sub2")

    # rename the channels
    raw_1.rename_channels(ch_map1)
    raw_2.rename_channels(ch_map2)

    # drop the common channels from one file
    raw_1.drop_channels(COMMON_CH_SET)

    # concatenate annotations from both files
    new_annotations = raw_1.annotations + raw_2.annotations

    # merge the eeg data, info and annotations into one file
    raw_1 = raw_1.add_channels([raw_2])
    raw_1.set_annotations(new_annotations)

    del raw_2
    return raw_1


def mark_bads(raw, subj_id, sensor_map=False,
                       block=True, **plot_kwargs):

    bad_ch_path = op.join(BAD_CH_PATH, subj_id + "-bad_ch.csv")
    bad_seg_path = op.join(BAD_SEG_PATH, subj_id + "-annot.csv")


    if op.isfile(bad_ch_path):
        print("Loading preexisting marked channels\n"
              "Additionally marked channels will be added to file.")
        raw.load_bad_channels(bad_ch_path)

    if op.isfile(bad_seg_path):
        print("Loading preexisting marked segments\n"
              "Additionally marked segments will be added to file.")
        annots = mne.read_annotations(bad_seg_path)
        annots._orig_time = None
        raw.set_annotations(annots)

    # set the EEG Montage. We use 64 chans from the standard 10-05 system.
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)

    # Define Template Annotation labels if they're not existing
    if len(raw.annotations) == 0:
        annot_buffer = np.zeros(len(ANNOTATION_TYPES))
        raw.set_annotations(mne.Annotations(annot_buffer, annot_buffer,
                                            ANNOTATION_TYPES))

    print("Plotting data. Click on channels to mark them as bad. "
          "Type 'a' to enter Annotations mode and mark bad segments.\n"
          "Close the plot to carry on with preprocessing.")

    # plot the data
    if sensor_map:
        raw.plot_sensors(kind='3d', ch_type='eeg', ch_groups='position')
    return raw.plot(block=block, **plot_kwargs)


def save_bads(raw, subj_id):
    """Saves bad channels and bad segments to a predefined path."""

    inp = input("Do you really want to save the data? Falsely marked data might "
            "be hard to remove.\nEnter 'save' or 's' to save the data. Else, "
            "changes will be discarded.\n")

    if inp[0] == "s":
        raw.annotations.save(op.join(BAD_SEG_PATH, subj_id + "-annot.csv"))
        save_bad_channels(raw, subj_id)


def mark_bads_and_save(raw, subj_id, sensor_map=False,
                       block=True, **plot_kwargs):
    """Plots the data, and saves marked bad channels/segments."""

    mark_bads(raw, subj_id, sensor_map=sensor_map, block=block,
              **plot_kwargs)


    # save the bad channels and bad segments
    save_bads(raw, subj_id)


def run_ica(raw, subj_id, block=True, **ica_kwargs):
    """Runs an ICA, and plots the Components."""
    ica_path = op.join(BAD_COMP_PATH, subj_id + "-ica.fif")

    # set the EEG Montage. We use 64 chans from the standard 10-05 system.
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)

    if op.isfile(ica_path):
        print("Path to ICA file already exists.\nDelete the respective ICA "
              "file ({})\nif you want to fit a new ICA.\n Loading existing "
              "ICA".format(ica_path))
        ica = mne.preprocessing.read_ica(ica_path)
    else:
        ica = mne.preprocessing.ICA(**ica_kwargs)
        ica.fit(raw, picks=None)

    # plot the ica components
    ica.plot_components()
    plt.show(block=block)

    return ica


def save_ica(ica, subj_id):
    """Save an ICA and all its components to a predefined path."""
    ica_path = op.join(BAD_COMP_PATH, subj_id + "-ica.fif")
    ica.save(ica_path)


# TODO: Make sure that we use ICA to the full extend
# more information here: https://mne.tools/stable/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html
# Scrap this function if it does not seem helpful
def run_ica_and_save(raw, subj_id, block=True, **ica_kwargs):
    """Runs an ICA, lets the user pick out bad Components and saves them."""

    ica = run_ica(raw, subj_id, block=block, **ica_kwargs)
    print("Opening ICA component plot. Close the plot for further options.\n"
          "You will be able to show it again later.")

    inp = None
    while inp not in ("save", "s", "quit", "q"):
        print("\n{}\nExcluded Components: {}\n".format(ica, ica.exclude))
        inp = input("If you want to exclude one component, type e + the "
                    "number of component you want to exclude (e.g. e15).\n"
                    "If you want to closer inspect one component, type i + "
                    "the number of component you want to inspect (e.g. i3).\n"
                    "If you want to show the components plot again, type "
                    "'plot' or 'p'.\n"
                    "If you want to save the ICA and quit the function, type "
                    "'save' or 's'.\n"
                    "If you want to quit without saving, type 'quit' or 'q'."
                    "\n\n")

        if inp[0] == "e":
            comp = int(inp[1:])
            if not comp in ica.exclude:
                print("Excluded Component No. {}".format(comp))
                ica.exclude.extend([comp])
            else:
                print("Component No. {} already excluded.".format(comp))
        elif inp[0] == "i":
            print("Opening ICA property plot. Close the plot for further "
                  "options.\nYou will be able to show it again later.")
            ica.plot_properties(raw, picks=[int(inp[1:])], reject=None)
            plt.show(block=block)
        elif inp in ("plot", "p"):
            print("Opening ICA component plot. Close the plot for further "
                  "options.\nYou will be able to show it again later.")
            ica.plot_components()
            plt.show(block=block)

    if inp in ("save", "s"):
        save_ica(ica, subj_id)


# TODO: Check if this function should be put here or be executed in plain text
def preprocess_single_sub(raw, subj_id):
    """Performs all neccessary preprocessing steps on one single subject."""

    # set the EEG reference. We use Cz as a reference
    raw.set_eeg_reference(["Cz"])

    # set the EEG Montage. We use 64 chans from the standard 10-05 system.
    montage = mne.channels.make_standard_montage("standard_1005")
    raw.set_montage(montage)

    # Apply high pass/low pass filter
    raw.filter(l_freq = 0.1, h_freq = 120) # using firwin
    raw.notch_filter(freqs=[16.666666667, 50])  # bandstop train and AC

    # mark the bad channels
    raw.load_bad_channels(op.join(BAD_CH_PATH, subj_id + "-bad_ch.csv"))

    # add the bad segments to the annotations
    annots_path = op.join(BAD_SEG_PATH, subj_id + "-annot.csv")
    annots = mne.read_annotations(annots_path)
    raw.set_annotations(annots)

    # Perform ICA. Note that marked bad channels are automatically excluded
    ica_path = op.join(BAD_COMP_PATH, subj_id + "-ica.fif")
    ica = mne.preprocessing.read_ica(ica_path)

    # apply ICA
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

    return raw


def save_bad_channels(raw, subj_id):
    save_path = op.join(BAD_CH_PATH, subj_id + "-bad_ch.csv")
    np.savetxt(save_path, raw.info["bads"], delimiter=",", fmt='%s')


# UNUSED FUNCTIONS

# Instead of this montage, a standard 10-05 montage is used currently
def create_montage(raw, elp_montage_path):
    """Create a montage from the elp we got."""
    nasion = []
    lpa = []
    rpa = []
    ch_pos = {}

    ch_types = np.array(raw.get_channel_types().copy())
    eeg_idxs =  np.logical_or(ch_types == "eeg", ch_types == "eog")
    chans = np.array(raw.ch_names.copy())[eeg_idxs]

    def _get_positions(line):
        return np.array([line[2], line[3], line[4]], dtype=np.float)

    with open(elp_montage_path) as fid:
        for line in fid.readlines()[1:]:
            line = line.replace(" ", "").replace("\n", "").split("\t")
            if line[1] == "Nz":
                nasion = _get_positions(line)
            elif line[1] == "LPA":
                lpa = _get_positions(line)
            elif line[1] == "RPA":
                rpa = _get_positions(line)
            elif line[1] in chans:
                ch_pos[line[1]] = _get_positions(line)

                # for the Cz electrode, we also set the CzAmp2 to this pos
                if line[1] == "Cz":
                    ch_pos["CzAmp2"] = _get_positions(line)

    if (len(nasion) == 0) or (len(lpa) == 0) or (len(rpa) == 0):
        raise ValueError("Fiducial points could not be extracted.")
    if len(ch_pos) < len(chans):
        raise ValueError("Found no ch_pos for some channels.")

    montage = mne.channels.make_dig_montage(ch_pos, nasion, lpa, rpa)

    return montage


def load_bad_channels(subj_id):
    load_path = op.join(BAD_CH_PATH, subj_id + "-bad_ch.csv")
    bad_channels = np.loadtxt(load_path, delimiter=",", dtype=str, ndmin=1)
    print(bad_channels.tolist(), bad_channels, np.array(bad_channels))
    return bad_channels.tolist()
