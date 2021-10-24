# imports
import time
from psychopy import visual, core, event, sound
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window
from psychopy import gui

# Presentation Parameters
class presentation_params:
    def __init__(self, debug=False, auto_end=True):
        # auto_end - If True, close window automatically; If False, window must be closed elsewhere in program.
        self.debug = debug
        self.auto_end = auto_end
        return

class presenter:
    # Object for Presenting a PsychoPy Slide with Common Features
    def __init__(self, params):
        self.params = params
        self.n_cur_stims = 0 # the current number of stimuli on screen
        if self.params.debug == True:
            print("Slide")

        # Open/Set PsychoPy Window Object
        self.psyPy_window = visual.Window()

        # Close PsychoPy Window (unless specified not to)
        if self.params.auto_end:
            self.psyPy_window.close()

    # Close Presentation
    def end_present(self, wait=0):
        # wait - Make Window wait wait seconds before closing
        if self.params.debug == True:
            print("End Present")
        time.sleep(wait)
        self.psyPy_window.close()

    # Handle Slide Presentation
    def present_slide(self):
        if self.params.debug == True:
            print("Present Slide")
        # Decide which (if any) Stimuli to remove
        #   Check how many current stimuli there are
        print("Num Current Stimuli: " + str(self.n_cur_stims))
        #   Unset AutoDraw for Stimuli to remove
        #       subtract 1 from self.n_cur_stims for each stimulus to remove

        # Decide Number of Stimuli to present (n)
        # Loop through n Stimuli
        #   Assign Position
        #   Assign Style
        #   Set AutoDraw
        #   Add 1 to self.n_cur_stims for each stimulus added
        # Flip Window
        pass
