import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from import_data import *
from preprocessing import *

def plot_channel(data, channel, Fs, start=0, end=5):
    dt = 1/Fs
    chan_data = list(data[channel])
    npts = len(chan_data)
    times = np.arange(npts)*dt
    plt.xlabel('Times (s)')
    plt.ylabel('Voltage (uV)')
    plt.title(channel)
    plt.plot(times[int(start*Fs):int(end*Fs)], chan_data[int(start*Fs):int(end*Fs)])
'''
def plot_power(freqs, ps, channel, Fs, max_freq):
    plt.plot(freqs, ps[channel]);
    #plt.yscale('log');
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (dB)')
    plt.xlim(0,max_freq);
'''
def plot_power(power,channel,max_freq):
    x = list(power['freqs'])
    y = list(power[channel])
    plt.plot(x,y)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (dB)')
    plt.xlim(0,max_freq);
    
def plot_ssvep(eeg, Fs=250):
    for chan in eeg.columns:
            plt.figure()
            #plt.xlim(4,5)
            plot_channel(eeg, chan, Fs)
            
def plot_mi(eeg, Fs=250):
    for chan in eeg.columns:
        for i in range(4):
            plt.figure()
            plt.xlim(i*5+0.5,(i+1)*5-0.5)
            plot_channel(eeg, chan, Fs, start=i*5, end=(i+1)*5)