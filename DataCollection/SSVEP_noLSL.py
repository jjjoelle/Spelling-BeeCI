## ADJUST VARIABLES: 
#   1. prefix: for storing files, change variable or add relevant directories
#   2. session: relevant to prefix
#   3. refresh rate
#   

from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox
import random
import numpy as np
import datetime 
from collections import deque
import scipy.signal as signal


# Global variables (set in main)
refresh_rate = 60.0
session = 2
prefix = None

# Naknishi's APPROXIMATION METHOD 
# frequency we are aproximating
#
def getRate(frequency, time_frames = 60):
    global refresh_rate

    indices = np.arange(0,time_frames)
    y = signal.square(2 * np.pi * frequency * (indices/refresh_rate))
    return (y + 1)/ 2


# function for SSVEP flashing using 
# gates: from getRate() the approximation method
# shape: psychopy object
# win: window
def flash(gates, shape, win):
    time = 1/refresh_rate
    for i in range(len(gates)):
        if gates[i] == 1:
            shape[0].draw()
        win.flip()
        core.wait(time)

# training: list of frequencies
# trial length: 
# ISI: 
# window: 
# size: size of stimuli
def trainingSequence(training, trial_length, ISI, window, size):
    global prefix 

    on = visual.Polygon(win=window,edges=6,radius=size/4,units="pix",lineWidth=10,ori=30.0,fillColor='white')
    off = visual.Polygon(win=window,edges=6,radius=size/4,units="pix",lineWidth=10,ori=30.0,fillColor='black')
    output = dict()
    shape = list()
    shape.append(on)
    shape.append(off)
    
    # record baseline
    timestamp1 = datetime.datetime.now().isoformat()
    core.wait(ISI)
    timestamp2 = datetime.datetime.now().isoformat()
    output['baseline'] = [timestamp1, timestamp2]
    
    for rate in training:
        times = list()
        gates = getRate(rate, trial_length*60)

        timestamp = datetime.datetime.now().isoformat()
        times.append(timestamp)
        flash(gates, shape, window)
        timestamp = datetime.datetime.now().isoformat()
        times.append(timestamp)
        window.flip()
        core.wait(ISI)
        # store start and end timestamps of SSVEP frequency for epoching
        output[rate] = times
    return output



if __name__ == "__main__":
    # Sampling variables
    fs = 250.          # sampling rate (Hz)
    dt = 1. / fs       # time between samples (s)
    dt_ms = dt * 1000. # time between samples (ms)
    buffer_len = 250   # num samples to store in buffer
    training_duration = 5
    
    '''prefix = "DataCollection/outputs/SSVEP/sess{}/".format(session) + datetime.datetime.now().isoformat()
    '''


    win = visual.Window(
        size=[600, 600],
        units="pix",
        fullscr=False,
        color='black'
    )

    training = np.arange(8.4,16,0.8)
    rng = np.random.default_rng()
    training = rng.permutation(training)

    output = trainingSequence(training, training_duration, 5, win, 600)
    win.close()

    # this can be useful for checking timestamps of start and end for each frequency
    # annoying otherwise 
    '''out_path = prefix + "_metadata.txt"
    open(out_path, 'w').write('')
    with open(out_path,"a") as fo:
        fo.write(f"rate: start_time, end_time\n")
        for k,v in output.items():
            fo.write(f"{str(k)}: {str(v)[1:-1]}\n")'''