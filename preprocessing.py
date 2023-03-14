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

def baseline_correct_openbci(openbci, names, eeg, idx):
    baseline_data = openbci.iloc[idx-1000:idx]
    for i,chan in enumerate(eeg.columns):
        baseline_mean = baseline_data[names[i+1]].mean()
        eeg[chan] = eeg[chan] - baseline_mean

def baseline_correct(eeg_data, baseline_data):
    bc_df = pd.DataFrame()
    for chan in eeg_data.columns:
        bc_df[chan] = eeg_data[chan] - baseline_data[chan].mean()
    return bc_df
        

def butter_notch(chan_data, Fs=250, notch_freq=60.0):
    # Define the filter parameters
    Q = 30.0

    # Calculate the notch filter coefficients
    w0 = notch_freq / (Fs / 2)
    b, a = iirnotch(w0, Q)

    # Apply the filter to the EEG data
    notched_data = filtfilt(b, a, chan_data)
    return notched_data

def butter_band(chan_data, Fs, low, high):
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

def fir_notch(chan_data, Fs=250, notch_freq=60.0):
    nyquist_freq = 0.5 * Fs
    numtaps = 101
    b = firwin(numtaps, notch_freq / nyquist_freq, window='hamming')
    notched_data = filtfilt(b, 1, chan_data)
    # Scale the filtered signal to remove any DC offset
    notched_data = notched_data - np.mean(notched_data)
    return notched_data

def fir_band(chan_data, Fs, low, high):
    # Define the filter parameters
    # Define filter parameters
    nyquist_freq = 0.5 * Fs
    cutoff_freqs = [low, high]
    numtaps = 101

    # Create filter coefficients using Hamming window function
    b = firwin(numtaps, cutoff_freqs, pass_zero=False, nyq=nyquist_freq, window='hamming')

    # Apply the filter to your EEG signal using filtfilt to avoid phase distortion
    filtered_data = filtfilt(b, 1, chan_data)
    return filtered_data
'''
def filter_eeg(eeg, Fs, low, high, notch_freq=60.0):
    for chan in eeg.columns:
        eeg[chan] = butter_notch(eeg[chan], Fs, notch_freq)
        eeg[chan] = butter_band(eeg[chan], Fs, low, high)

def chop_ends(eeg, Fs, amt=0.5):
    chopped_eeg = pd.DataFrame()
    for chan in eeg.columns:
        chopped_eeg[chan] = eeg[chan][int(Fs*amt):int(-Fs*amt)]
    return chopped_eeg       
'''
def filter_eeg(eeg, Fs, low, high, notch_freq=60.0):
    filtered_eeg = pd.DataFrame()
    for chan in eeg.columns:
        #filtered_eeg[chan] = eeg[chan][int(Fs*0.5):int(-Fs*0.5)]
        filtered_eeg[chan] = butter_notch(eeg[chan], Fs, notch_freq)
        filtered_eeg[chan] = butter_band(filtered_eeg[chan], Fs, low, high)
    return filtered_eeg

def power_spectrum(eeg, Fs):
    freqs = np.fft.fftfreq(n=len(eeg[eeg.columns[0]]), d=1/Fs)
    ps = {}
    for chan in eeg.columns:
        ft = np.fft.fft(eeg[chan])
        ps[chan] = 10*np.log10(np.abs(ft)**2)
    return freqs, ps
    
def process_eeg(eeg_file, col_names, openbci_file, low=1, high=100):
    eeg = read_file(eeg_file, col_names)
    openbci, num_channels, Fs, column_names = read_openbci_file(openbci_file)
    idx = get_idx(openbci, column_names, eeg, col_names)
    if (idx < 0):
        return -1
    baseline_correct_openbci(openbci, column_names, eeg, col_names, idx)
    filtered_eeg = filter_eeg(eeg, Fs, low, high)
    return filtered_eeg, Fs