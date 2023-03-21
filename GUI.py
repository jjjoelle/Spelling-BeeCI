from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox
import numpy as np
import scipy.signal as signal
import threading
import sys
import pylsl
import time

from live_bci import * 


'''win = visual.Window(
    size=[600, 600],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)

center = visual.Polygon(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    fillColor='#FFD700'
)
above = visual.Polygon(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    pos=(0,140),
    fillColor= '#DCDCDC'

)
below = visual.Polygon(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    pos=(0,-140),
    fillColor= '#DCDCDC'

)

leftUp = visual.Polygon(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    pos=(-118,65),
    fillColor= '#DCDCDC'

)
leftDown = visual.Polygon(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    pos=(-118,-65),
    fillColor= '#DCDCDC'

)
rightUp = visual.Circle(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    pos=(118,65),
    fillColor= '#DCDCDC'

)
rightDown = visual.Polygon(
    win=win,
    edges=6,
    radius=60,
    units="pix",
    lineWidth=10,
    ori=30.0,
    pos=(118,-65),
    fillColor= '#DCDCDC'

)

center.draw()
above.draw()
below.draw()
leftUp.draw()
leftDown.draw()
rightUp.draw()
rightDown.draw()

win.flip()

event.waitKeys()

win.close()
'''

SSVEP_record = False
ssvep_data = []

#def MI_lsl_thread(channels: list, filename: str, eeg_inlet):
def MI_lsl_thread(filename: str, eeg_inlet):
    # All this will do is read from LSL and append to file when not empty
    
    print('Motor imagery LSL thread awake'); sys.stdout.flush();
    
    # Read LSL
    while True:
        # state = MI_model(filename)
        # if state break

        sample, times = eeg_inlet.pull_sample()
        # Append sample if exists (from single channel, ch) to file
        if len(sample) > 0:
            with open(filename,"a") as fo:
                # TODO adjust to make this better
                fo.write(f"{str(times)}, {str(sample)[1:-1]}\n")

def SSVEP_lsl_thread(filename: str, eeg_inlet):
    global SSVEP_record 
    global ssvep_data

    # All this will do is read from LSL and append to file when not empty
    
    print('SSVEP LSL thread awake'); sys.stdout.flush();
    
    # Read LSL for duration
    # TODO make direction actually time 
    #start_time = time.monotonic()
    #while time.monotonic() - start_time < duration:
    while True:
        if not SSVEP_record:
            # if the flag is False, sleep for 0.1 seconds and check again
            ssvep_data = []
            time.sleep(0.1)
            #reset file? 
            continue

        sample, times = eeg_inlet.pull_sample()
        # Append sample if exists (from single channel, ch) to file
        if len(sample) > 0:
            ssvep_data.append(sample)
            #with open(filename,"a") as fo:
                # fo.write(f"{str(sample)[1:-1]}\n")




# TODO: 
# make positions relative to window_size 
def makeHexagonsOnMode(window, window_size, positions_center):
    allShapes = []
    color = '#DCDCDC'

    for tuple_xy in positions_center: 
        if tuple_xy == (0,0): 
            color = '#FFD700'
        else: 
            color = '#DCDCDC'

        shape = visual.Polygon(
            win=window,
            edges=6,
            radius=window_size/10,
            units="pix",
            lineWidth=10,
            ori=30.0,
            pos=tuple_xy,
            fillColor=color
        )
        allShapes.append(shape)
    return allShapes

    '''for tuple_xy in positions_bottom: 
        shape = visual.Polygon(
            win=window,
            edges=6,
            radius=window_size/10,
            units="pix",
            lineWidth=10,
            ori=30.0,
            pos=tuple_xy,
            fillColor='#FFD700'
        )
        allShapes.append(shape)'''



def makeTextOnMode(window, window_size, positions, text):
    textBoxes = []
    color = 'black'

    for i in range(len(positions)): 

        shape = visual.TextStim(window, text=text[i], pos=positions[i], color='black')
        textBoxes.append(shape)

    return textBoxes

def drawHexagons(window, allShapes): 
    for shape in allShapes:
        shape.draw()
    window.flip()


def getRate(frequency, refresh_rate = 60):

    indices = np.arange(0,refresh_rate)
    y = signal.square(2 * np.pi * frequency * (indices/refresh_rate))
    return (y + 1)/ 2

def flash(gates, win, refresh_rate):
    time = 1/refresh_rate
    i = 0 
    for i in range(len(gates[10.0][0])):
        for freqs, flash_shape in gates.items():
            if flash_shape[0][i] == 1:
                flash_shape[1].draw()
        win.flip()
        core.wait(time)

