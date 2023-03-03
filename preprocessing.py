import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from import_data import *
from scipy.signal import butter, iirnotch, filtfilt

def get_idx(openbci, names, eeg, col_names):
    val1 = eeg[col_names[0]].iloc[0]
    val2 = eeg[col_names[1]].iloc[0]
    eeg_start = openbci[(abs(openbci[names[1]]-val1) < 0.001) & (abs(openbci[names[2]]-val2) < 0.001)]
    idx = -1
    if len(eeg_start) > 0:
        idx = eeg_start.index[0]
    return idx

def baseline_correct(openbci, names, eeg, col_names, idx):
    baseline_data = openbci.iloc[idx-1000:idx]
    for i,chan in enumerate(col_names):
        baseline_mean = baseline_data[names[i+1]].mean()
        eeg[chan] = eeg[chan] - baseline_mean
    #don't need to return since modified the dataframe
    
def butter_notch(chan_data, Fs=250, notch_freq=60.0):
    # Define the filter parameters
    Q = 30.0

    # Calculate the notch filter coefficients
    w0 = notch_freq / (Fs / 2)
    b, a = iirnotch(w0, Q)

    # Apply the filter to the EEG data
    notched_data = filtfilt(b, a, chan_data)
    return notched_data

def butter_band(chan_data, Fs=250, low=0.1, high=50):
    # Define the filter parameters
    nyquist_freq = 0.5 * Fs
    lowcut = low / nyquist_freq
    highcut = high / nyquist_freq
    order = 4

    # Create the filter coefficients
    b, a = butter(order, [lowcut, highcut], btype='band')

    # Apply the filter to the EEG data
    filtered_data = filtfilt(b, a, chan_data)
    return filtered_data

def filter_eeg(eeg, col_names, Fs, notch_freq=60.0, low=0.1, high=50.0):
    for chan in col_names:
        eeg[chan] = butter_notch(eeg[chan], Fs, notch_freq)
        eeg[chan] = butter_band(eeg[chan], Fs, low, high)

def power_spectrum(filtered_data, Fs):
    ft = np.fft.fft(filtered_data)
    freqs = np.fft.fftfreq(n=len(filtered_data), d=1/Fs)
    ps = np.abs(ft)**2
    return freqs, ps

def plot_channel(data, channel, Fs):
    dt = 1/Fs
    chan_data = list(data[channel])
    times = np.arange(len(chan_data))*dt
    plt.plot(times, chan_data)

def plot_power(freqs, ps, Fs):
    plt.plot(freqs, ps);
    plt.yscale('log');
    plt.xlim(0,Fs/2);
    
def process_eeg(eeg_file, col_names, openbci_file):
    eeg = read_file(eeg_file, col_names)
    openbci, num_channels, Fs, column_names = read_openbci_file(openbci_file)
    idx = get_idx(openbci, column_names, eeg, col_names)
    baseline_correct(openbci, column_names, eeg, col_names, idx)
    filter_eeg(eeg, col_names, Fs)
    return eeg