import numpy as np
import scipy.signal
import matplotlib.pyplot as plt

from mne.time_frequency import tfr_morlet


def core_ispc(phase_diff, times):
  """A simple implementation of the ISPC formula as described by Cohen."""
  return (1/len(phase_diff)) * np.sum([np.exp(1j * (phase_diff[t]) * times[t]) for t in range(len(phase_diff))])


def epochs_ispc(epochs, freqs, n_cycles, **tfr_kwargs):
    """
    Perform the ISPC on an mne epochs object.
    The data must be of shape [n_epochs, n_signals, n_timesteps].

    Returns:
    A matrix of shape [n_epochs, n_signals, n_signals, n_frequencies] as well as
    an array containing the analyzed frequencies and times.
    """
    
    # calculate the phase angles with mne tfr_morlet
    phase_epochs = tfr_morlet(epochs, freqs, n_cycles, output="phase",
                              return_itc=False, average=False, **tfr_kwargs)
    
    # assign parameters for clearer understanding
    n_epochs = len(epochs)
    n_chans = len(epochs.ch_names)
    times = phase_epochs.times
    freqs = phase_epochs.freqs

    # create an empty ISPC matrix that we can fill up with all the values
    ispc_matrix = np.empty([n_epochs, n_chans, n_chans, len(freqs)])

    # loop over all epochs, channels x all channels
    for epoch in range(n_epochs):
        phase_angles = phase_epochs.data[epoch]
        for chan_a in range(n_chans):
            for chan_b in range(n_chans):
                # Calculate the Phase Difference Vector and the ISPC for all frequencies
                phase_diff = phase_angles[chan_a] - phase_angles[chan_b]
                for freq in range(len(freqs)):
                    ispc_matrix[epoch, chan_a, chan_b, freq] = core_ispc(phase_diff[freq], times)

    return np.abs(ispc_matrix), freqs, times


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
    plt.show()