def flashMouseResponse(gates, win, refresh_rate, mouse, text=None):
    time = 1/refresh_rate
    i = 0 
    for i in range(len(gates[10.0][0])):
        for freqs, flash_shape in gates.items():
            if flash_shape[0][i] == 1:
                flash_shape[1].draw()
            flash_shape[2].draw()
            if mouse.isPressedIn(flash_shape[1], buttons=[0]):
                return freqs
        if text != None:
            text.draw()
        win.flip()
        core.wait(time)
    return None 

def repeatTrials(gates, window, refresh_rate, mouse):
    global SSVEP_record
    global ssvep_data


    check = None 
    text = None
    letters = ''
    while check == None:
        SSVEP_record = True
        for i in range(3):
            flashMouseResponse(gates, window, refresh_rate, mouse, text)
        check = classify_freq(ssvep_data)
        SSVEP_record = False
        
        if check != None:
            letters += ' ' + gates[check][2].text
            check = None
            text = visual.TextStim(window, text=letters, pos=(0, -250), color='black')
            text.draw()
            
        drawHexagons(window, shapes)
        core.wait(2)

        if len(letters) > 5: 
            break

    return letters

'''
window = visual.Window(
    size=[600, 600],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)
positions = [(0,0), (0,140), (0,-140), (-118,65), (-118,-65), (118,65), (118,-65)]
positions = [(0,0), (0,150), (0,-150), (-133,67), (-133,-67), (133,67), (133,-67)]
freqs =  [8.4,  9.2, 10.0 , 10.8, 11.6, 12.4, 13.2] #, 14.0 , 14.8, 15.6]
text = ["A", "B", "C", "D", "E", "F", "G"]
shapes = makeHexagonsOnMode(window, 600, positions)
text_boxes = makeTextOnMode(window, 600, positions, text)

gates = dict()
for i in range(len(freqs)): 
    rate = getRate(freqs[i], 30)
    shape = shapes[i]
    letter = text_boxes[i]
    gates[freqs[i]] = (rate, shape, letter)

#for i in range(5):
#    flash(gates, window, 30)
#core.wait(5)

mouse = event.Mouse(visible=True, newPos=None, win=window)
repeatTrials(gates, window, 30, mouse)
window.close()


check = None 
while check == None:
    check = flashMouseResponse(gates, window, 30, mouse)
text = visual.TextStim(window, text=str(check), pos=(0, -250), color='black')
text.draw()
drawHexagons(window, shapes)
core.wait(3)
'''



if __name__ == "__main__":
    SSVEP_record = False
    window_size = 600

    file = 'test.txt'
    eeg_streams = pylsl.resolve_stream('type', 'EEG')
    eeg_inlet = pylsl.stream_inlet(eeg_streams[0], recover = False)
    print('Inlet Created'); sys.stdout.flush();
    
    # Launch LSL thread
    lsl = threading.Thread(target = SSVEP_lsl_thread, args = (file, eeg_inlet))
    lsl.start()
    #lsl.setDaemon(True) 


    window = visual.Window(
        size=[600, 700],
        units="pix",
        fullscr=False,
        color=[1, 1, 1]
    )

   
    a = int(window_size/4)
    c = int(a / 2)
    offset = 100
    positions = [(0,0+offset), 
        (0,a+offset), 
        (0, -1 * a + offset), 
        (-1 * a, -1 * c + offset), 
        (-1 * a, c + offset), 
        (a, -1 * c + offset), 
        (a, c + offset)]
        # (-1 * a - offset, -offset),
        # (0, -offset),
        # (-1 * a + offset, -offset)
    #positions = [(0,0), (0,150), (0,-150), (-133,67), (-133,-67), (133,67), (133,-67)]
    freqs =  [8.4,  9.2, 10.0 , 10.8, 11.6, 12.4, 13.2]#, 14.0 , 14.8, 15.6]
    text = ["A", "B", "C", "D", "E", "F", "G"]#, 't', 't', 't']
    shapes = makeHexagonsOnMode(window, 600, positions)
    text_boxes = makeTextOnMode(window, 600, positions, text)

    gates = dict()
    for i in range(len(freqs)): 
        rate = getRate(freqs[i], 30)
        shape = shapes[i]
        letter = text_boxes[i]
        gates[freqs[i]] = (rate, shape, letter)



    mouse = event.Mouse(visible=True, newPos=None, win=window)
    repeatTrials(gates, window, 30, mouse)
    # lsl.cancel()
    window.close()