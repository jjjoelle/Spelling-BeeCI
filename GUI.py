from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox

win = visual.Window(
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
rightUp = visual.Polygon(
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