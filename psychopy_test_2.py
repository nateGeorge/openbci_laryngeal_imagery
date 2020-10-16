import psychopy
from psychopy import visual, core, event
import time
from pyglet import media

window = visual.Window()

Hz_7 = visual.MovieStim.loadMovie(window, 'f7Hz.avi')

Hz_7.draw(window)
window.flip()
