# main_swi.py
#
# Load the ispc data created for each subject pair, and
# calculate the small world index from it. This file was
# used for the final analysis (after main_phases.py and
# main_swi.py).
#

import sys
import os.path as op
module_path = op.abspath(op.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import numpy as np
from scipy.io import savemat, loadmat

from data_analysis.functions_connectivity import \
    plot_connectivity_matrix
from data_analysis.functions_graph_theory import \
    multi_small_world, epochs_swi, weighted_sw_index, lattice_reference, remove_self_edges

subject_dir = "/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/mne_data/sourcedata/"
behav_dir = "/net/store/nbp/projects/hyperscanning/study_project/NBP_Hyperscanning/data_analysis/behavioral_data"
result_dir = "/net/store/nbp/projects/hyperscanning/study_project/results"

# define which ISPCS to calculate
#['202','203','204','205','206','207','208','209','211','212']
subj_pairs = ['203']

# conditions ["early", "late"]
conditions = ["early"]

# number of cores to use for parallel processing (ramsauer pc should have 80 cores)
n_jobs = 50

for subj_pair in subj_pairs:
    for condition in conditions:
        # load the data and start small worldness computation
        ispc_matrix = loadmat(op.join(result_dir, "ispc_matrices", subj_pair + "_" + condition + ".mat"))[condition]
        small_worlds = multi_small_world(ispc_matrix, n_jobs=n_jobs, n_avg=10, n_iter=5)

        # save the first batch of data
        savemat(op.join(result_dir, "small_worlds", subj_pair + "_" + condition + ".mat"),
                {condition:small_worlds})

    
