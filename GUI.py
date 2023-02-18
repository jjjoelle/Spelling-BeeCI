from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox

win = visual.Window(
    size=[400, 400],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)

rect = visual.Polygon(
    win=win,
    edges=6,
    radius=100,
    units="pix",
    lineWidth=10,
    lineColor=[-1,-1,-1],
    ori=30.0
)

rect.draw()

win.flip()

event.waitKeys()

win.close()