from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox
import random
import datetime 
# Function 1: print a prompt for X seconds 
#   -> t: seconds

# Function 2: print a list of prompts 
#   -> find permutations between 2 list or literally just go in order of list
#   -> x time 

def drawPrompt(prompt, t, window, window_size): 
    radius = window_size / 3
    height = radius * 2 
    prompt_size = radius / 3

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
    window.flip()
    core.wait(t)
    #window.flip()
    stopSign.draw()
    stop.draw()
    window.flip()
    core.wait(1)


def repeatTrials(trials, prompts, trial_duration, window, window_size):
    ordered_prompts = [''] * trials
    random.choice(prompts)
    outputs = dict()
    for i in range(trials):
        round = list()
        ordered_prompts[i] = random.choice(prompts)
        core.wait(2)
        round.append(datetime.datetime.now().strftime('%H:%M:%S'))
        drawPrompt(ordered_prompts[i], trial_duration, window, window_size)
        round.append(datetime.datetime.now().strftime('%H:%M:%S'))
        window.flip()
        outputs['trial_'+str(i)] = round
    outputs['prompts'] = ordered_prompts
    return outputs



win = visual.Window(size=[600, 600], color='black', units='pix', fullscr=False)

prompts = ['Right Fist', 'Left Fist', 'Right Arm', 'Left Arm']
output = repeatTrials(2, prompts, 3, win, 600)
win.close()

out_path = "DataCollection/outputs/MI_collection_" + datetime.datetime.now().isoformat() + ".txt"
open(out_path, 'w').write('')
with open(out_path,"a") as fo:
    for key,val in output.items():
        line = f"{key}: {val}\n"
        fo.write(line)
