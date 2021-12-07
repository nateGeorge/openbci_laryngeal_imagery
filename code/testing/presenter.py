# imports - base
import time
from psychopy import visual, core, event, sound
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window
from psychopy import gui

# imports - homemade
import connect



# Presentation Parameters
class presentation_params:
    def __init__(self, debug=False, auto_end=True, placeholder=1):
        # auto_end - If True, close window automatically; If False, window must be closed elsewhere in program.
        # placeholder - Marks where the presentation currently stands; useful for moving forward/backward through the experiment
        self.debug = debug
        self.auto_end = auto_end
        self.placeholder = placeholder


class presenter:
    # Object for Presenting PsychoPy Slides with Common Features
    def __init__(self, params, dlg_settings):
        self.params = params
        self.cur_stims = [] # current stims
        self.placeholder = self.params.placeholder
        self.dlg_settings = dlg_settings
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

    # Handle Key Press
    def get_keypress(self):
        # Return Keys Pressed
        keys = event.getKeys()
        if self.params.debug:
            print(keys)
        return keys

    # Mangage Presentation of A Set of Slides
    def present_slide_set(self, set="", kwarg=""):
        """
        Run a set of slides then wait for key press to continue/exit

        Parameters:
          set: (str) the name of the slide set
          kwarg: (str) "--"-seperated keyword argument string for modifying slide sets


        #######  Test Sets ########
              - individual-test -- test the workflow for presenting an individual slide
              - individual-test-w-xconnectx -- test the workflow for presenting an individual slide and connect the recording EEG device
                  - previously individual-test-w-connect; changed to xconnectx to reflect that connection is no longer made in the presenter object and this slide set has been minimally changed
              - ssvep-test -- test making the SSVEP stimulus with this set
              - multi-slide-test -- test the workflow with multiple stimuli sequentially
        #######  Instruction Sets ########
              - pre-exp -- Present the instructions leading up to the experiment
              - pre-SSVEP -- Present the instructions leading up to SSVEP
              - pre-Motor-Real -- Present the instructions leading up to the Motor-Activity trial
              - pre-Motor-Imagined -- Present the instructions leading up to the Motor-Imagery trial
              - pre-Laryngeal-Activity-Real -- Present the instructions leading up to the Laryngeal Activity Real trial
              - pre-Laryngeal-Activity-Imained -- Present the instructions leading up to the Laryngeal Activity Imagined trial
              - pre-Laryngeal-Modulation-Real -- Present the instructions leading up to Laryngeal Modulation Real trial
              - pre-Laryngeal-Modulation-Imagined -- Present the instructions leading up to Laryngeal Modulation Imagined trial
        #######  Trial Sets ########
              - Check -- Present Elephant Question Stimulus and ask the participant to respond with the keyboard
                  - "Is the Elephant in the box? Click the 'y' for yes or 'n' for no."
              - SSVEP -- Present flashing stimulus
                  - "Is the Elephant in the box? Look at the flashing light on the right for yes. Look at the flashing light on the left for no."
              - Motor-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Raise your right arm for Yes. Raise your left arm for No."
              - Motor-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Imagin raising your right arm for Yes. Imagin raising your left arm for No."
              - Laryngeal-Activity-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Make a humming sound for Yes. Remain silent for No."
              - Laryngeal-Activity-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Imagine making a humming sound for Yes. Remain silent for No."
              - Laryngeal-Modulation-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Hum a high pitch sound for Yes. Hum a low pitch sound for No."
              - Laryngeal-Modulation-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Imagine humming a high pitch sound for Yes. Imagine humming a low pitch sound for No."
            """
        if set == "individual-test":
            if self.params.debug == True:
                print("Slide Set: Test Individual")

            Text_Stim = visual.TextStim(win=self.psyPy_window, text="This is a test")

            Text_Stim.draw()
            self.psyPy_window.flip()

            time.sleep(1)

        if set == "ssvep-test":
            print("Slide Set: SSVEP Test")

            frequency_Yes_Right = 12
            frequency_No_Left = 7
            stim_size = int(self.psyPy_window.size[0] / 3)
            SSVEP_Stim_Yes_Right = visual.MovieStim3(self.psyPy_window, f'media/{frequency_Yes_Right}Hz.avi', size=(stim_size, stim_size), pos=[stim_size * .75, 0])
            SSVEP_Stim_No_Left = visual.MovieStim3(self.psyPy_window, f'media/{frequency_No_Left}Hz.avi', size=(stim_size, stim_size), pos=[stim_size * -.75, 0])

            j = 0
            while (SSVEP_Stim_No_Left.status == 1 or SSVEP_Stim_Yes_Right.status == 1) or j == 0:
                SSVEP_Stim_No_Left.draw()
                SSVEP_Stim_Yes_Right.draw()
                self.psyPy_window.flip()
                j+=1

            Done_Text_Stim = visual.TextStim(win=self.psyPy_window, text="SSVEP Done")
            Done_Text_Stim.draw()
            self.psyPy_window.flip()

            time.sleep(1)

            #show SSVEP start time and duration

        if set == "multi-slide-test":

            # make/show text stim
            Text_Stim = visual.TextStim(self.psyPy_window, text="Multi-Slide Test: Text")
            Text_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)

            # make/show rect stim
            Rect_Stim = visual.Rect(self.psyPy_window, pos=((0, 0.25)), lineColor="red")
            Rect_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)

            # make/show movie stim
            stim_size = int(self.psyPy_window.size[0] / 3)
            Movie_Stim = visual.MovieStim3(self.psyPy_window, f'media/7Hz.avi', size=(stim_size, stim_size), pos=[0, 0])
            j=0
            while Movie_Stim.status == 1 or j == 0:
                Movie_Stim.draw()
                self.psyPy_window.flip()
                j+=1

            # make/show image stim
            Img_Stim = visual.ImageStim(self.psyPy_window, image=f'media/lemmling-2D-cartoon-elephant.jpg', mask=f'media/lemmling-2D-cartoon-elephant-transparency-mask.jpg', pos=((0, 0.25)), size=0.4)
            Img_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)

        while True:
            Response_Key_Text_Prompt = "Press: 'x' to Exit; right arrow to Move Forward; left arrow to Go Back"
            Response_Key_Text_Stim = visual.TextStim(win=self.psyPy_window, text=Response_Key_Text_Prompt, height=.04)
            Response_Key_Text_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(2)
            keys = self.get_keypress()
            print(keys)
            # Check for Response Key
            # If Key = x -> Exit
            if 'x' in keys:
                print('Found X Keys')
                break
            # If Key = right -> Move Forward
            if 'right' in keys:
                print('Found Right Keys')
                # add one to placeholder
                break
            # If Key = left -> Move Backward (repeat instructions/trial)
            if 'left' in keys:
                print('Found Left Keys')
                # subtract one from placeholder
                break

        # Test 2
        self.get_keypress()
        # End Test
