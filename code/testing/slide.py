# imports
from psychopy import visual, core, event, sound
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window
from psychopy import gui

# Slide Parameters
class slide_params:
    def __init__(self, debug=False):
        self.debug = debug
        return

class slide:
    # Present a PsychoPy Slide with Common Features
    def __init__(self, params):
        self.params = params
        if self.params.debug == True:
            print("Slide")
        # Open PsychoPy Window
        psyPy_window = visual.Window()

        # Set/Return Window Object
        return
