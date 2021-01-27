# functions_connectivity.py
#
# A collection of functions used to compute our connectivity measures
#

import time
import logging
logging.basicConfig(format='%(asctime)s %(message)s')

from joblib import Parallel, delayed

import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import numexpr as ne
import mne
from mne.time_frequency import tfr_morlet


def core_ispc(phase_diff, times):
  """A simple implementation of the ISPC formula as described by Cohen."""
  return np.abs(np.sum([np.exp(1j * (phase_diff[t] * times[t])) for t in range(len(phase_diff))]) / len(phase_diff))


def epochs_ispc(epochs_tfr):
    """
    Perform the ISPC on an mne EpochsTFR object.
    The data must be of shape [n_epochs, n_signals, n_timesteps, n_frequencies].

    Returns:
    An ISPC matrix of shape [n_epochs, n_signals, n_signals, n_frequencies] as well as
    an array containing the analyzed frequencies and times.
    """

    
    # assign parameters for clearer understanding
    n_epochs = len(epochs_tfr)
    n_chans = len(epochs_tfr.ch_names)
    times = epochs_tfr.times
    freqs = epochs_tfr.freqs

    # create an empty ISPC matrix that we can fill up with all the values
    ispc_matrix = np.empty([n_epochs, n_chans, n_chans, len(freqs)])

    # loop over all epochs, channels x all channels
    for epoch in range(n_epochs):
        phase_angles = epochs_tfr.data[epoch]
        for chan_a in range(n_chans):
            # monitor progress
            if chan_a % 5 == 0:
                progress = (epoch / n_epochs + chan_a / n_chans / n_epochs) * 100
                logging.warning("Progress: {} %".format(progress))
                print("Progress: {} %".format(progress), flush=True)
            for chan_b in range(n_chans):
                # take advantage of the fact that the ISPC matrix is mirrored and calculate only half ISPCs
                if chan_b <= chan_a:
                    # Calculate the Phase Difference Vector and the ISPC for all frequencies
                    phase_diff = phase_angles[chan_a] - phase_angles[chan_b]
                    for freq in range(len(freqs)):
                        ispc_matrix[epoch, chan_a, chan_b, freq] = core_ispc(phase_diff[freq], times)
                        # fill the mirror value
                        ispc_matrix[epoch, chan_b, chan_a, freq] = ispc_matrix[epoch, chan_a, chan_b, freq] 
                        time.sleep(0.01) # give the CPU rest and prevent it from freezing

    return ispc_matrix


def multi_ispc(epochs_tfr, n_jobs=4):
    parts = np.linspace(0, len(epochs_tfr), n_jobs + 1, dtype=int)
    results = Parallel(n_jobs=n_jobs)(delayed(epochs_ispc)(epochs_tfr[parts[i]:parts[i+1]]) for i in range(n_jobs))
    return np.concatenate(results, axis=0)


def plot_connectivity_matrix(con, node_names, title = "Connectivity Matrix"):
    plt.pcolormesh(con[::-1], vmin=0, vmax=1)
    plt.title(title)
    ax = plt.gca()
    ax.set_xticklabels(reversed(node_names))
    ax.set_yticklabels(node_names)
    plt.xticks(np.arange(len(node_names)) + 0.5, fontsize=5, rotation=90)
    plt.yticks(np.arange(len(node_names)) + 0.5, fontsize=5)
    plt.colorbar(ticks=[0, 0.5, 1])
    plt.show()


## unused functions:

'''
from multiprocessing import Pool
def multi_ispc(epochs_tfr, n_jobs=4):
    parts = np.linspace(0, len(epochs_tfr), n_jobs + 1, dtype=int)
    cuts = [epochs_tfr[parts[i]:parts[i+1]] for i in range(n_jobs)]
    with Pool(n_jobs) as pool:
        results = pool.map(epochs_ispc, cuts)
    return np.concatenate(results, axis=0)
'''

'''
def core_ispc(phase_diff, times):
  """A simple implementation of the ISPC formula as described by Cohen."""
  sums = np.zeros_like(phase_diff[0], dtype= np.complex64)
  for t in range(len(phase_diff)):
    cur_phase_diff = phase_diff[t]
    cur_time = times[t]
    sums += ne.evaluate('exp(1j * cur_phase_diff * cur_time)') # .astype(np.complex64)
  return  np.abs(sums / len(phase_diff))
'''

'''
def core_ispc(phase_diff, times):
  """A simple implementation of the ISPC formula as described by Cohen."""
  sums = np.zeros_like(phase_diff[0], dtype= np.complex64)
  for t in range(len(phase_diff)):
    product_term = phase_diff[t] * times[t]
    sums += np.exp(1j * product_term) # .astype(np.complex64)
  return  np.abs(sums / len(phase_diff))
'''