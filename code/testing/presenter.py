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

# Slide Parameters
class slide:
    # Object to Structure the attributes of a single slide
    def __init__(self, slide_type="", response_type="", real_or_imagined="", check_board=False):
        # Take arguments for:
        #   slide_type:
        #       - instructions -- no annotations needed
        #       - trial -- manage annotations/labeling
        #   response_type:
        #       - SSVEP
        #       - Motor
        #       - Laryngeal-Activation
        #       - Laryngeal-Modulation
        #   real_or_imagined:
        #       - Real - The response was real (externally performed)
        #       - Imagined - The response was imagined (internally performed)
        #   check_board:
        #       - True -- Check data quality before
        #       - False -- Don't check data quality before slide
        self.slide_type = slide_type
        self.response_type = response_type
        self.real_or_imagined = real_or_imagined
        self.check_board = check_board


class presenter:
    # Object for Presenting a PsychoPy Slides with Common Features
    def __init__(self, params):
        self.params = params
        self.n_cur_stims = 0 # the current number of stimuli on screen
        if self.params.debug == True:
            print("Presenter")

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

    # Handle Single Slide Presentation
    def present_slide(self, slide):
        if self.params.debug == True:
            print("Present Slide")
            print("Num Current Stimuli: " + str(self.n_cur_stims))
        # Decide which (if any) Stimuli to remove
        #   Check how many current stimuli there are
        #   Unset AutoDraw for Stimuli to remove
        #       subtract 1 from self.n_cur_stims for each stimulus to remove

        # Specify Stimuli Presentation to Slide Parameters
            # Decide Number of Stimuli to present (n)
            # Loop through n Stimuli
            #   Assign Position
            #   Assign Style
            #   Set AutoDraw
            #   Add 1 to self.n_cur_stims for each stimulus added
            # Flip Window
        pass

    # Mangage Presentation of A Set of Slides
    def present_slide_set(self, set=""):
        #   set:
        ########  Test Sets ########
        #       - individual-test -- test the workflow for presenting an individual slide
        ########  Instruction Sets ########
        #       - pre-exp -- Present the instructions leading up to the experiment
        #       - pre-SSVEP -- Present the instructions leading up to SSVEP
        #       - pre-Motor-Real -- Present the instructions leading up to the Motor-Activity trial
        #       - pre-Motor-Imagined -- Present the instructions leading up to the Motor-Imagery trial
        #       - pre-Laryngeal-Activity-Real -- Present the instructions leading up to the Laryngeal Activity Real trial
        #       - pre-Laryngeal-Activity-Imained -- Present the instructions leading up to the Laryngeal Activity Imagined trial
        #       - pre-Laryngeal-Modulation-Real -- Present the instructions leading up to Laryngeal Modulation Real trial
        #       - pre-Laryngeal-Modulation-Imagined -- Present the instructions leading up to Laryngeal Modulation Imagined trial
        ########  Trial Sets ########
        #       - Check -- Present Elephant Question Stimulus and ask the participant to respond with the keyboard
        #           - "Is the Elephant in the box? Click the 'y' for yes or 'n' for no."
        #       - SSVEP -- Present flashing stimulus
        #           - "Is the Elephant in the box? Look at the flashing light on the right for yes. Look at the flashing light on the left for no."
        #       - Motor-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
        #           - "Is the Elephant in the box? Raise your right arm for Yes. Raise your left arm for No."
        #       - Motor-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
        #           - "Is the Elephant in the box? Imagin raising your right arm for Yes. Imagin raising your left arm for No."
        #       - Laryngeal-Activity-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
        #           - "Is the Elephant in the box? Make a humming sound for Yes. Remain silent for No."
        #       - Laryngeal-Activity-Imained -- Present Elephant Question Stimulus w/ appropriate response prompt
        #           - "Is the Elephant in the box? Imagine making a humming sound for Yes. Remain silent for No."
        #       - Laryngeal-Modulation-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
        #           - "Is the Elephant in the box? Hum a high pitch sound for Yes. Hum a low pitch sound for No."
        #       - Laryngeal-Modulation-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
        #           - "Is the Elephant in the box? Imagine humming a high pitch sound for Yes. Imagine humming a low pitch sound for No."
        if set == "test-individual":
            if self.params.debug == True:
                print("Slide Set: Test Individual")
            slide1 = slide()
            self.present_slide(slide1)
