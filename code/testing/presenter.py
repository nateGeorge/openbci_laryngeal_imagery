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

# Slide Parameters
class slide:
    # Object to Structure the attributes of a single slide
    def __init__(self, slide_type="", response_type="", real_or_imagined="", check_board=False, stim_list=[]):
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
        #   stim_list: list of stimuli for presenting
        self.slide_type = slide_type
        self.response_type = response_type
        self.real_or_imagined = real_or_imagined
        self.check_board = check_board
        self.stim_list = stim_list


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

    # Handle Single Slide Presentation
    def present_slide(self, slide, wait=0):
        # wait - Make window wait on screen for wait seconds
        if self.params.debug == True:
            print("Present Slide")
        # Decide which (if any) Stimuli to remove (from presenter.cur_stims)
        #   Check how many current stimuli there are
        #   Unset AutoDraw for Stimuli to remove
        #       subtract 1 from self.n_cur_stims for each stimulus to remove

        # Add slide.stim_list to presenter.cur_stims
        self.cur_stims = self.cur_stims + slide.stim_list

        # Loop through num cur_stim:
        for i in range(len(self.cur_stims)):
            # get stim_type
            stim_type = str(type(self.cur_stims[i])).split('.')[-2]

            if stim_type == "movie3":
                j = 0
                while self.cur_stims[i].status == 1 or j == 0:
                    self.cur_stims[i].draw()
                    self.psyPy_window.flip()
                    j+=1
        #   #   # handle movie (SSVEP) element stim
        #   # if stim type == array:
        #   #   #   handle multi-element stim
            else:
                # handle single element stim
                self.cur_stims[i].draw()
                self.psyPy_window.flip()
                time.sleep(1)

        # TEST: this return should really be an attribute for an object but I'll fix it later
        start_time = -1 # annoying bug
        return start_time

    # Mangage Presentation of A Set of Slides
    def present_slide_set(self, set=""):
        # Run a set of slides then wait for key press to continue/exit
        #   set:
        ########  Test Sets ########
        #       - individual-test -- test the workflow for presenting an individual slide
        #       - individual-test-w-connect -- test the workflow for presenting an individual slide and connect the recording EEG device
        #       - ssvep-test -- test making the SSVEP stimulus with this set
        #       - multi-slide-test -- test the workflow with multiple stimuli sequentially
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
        if set == "individual-test":
            if self.params.debug == True:
                print("Slide Set: Test Individual")

            Text_Stim = visual.TextStim(win=self.psyPy_window, text="This is a test")

            slide1 = slide(stim_list=[Text_Stim]) # use this to create stims, but for testing right now just add a stim to the self.cur_stims array

            self.present_slide(slide1, wait=1)

        if set == "individual-test-w-connect":
            print("Slide Set: Test Individual w/ Connect")
            print("Start Time - Set: " + str(time.time()))

            Text_Stim = visual.TextStim(win=self.psyPy_window, text="This is a test with OpenBCI connection included")

            slide1 = slide(stim_list=[Text_Stim]) # use this to create stims, but for testing right now just add a stim to the self.cur_stims array

            self.present_slide(slide1, wait=1)

        if set == "ssvep-test":
            print("Slide Set: SSVEP Test")
            frequency = 7
            stim_size = int(self.psyPy_window.size[0] / 3)
            SSVEP_Stim = visual.MovieStim3(self.psyPy_window, f'media/{frequency}Hz.avi', size=(stim_size, stim_size), pos=[0, 0])

            slide1 = slide(stim_list=[SSVEP_Stim])

            start_time = self.present_slide(slide1, wait=0)

            duration = time.time() - start_time
            print("Duration - Outside: " + str(duration))

        if set == "multi-slide-test":

            # make text stim
            Text_Stim = visual.TextStim(self.psyPy_window, text="Multi-Slide Test: Text")
            # make rect stim
            Rect_Stim = visual.Rect(self.psyPy_window, pos=((0, 0.25)), lineColor="red")
            # make movie stim
            stim_size = int(self.psyPy_window.size[0] / 3)
            Movie_Stim = visual.MovieStim3(self.psyPy_window, f'media/7Hz.avi', size=(stim_size, stim_size), pos=[0, 0])
            # make image stim
            Img_Stim = visual.ImageStim(self.psyPy_window, image=f'media/lemmling-2D-cartoon-elephant.jpg', mask=f'media/lemmling-2D-cartoon-elephant-transparency-mask.jpg', pos=((0, 0.25)), size=0.4)
                # append all stim to an array
            stims = [Text_Stim, Rect_Stim, Movie_Stim, Img_Stim]

            # create slide object with stims_list equal to the stim array
            slides = slide(stim_list=stims) # use this to create stims, but for testing right now just add a stim to the self.cur_stims array


            returned_start_time = self.present_slide(slides, wait=1)


        # Wait for Response Key After Instruction/Trial
            # Present Response Prompt at Bottom of Screen
            # Wait (indefinitely) for response
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