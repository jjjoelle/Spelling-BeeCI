from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox
import random
import numpy as np
import datetime 
import pylsl
from collections import deque

import threading
import sys

# Global variables (set in main)
eeg_inlet = None
buffer = None
last_sample = 0
prefix = ''
session = 2
file_paths = dict()

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
            #last_sample = sample
            buffer.append(sample)
    
# Function 1: print a prompt for X seconds 
#   -> t: seconds

# Function 2: print a list of prompts 
#   -> find permutations between 2 list or literally just go in order of list
#   -> x time 

def drawPrompt(prompt_text, t, window, window_size): 
    global file_paths
    global buffer
    global eeg_inlet

    radius = window_size / 3
    height = radius * 2 
    prompt_size = radius / 3
    times = list()

    circle = visual.Circle(window, radius=radius, edges=100, fillColor='white', lineColor='black', lineWidth=3)
    exclamation_mark = visual.TextStim(window, text='!', pos=[0, 0], height=radius, color='red')
    rectangle = visual.Rect(window, width=height, height=height, fillColor='white', lineColor='black')
    prompt = visual.TextStim(window, text=prompt_text, pos=[0, 0], height=prompt_size, color='black')
    stopSign = visual.Polygon(window, edges=8, radius=radius, units='pix', ori=22.5, pos=[0,0], fillColor='red')
    stop = visual.TextStim(window, text='STOP', pos=[0, 0], height=prompt_size, color='white')

    # MI incoming
    circle.draw()
    exclamation_mark.draw()
    window.flip()
    core.wait(1.5)

    # begin MI
    rectangle.draw()
    prompt.draw()
    data, timestamp = eeg_inlet.pull_sample()
    times.append(timestamp)
    window.flip()
    core.wait(t)
    path = prefix + "_" + file_paths[prompt_text] + ".txt"  
    with open(path,"a") as fo:
        for i in range(len(buffer)):
            fo.write(str(buffer.popleft())[1:-1])
            fo.write('\n')
    
    # stop MI
    stopSign.draw()
    stop.draw()
    data, timestamp = eeg_inlet.pull_sample()
    times.append(timestamp)
    window.flip()
    core.wait(1)

    return times


def repeatTrials(trials, prompts, trial_duration, window, window_size):
    global buffer

    ordered_prompts = prompts * (int(trials/4))
    ordered_prompts = random.sample(prompts, trials)
    outputs = dict()
    for i in range(2):
        core.wait(trial_duration)
        # record baseline
        path = prefix + "_baseline.txt"
        with open(path,"a") as fo:
            for j in range(len(buffer)):
                fo.write(str(buffer.popleft())[1:-1])
                fo.write('\n')
    
    for i in range(trials):
        core.wait(trial_duration)
        # record no MI
        path = prefix + "_NOMI.txt"
        with open(path,"a") as fo:
            for j in range(len(buffer)):
                fo.write(str(buffer.popleft())[1:-1])
                fo.write('\n')
        # act and record MI
        times = drawPrompt(ordered_prompts[i], trial_duration, window, window_size)
        window.flip()
        outputs['trial_'+str(i)] = times

    outputs['prompts'] = ordered_prompts
    return outputs


if __name__ == "__main__":
    # MAKE SURE YOU HAVE AN LSL STREAM RUNNING
    # (for this example I use synthetic data from OpenBCI GUI)

    # Sampling variables
    fs = 250.          # sampling rate (Hz)
    dt = 1. / fs       # time between samples (s)
    dt_ms = dt * 1000. # time between samples (ms)
    trial_duration = 5
    buffer_len = 250   # num samples to store in buffer
    buffer_len = buffer_len * trial_duration
    buffer = deque(maxlen=buffer_len)

    # set up file info 
    file_paths = {'Right Fist': 'MIRF', 'Left Fist': 'MILF', 'Swim': 'MISw', 'Typing': 'MITy'}
    prefix = prefix = 'DataCollection/outputs/MI/sess{}/".format(session)' + datetime.datetime.now().isoformat() + '_MI'
    out_path = f"{prefix}_metadata.txt"
    open(out_path, 'w').write('')
    out_path = f"{prefix}_baseline.txt"
    open(out_path, 'w').write('')
    
    # Fill buffer with 0s
    for i in range(buffer_len):
        buffer.append([0.]*8)
        
    # Initiate LSL streams and create inlets
    eeg_streams = pylsl.resolve_stream('type', 'EEG')
    eeg_inlet = pylsl.stream_inlet(eeg_streams[0], recover = False)
    print('Inlet Created'); sys.stdout.flush();
    
    # Launch LSL thread
    lsl = threading.Thread(target = lsl_thread, args = ())
    lsl.setDaemon(True) #turn into True 
    lsl.start()
    
    # show prompts on screen
    win = visual.Window(size=[600, 600], color='black', units='pix', fullscr=True)
    prompts = ['Right Fist', 'Left Fist', 'Swim', 'Typing']
    output = repeatTrials(8, prompts, trial_duration, win, 600)
    win.close()

    with open(out_path,"a") as fo:
        for key,val in output.items():
            line = f"{key}: {val}\n"
            fo.write(line)


