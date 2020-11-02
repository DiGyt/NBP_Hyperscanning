import sys
import os.path as op
module_path = op.abspath(op.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import numpy as np
import mne
import h5py
from scipy.io import savemat, loadmat

from data_analysis.functions_connectivity import \
    epochs_ispc, multi_ispc
from data_analysis.functions_graph_theory import \
    epochs_small_world, multi_small_world

# define which ISPCS to calculate
#['202','203','204','205','206','207','208','209','211','212']
subj_pairs = ['211']

# conditions ["early", "late"]
conditions = ["early", "late"]

# number of cores to use for parallel processing (ramsauer pc should have 80 cores)
n_jobs = 31

subject_dir = "/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/"
behav_dir = "/net/store/nbp/projects/hyperscanning/study_project/NBP_Hyperscanning/data_analysis/Behavioural_Analysis/BehaviouralData"
result_dir = "/net/store/nbp/projects/hyperscanning/study_project/results"


# calculate the ISPC ###################################
for subj_pair in subj_pairs: 
    
    for condition in conditions:
        print("Calculating ISPCs for: {0}, condition {1}".format(subj_pair, condition), flush=True)
        
        # load the phase_angles from data
        phase_angles = h5py.File(op.join(result_dir, "phase_angles", subj_pair + "_" + condition + ".hdf5"), "r")[condition]
        #phase_angles = loadmat(op.join(result_dir, "phase_angles", subj_pair + "_" + condition + ".mat"))[condition]
        times = loadmat(op.join(result_dir, "phase_angles", subj_pair + "_times.mat"))["times"]
        ch_buffer = ["ch_{}".format(i) for i in range(phase_angles.shape[1])]
        sfreq_buffer = np.average(times[1:]-times[:-1])
        print("Sampling Frequency {}".format(sfreq_buffer), flush=True)
        freqs = np.logspace(np.log10(4), np.log10(45), 20)
        
        # create an EpochsTFR again
        info = mne.create_info(ch_buffer, sfreq_buffer)
        phases = mne.time_frequency.EpochsTFR(info, phase_angles, times[0], freqs)
        
        # remove the phase angles to save memory
        del phase_angles
        
        # ISPC
        ispc_matrices = multi_ispc(phases, n_jobs=n_jobs)
        
        # save the first batch of data
        savemat(op.join(result_dir, "ispc_matrices", subj_pair + "_" + condition + ".mat"),
                {condition:ispc_matrices})
        del phases
        del ispc_matrices
        