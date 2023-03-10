from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox
import random
import numpy as np
import datetime 
import pylsl
from collections import deque
import scipy.signal as signal
import threading
import sys

# Global variables (set in main)
eeg_inlet = None
buffer = None
last_sample = 0
refresh_rate = 60.0
session = 3
prefix = None

def lsl_thread():
    global buffer
    global last_sample
    global eeg_inlet
    # All this will do is read from LSL and append to buffer when not empty
    ch = 0
    
    print('LSL thread awake'); sys.stdout.flush();
    
    # Read LSL
    while True:
        sample, times = eeg_inlet.pull_sample()
        # Append sample if exists (from single channel, ch) to buffer
        if len(sample) > 0:
            out_path = prefix + "_data.txt"
            with open(out_path,"a") as fo:
                fo.write(f"{str(times)}, {str(sample)[1:-1]}\n")
    


def getRate(frequency, time_frames = 60):
    global refresh_rate

    indices = np.arange(0,time_frames)
    y = signal.square(2 * np.pi * frequency * (indices/refresh_rate))
    return (y + 1)/ 2

def flash(gates, shape, win):
    for i in range(len(gates)):
        if gates[i] == 1:
            shape[0].draw()
        win.flip()


def trainingSequence(training, trial_length, ISI, window, size):
    global buffer
    global eeg_inlet
    global prefix 

    on = visual.Polygon(win=window,edges=6,radius=size/4,units="pix",lineWidth=10,ori=30.0,fillColor='white')
    off = visual.Polygon(win=window,edges=6,radius=size/4,units="pix",lineWidth=10,ori=30.0,fillColor='black')
    output = dict()
    shape = list()
    shape.append(on)
    shape.append(off)
    
    for i in range(2):
        data,timestamp1 = eeg_inlet.pull_sample()
        core.wait(ISI)
    # record baseline
    data,timestamp2 = eeg_inlet.pull_sample()
    output['baseline'] = [timestamp1, timestamp2]

    ''' path = prefix + "_baseline.txt"
        with open(path,"a") as fo:
            for j in range(len(buffer)):
                fo.write(str(buffer.popleft())[1:-1])
                fo.write('\n')'''
    
    for rate in training:
        times = list()
        gates = getRate(rate, trial_length*60)
        data,timestamp = eeg_inlet.pull_sample()
        times.append(timestamp)
        flash(gates, shape, window)
        '''path = prefix + "_{:.2f}".format(rate) + "Hz.txt"  
        with open(path,"a") as fo:
            for i in range(len(buffer)):
                fo.write(str(buffer.popleft())[1:-1])
                fo.write('\n')'''

        data,timestamp = eeg_inlet.pull_sample()
        times.append(timestamp)
        window.flip()
        core.wait(ISI)
        output[rate] = times
    return output



if __name__ == "__main__":
    # Sampling variables
    fs = 250.          # sampling rate (Hz)
    dt = 1. / fs       # time between samples (s)
    dt_ms = dt * 1000. # time between samples (ms)
    buffer_len = 250   # num samples to store in buffer
    training_duration = 7
    buffer_len = buffer_len * training_duration
    buffer = deque(maxlen=buffer_len)
    
    prefix = "DataCollection/outputs/SSVEP/sess{}/".format(session) + datetime.datetime.now().isoformat()
    out_path = prefix + "_metadata.txt" 
    open(out_path, 'w').write('')
    out_path = prefix + "_baseline.txt" 
    open(out_path, 'w').write('')

     # Fill buffer with 0s
    for i in range(buffer_len):
        buffer.append([0.] * 8)
    

    # Initiate LSL streams and create inlets
    eeg_streams = pylsl.resolve_stream('type', 'EEG')
    eeg_inlet = pylsl.stream_inlet(eeg_streams[0], recover = False)
    print('Inlet Created'); sys.stdout.flush();
    
    # Launch LSL thread
    lsl = threading.Thread(target = lsl_thread, args = ())
    lsl.setDaemon(True) #turn into True 
    lsl.start()

    win = visual.Window(
        size=[600, 600],
        units="pix",
        fullscr=True,
        color='black'
    )

    training = np.arange(8.4,16,0.8)
    rng = np.random.default_rng()
    training = rng.permutation(training)

    output = trainingSequence(training, training_duration, 5, win, 800)
    win.close()

    out_path = prefix + "_metadata.txt"
    open(out_path, 'w').write('')
    with open(out_path,"a") as fo:
        fo.write(f"rate: start_time, end_time\n")
        for k,v in output.items():
            fo.write(f"{str(k)}: {str(v)[1:-1]}\n")