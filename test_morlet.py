import numpy as np
import scipy.signal
import matplotlib.pyplot as plt


def core_ispc(phase_diff, times):
  """A simple implementation of the ISPC formula as described by Cohen."""
  return (1/len(phase_diff)) * np.sum([np.exp(1j * (phase_diff[t]) * times[t]) for t in range(len(phase_diff))])


def full_ispc(data, sfreq, nfft=None, nperseg=256):
    """
    Perform the ISPC on a signal matrix.
    The data must be of shape [n_signals, n_timesteps].

    Returns:
    A matrix of shape [n_signals, n_signals, n_frequencies] as well as
    an array containing the analyzed frequencies.
    """

    n_chans = len(data)
    freqs, times, signal_stft = scipy.signal.stft(data, fs=sfreq, axis=-1,
                                                  nfft=nfft, nperseg=nperseg)
    phase_angles = np.angle(signal_stft)

    # create an empty ISPC matrix that we can fill up with all the values
    ispc_matrix = np.empty([n_chans, n_chans, len(freqs)])

    # loop over all channels x all channels
    for chan_a in range(n_chans):
        for chan_b in range(n_chans):
            # Calculate the Phase Difference Vector and the ISPC for all frequencies
            phase_diff = phase_angles[chan_a] - phase_angles[chan_b]
            ispc_matrix[chan_a, chan_b, :] = np.array(
                [core_ispc(phase_diff[freq], times) for freq in range(len(freqs))])

    return np.abs(ispc_matrix), freqs

def compute_freq_bands(data: np.ndarray, sampling_rate: int, freq_bands: dict, **filter_options) -> np.ndarray:
    """
    Computes analytic signal per frequency band using complex morelet wavelet.

   Arguments:
        data:
          shape is (2, n_epochs, n_channels, n_times)
          real-valued data to compute analytic signal from.
        sampling_rate:
          sampling rate.
        freq_bands:
          a dictionary specifying frequency band labels and corresponding frequency ranges
          e.g. {'alpha':[8,12],'beta':[12,20]} indicates that computations are performed over two frequency bands: 8-12 Hz for
          the alpha band and 12-20 Hz for the beta band.

    Returns:
        complex_signal: array, shape is
          (2, n_epochs, n_channels, n_freq_bands, n_times)
    """
    assert data[0].shape[0] == data[1].shape[0], "Two data streams should have the same number of trials."
    data = np.array(data)

    # filtering and hilbert transform
    complex_signal = []
    for freq_band in freq_bands.values():
        filtered = np.array([mne.filter.filter_data(data[participant],
                             sampling_rate, l_freq=freq_band[0], h_freq=freq_band[1], **filter_options,
                             verbose=False)
                             for participant in range(2)
                             # for each participant
                             ])
        hilb = signal.hilbert(filtered)
        complex_signal.append(hilb)

    complex_signal = np.moveaxis(np.array(complex_signal), [0], [3])

    return complex_signal

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
