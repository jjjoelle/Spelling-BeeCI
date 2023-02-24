# Example python code for:
# - Animating live Python data
# - Reading LSL in real-time
# - Doing something with that LSL data in real-time
#   - ^ but also multi-threaded
#
# Intended demo uses synthetic stream + LSL output using OpenBCI GUI
# but it should work with any LSL stream (just make sure to set fs)
#
# Created......: 05May22 [ollie-d]
# Last Modified: 05May22 [ollie-d]

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
x = None
buffer = None
line = None
ax = None
last_sample = 0

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
            last_sample = sample
            buffer.append(last_sample)
    

def drawPrompt(prompt, t, window, window_size): 
    radius = window_size / 3
    height = radius * 2 
    prompt_size = radius / 3
    times = list()

    circle = visual.Circle(window, radius=radius, edges=100, fillColor='white', lineColor='black', lineWidth=3)
    exclamation_mark = visual.TextStim(window, text='!', pos=[0, 0], height=radius, color='red')
    rectangle = visual.Rect(window, width=height, height=height, fillColor='white', lineColor='black')
    prompt = visual.TextStim(window, text=prompt, pos=[0, 0], height=prompt_size, color='black')
    stopSign = visual.Polygon(window, edges=8, radius=radius, units='pix', ori=22.5, pos=[0,0], fillColor='red')
    stop = visual.TextStim(window, text='STOP', pos=[0, 0], height=prompt_size, color='white')

    circle.draw()
    exclamation_mark.draw()
    window.flip()
    core.wait(1.5)
    #window.flip()
    rectangle.draw()
    prompt.draw()
    data, timestamp = eeg_inlet.pull_sample()
    times.append(data, timestamp)
    window.flip()
    core.wait(t)
    #window.flip()
    stopSign.draw()
    stop.draw()
    data, timestamp = eeg_inlet.pull_sample()
    times.append(data, timestamp)
    window.flip()
    core.wait(1)
    return times

def repeatTrials(trials, prompts, trial_duration, window, window_size):
    ordered_prompts = [''] * trials
    random.choice(prompts)
    outputs = dict()
    for i in range(trials):
        ordered_prompts[i] = random.choice(prompts)
        core.wait(2)
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
    buffer_len = 250   # num samples to store in buffer
    buffer = deque(maxlen=buffer_len)
    
    # Fill buffer with 0s
    for i in range(buffer_len):
        buffer.append(0.)
    
    # Create an x-axis of spaced values in seconds
    x = np.linspace(0, buffer_len*dt_ms, num=buffer_len)
    

    # Initiate LSL streams and create inlets
    eeg_streams = pylsl.resolve_stream('type', 'EEG')
    eeg_inlet = pylsl.stream_inlet(eeg_streams[0], recover = False)
    print('Inlet Created'); sys.stdout.flush();
    
    # Launch LSL thread
    lsl = threading.Thread(target = lsl_thread, args = ())
    lsl.setDaemon(False)
    lsl.start()
    
    # Launch animation
    win = visual.Window(size=[600, 600], color='black', units='pix', fullscr=False)

    prompts = ['Right Fist', 'Left Fist', 'Right Arm', 'Left Arm']
    output = repeatTrials(2, prompts, 3, win, 600)
    win.close()

    prefix = datetime.datetime.now().isoformat() + ".txt"
    out_path = "DataCollection/outputs/MI_metadata_" + prefix
    open(out_path, 'w').write('')
    with open(out_path,"a") as fo:
        for key,val in output.items():
            line = f"{key}: {val}\n"
            fo.write(line)

    out_path = "DataCollection/outputs/MI_collection_" + prefix
    open(out_path, 'w').write('')
    with open(out_path,"a") as fo:
        fo.write(buffer)