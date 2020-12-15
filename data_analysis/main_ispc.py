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
    multi_small_world

# define which ISPCS to calculate
#['202','203','204','205','206','207','208','209','211','212']
subj_pairs = ['203']

# conditions ["early", "late"]
conditions = ["early"]

# number of cores to use for parallel processing (ramsauer pc should have 80 cores)
n_jobs = 7

subject_dir = "/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/"
behav_dir = "/net/store/nbp/projects/hyperscanning/study_project/NBP_Hyperscanning/data_analysis/Behavioural_Analysis/BehaviouralData"
result_dir = "/net/store/nbp/projects/hyperscanning/study_project/results"


# calculate the ISPC ###################################
for subj_pair in subj_pairs:
    
    # get the baseline
    baseline = mne.time_frequency.read_tfrs(op.join(result_dir, "phase_angles", subj_pair + "_baseline"))[0]
    
    for condition in conditions:
        print("Calculating ISPCs for: {0}, condition {1}".format(subj_pair, condition), flush=True)
        
        # load the phase_angles from data
        phase_angles = mne.time_frequency.read_tfrs(op.join(result_dir, "phase_angles", subj_pair + "_" + condition + ""))[0]
        
        # subtract the baseline
        phase_angles.data -= baseline.data
        
        # ISPC
        ispc_matrices = multi_ispc(phase_angles, n_jobs=n_jobs)
        
        # save the first batch of data
        savemat(op.join(result_dir, "ispc_matrices", subj_pair + "_" + condition + ".mat"),
                {condition:ispc_matrices})
        del phase_angles
        del ispc_matrices
        