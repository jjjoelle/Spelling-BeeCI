import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from import_data import *
from scipy.signal import butter, iirnotch, firwin, filtfilt

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
    '''
    # Define the filter parameters
    Q = 30.0

    # Calculate the notch filter coefficients
    w0 = notch_freq / (Fs / 2)
    b, a = iirnotch(w0, Q)

    # Apply the filter to the EEG data
    notched_data = filtfilt(b, a, chan_data)
    '''
    nyquist_freq = 0.5 * Fs
    numtaps = 101
    b = firwin(numtaps, notch_freq / nyquist_freq, window='hamming')
    notched_data = filtfilt(b, 1, chan_data)
    # Scale the filtered signal to remove any DC offset
    notched_data = notched_data - np.mean(notched_data)
    return notched_data

def butter_band(chan_data, Fs, low, high):
    # Define the filter parameters
    '''
    nyquist_freq = 0.5 * Fs
    lowcut = low / nyquist_freq
    highcut = high / nyquist_freq
    order = 4

    # Create the filter coefficients
    b, a = butter(order, [lowcut, highcut], btype='band')

    # Apply the filter to the EEG data
    filtered_data = filtfilt(b, a, chan_data)
    '''
    # Define filter parameters
    nyquist_freq = 0.5 * Fs
    cutoff_freqs = [low, high]
    numtaps = 101

    # Create filter coefficients using Hamming window function
    b = firwin(numtaps, cutoff_freqs, pass_zero=False, nyq=nyquist_freq, window='hamming')

    # Apply the filter to your EEG signal using filtfilt to avoid phase distortion
    filtered_data = filtfilt(b, 1, chan_data)
    return filtered_data

def filter_eeg(eeg, col_names, Fs, low, high, notch_freq=60.0):
    for chan in col_names:
        eeg[chan] = butter_notch(eeg[chan], Fs, notch_freq)
        eeg[chan] = butter_band(eeg[chan], Fs, low, high)

def power_spectrum(data, Fs):
    freqs = np.fft.fftfreq(n=len(data[data.columns[0]]), d=1/Fs)
    ps = {}
    for chan in data.columns:
        ft = np.fft.fft(data[chan])
        ps[chan] = 10*np.log10(np.abs(ft)**2)
    return freqs, ps

def plot_channel(data, channel, Fs, start=0, end=5):
    dt = 1/Fs
    chan_data = list(data[channel])
    npts = len(chan_data)
    times = np.arange(npts)*dt
    plt.xlabel('Times (s)')
    plt.ylabel('Voltage (uV)')
    plt.title(channel)
    plt.plot(times[int(start*Fs):int(end*Fs)], chan_data[int(start*Fs):int(end*Fs)])

def plot_power(freqs, ps, channel, Fs, max_freq):
    plt.plot(freqs, ps[channel]);
    #plt.yscale('log');
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (dB)')
    plt.xlim(0,max_freq);
    
def process_eeg(eeg_file, col_names, openbci_file, low=1, high=50):
    eeg = read_file(eeg_file, col_names)
    openbci, num_channels, Fs, column_names = read_openbci_file(openbci_file)
    idx = get_idx(openbci, column_names, eeg, col_names)
    if (idx < 0):
        return -1
    baseline_correct(openbci, column_names, eeg, col_names, idx)
    filter_eeg(eeg, col_names, Fs, low, high)
    return eeg, Fs