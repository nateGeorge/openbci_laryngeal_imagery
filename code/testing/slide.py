# imports
from psychopy import visual, core, event, sound
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window
from psychopy import gui

# Slide Parameters
class slide_params:
    def __init__(self, debug=False, auto_end=True):
        # auto_end - If True, close window automatically; If False, window must be closed elsewhere in program.
        self.debug = debug
        self.auto_end = auto_end
        return

class slide:
    # Object for Presenting a PsychoPy Slide with Common Features
    def __init__(self, params):
        self.params = params
        if self.params.debug == True:
            print("Slide")

        # Open/Set PsychoPy Window Object
        self.psyPy_window = visual.Window()

        # Close PsychoPy Window (unless specified not to)
        if self.params.auto_end:
            self.psyPy_window.close()
