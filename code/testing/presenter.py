# imports - base
import sys
import time
from psychopy import visual, core, event, sound, gui
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window
from psychopy import gui

# imports - other
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame as df

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
    def __init__(self, params, dlg_settings, cnct=None):
        self.params = params
        self.cur_stims = [] # current stims
        self.placeholder = self.params.placeholder
        self.dlg_settings = dlg_settings
        self.cnct = cnct
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

    # Wait for Key Press
    def wait_for_keypress(self):
        # present waiting stimulus
        # (infinite while loop)
            # get keys
            # check keys

        return

    # Mangage Presentation of A Set of Slides
    def present_slide_set(self, set="", elephant_ans=None, wait_after=True, not_ssvep_response_time=5):
        """
        Run a set of slides then wait for key press to continue/exit

        Parameters:
          set: (str) the name of the slide set
          elephant_ans: (bool) If True, the elephant question will be rendered such that the correct answer is True
          wait_after: (bool) If False, this method does not wait for a keypress at the end of the current slide set
          not_ssvep_response_time: (int) How many seconds to allow participant to respond for; SSVEP is 5 seconds (length of media file) regardless of this parameter


        #######  Test Sets ########
              - individual-test -- test the workflow for presenting an individual slide
              - individual-test-w-xconnectx -- test the workflow for presenting an individual slide and connect the recording EEG device
                - previously individual-test-w-connect; changed to xconnectx to reflect that connection is no longer made in the presenter object and this slide set has been minimally changed
              - multi-slide-test -- test the workflow with multiple stimuli sequentially
              - alpha-check-test -- test the workflow for checking alpha waves; eyes open and closed; returns epoch_info values as (1, 2) arrays
              - alpha-check-open -- check alpha waves when particpant eyes are open
              - alpha-check-closed -- check alpha waves when particpant eyes are closed
        #######  Instruction Sets ########
              - pre-exp -- Present the instructions leading up to the experiment
              - pre-alpha-check - instructions for the alpha wave check
              - pre-SSVEP -- Present the instructions leading up to SSVEP
              - pre-Motor-Real -- Present the instructions leading up to the Motor-Activity trial
              - pre-Motor-Imagined -- Present the instructions leading up to the Motor-Imagery trial
              - pre-Laryngeal-Activity-Real -- Present the instructions leading up to the Laryngeal Activity Real trial
              - pre-Laryngeal-Activity-Imained -- Present the instructions leading up to the Laryngeal Activity Imagined trial
              - pre-Laryngeal-Modulation-Real -- Present the instructions leading up to Laryngeal Modulation Real trial
              - pre-Laryngeal-Modulation-Imagined -- Present the instructions leading up to Laryngeal Modulation Imagined trial
        #######  Trial Sets ########
              - Elephant-Question -- Present Elephant Question Stimulus and ask the participant to respond with the keyboard; require correct answer
                  - "Is the Elephant in the box? Click the 'y' for yes or 'n' for no."
              - SSVEP -- Present flashing stimulus
                  - "Is the Elephant in the box? Look at the flashing light on the right for yes. Look at the flashing light on the left for no."
              - Motor-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Raise your right arm for Yes. Raise your left arm for No."
              - Motor-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Imagine raising your right arm for Yes. Imagine raising your left arm for No."
              - Laryngeal-Activity-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Make a humming sound for Yes. Remain silent for No."
              - Laryngeal-Activity-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Imagine making a humming sound for Yes. Remain silent for No."
              - Laryngeal-Modulation-Real -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Hum a high pitch sound for Yes. Hum a low pitch sound for No."
              - Laryngeal-Modulation-Imagined -- Present Elephant Question Stimulus w/ appropriate response prompt
                  - "Is the Elephant in the box? Imagine humming a high pitch sound for Yes. Imagine humming a low pitch sound for No."
            """
        # Test Sets ############################################################

        if set == "individual-test":
            if self.params.debug == True:
                print("Slide Set: Test Individual")

            Text_Stim = visual.TextStim(win=self.psyPy_window, text="This is a test")

            Text_Stim.draw()
            self.psyPy_window.flip()

            time.sleep(1)

        if set == "alpha-check-test":
            # provide instructions
            Instruction_Text_1 = "Close your eyes when you hear the beep"
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_Text_1)
            Instruct_Stim_1.draw()
            self.psyPy_window.flip()

            time.sleep(1)

            # prompt user to close their eyes (beep sound)
            c = sound.Sound('C', 1)
            g = sound.Sound('G', 1)
            c.play()
            start_time_closed = time.time() - self.cnct.exp_start_time
            time.sleep(5)

            # provide instructions to keep eyes open
            Instruction_Text_2 = "Keep eyes open until the next beep"
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_Text_2)
            Instruct_Stim_2.draw()
            self.psyPy_window.flip()

            # prompt user to open their eyes (beep sound)
            g.play()

            start_time_open = time.time() - self.cnct.exp_start_time
            duration_closed = start_time_open - start_time_closed

            # get last (duration_closed) seconds of data from board - alpha should be present
            data_closed = self.cnct.cnct.board_obj.get_current_board_data(int(duration_closed * self.cnct.cnct.sfreq))[0]
            print(self.cnct)


            time.sleep(5)

            # done + closing beep
            c.play()
            # get data from board

            duration_open = time.time() - start_time_open - self.cnct.exp_start_time

            # get last (duration_open) seconds of data from board - alpha should not be present
            data_open = self.cnct.cnct.board_obj.get_current_board_data(int(duration_open * self.cnct.cnct.sfreq))[0]
            # print(self.cnct.cnct.board_obj)


            Done_Stim = visual.TextStim(self.psyPy_window, text="Done")
            Done_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            self.psyPy_window.flip()

            # plot the data
            X = np.linspace(0, int(len(data_closed)/self.cnct.cnct.sfreq), int(len(data_closed)))
            print("Len of data_closed: " + str(len(data_closed)))
            plt.plot(X, data_closed)
            plt.title("Eyes Closed")
            plt.show()

            X = np.linspace(0, int(len(data_open)/self.cnct.cnct.sfreq), int(len(data_open)))
            print("Len of data_open: " + str(len(data_open)))
            plt.plot(X, data_open)
            plt.title("Eyes Open")
            plt.show()

            # set up epoch info
            epoch_label = ["alpha-closed", "alpha-open"]
            start_time = [start_time_closed, start_time_open]
            duration = [duration_closed, duration_open]

            # calculate fft of data
            timestep = 1/self.cnct.cnct.sfreq
            fft = df()
            exp = 1
            while 2**exp < len(data_closed):
                NFFT = 2**exp
                exp += 1
            # fft['Frequency'] = np.fft.fftfreq(NFFT)
            # fft['Frequency'] = np.fft.fftshift(fft['Frequency'])
            # fft = fft.query('Frequency>=0').mul(self.cnct.cnct.sfreq)
            fft['Eyes Closed Alpha PSD'] = (np.real(np.fft.fft(data_closed, n=NFFT))**2)[8:13] # analyzing channel 0 for now
            fft['Eyes Open Alpha PSD'] = (np.real(np.fft.fft(data_open, n=NFFT))**2)[8:13]


            # compare 10 Hz power with eyes closed to 10 Hz power without eyes closed

            #   # Get average FFT between 8 and 13 Hz
            avg_alpha_power_closed = np.mean(fft['Eyes Closed Alpha PSD']) # alpha-band: 8 to 13 Hz
            avg_alpha_power_open = np.mean(fft['Eyes Open Alpha PSD']) # alpha-band: 8 to 13 Hz

            # Get user to confirm that alpha waves appear correct
            print("Eyes Closed (Alpha): " + str(avg_alpha_power_closed))
            print("Eyes Open (Alpha): " + str(avg_alpha_power_open))

            confirm_dlg = gui.Dlg(title='Is the Alpha Band Activity Reasonable?')
            confirm_dlg.addText('Eyes-Closed Alpha wave power ( ' + str(avg_alpha_power_closed) + ' ) is ' + str(avg_alpha_power_closed/avg_alpha_power_open) + ' x Eyes-open Alpha wave power (' + str(avg_alpha_power_open) + ')')
            confirm_dlg.addField("Confirm Alpha-band Activity?", False)
            confirm = confirm_dlg.show()[0]
            print("Did I get True (I should)?")
            print("Check: " + str(confirm))

            alpha_ratio = avg_alpha_power_closed/avg_alpha_power_open # ratio of present alpha waves to not present

        if set == "alpha-check-closed":
            # provide instructions
            Instruction_Text_1 = "Close your eyes when you hear the beep"
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_Text_1)
            Instruct_Stim_1.draw()
            self.psyPy_window.flip()

            time.sleep(1)

            # prompt user to close their eyes (beep sound)
            c = sound.Sound('C', 1)
            g = sound.Sound('G', 1)
            c.play()
            start_time_closed = time.time() - self.cnct.exp_start_time
            time.sleep(5)

            # prompt user to open their eyes (beep sound)
            g.play()

            start_time_open = time.time() - self.cnct.exp_start_time
            duration_closed = start_time_open - start_time_closed

            # get last (duration_closed) seconds of data from board - alpha should be present
            data_closed = self.cnct.cnct.board_obj.get_current_board_data(int(duration_closed * self.cnct.cnct.sfreq))[0]
            print(self.cnct)
            # get data from board


            Done_Stim = visual.TextStim(self.psyPy_window, text="Done")
            Done_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            self.psyPy_window.flip()

            # plot the data
            X = np.linspace(0, int(len(data_closed)/self.cnct.cnct.sfreq), int(len(data_closed)))
            print("Len of data_closed: " + str(len(data_closed)))
            plt.plot(X, data_closed)
            plt.title("Eyes Closed")
            plt.show()

            # set up epoch info
            epoch_label = "alpha-closed"
            start_time = start_time_closed
            duration = duration_closed

            # calculate fft of data
            timestep = 1/self.cnct.cnct.sfreq
            fft = df()
            exp = 1
            while 2**exp < len(data_closed):
                NFFT = 2**exp
                exp += 1
            # fft['Frequency'] = np.fft.fftfreq(NFFT)
            # fft['Frequency'] = np.fft.fftshift(fft['Frequency'])
            # fft = fft.query('Frequency>=0').mul(self.cnct.cnct.sfreq)
            fft['Eyes Closed Alpha PSD'] = (np.real(np.fft.fft(data_closed, n=NFFT))**2)[8:13] # analyzing channel 0 for now

            #   # Get average FFT between 8 and 13 Hz
            avg_alpha_power_closed = np.mean(fft['Eyes Closed Alpha PSD']) # alpha-band: 8 to 13 Hz

            # Get user to confirm that alpha waves appear correct
            print("Eyes Closed (Alpha): " + str(avg_alpha_power_closed))

        if set == "alpha-check-open":
            # provide instructions
            Instruction_Text_1 = "Keep your eyes open when you hear the beep"
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_Text_1)
            Instruct_Stim_1.draw()
            self.psyPy_window.flip()

            time.sleep(1)

            # prompt user to close their eyes (beep sound)
            c = sound.Sound('C', 1)
            g = sound.Sound('G', 1)
            c.play()
            start_time = time.time() - self.cnct.exp_start_time
            time.sleep(5)

            # prompt user to open their eyes (beep sound)
            g.play()

            stop_time = time.time() - self.cnct.exp_start_time
            duration =  stop_time - start_time

            # get last (duration_open) seconds of data from board - alpha should not be present
            data_open = self.cnct.cnct.board_obj.get_current_board_data(int(duration * self.cnct.cnct.sfreq))[0] # only channel 1 is beign analyzed here

            Done_Stim = visual.TextStim(self.psyPy_window, text="Done")
            Done_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            self.psyPy_window.flip()

            # plot the data
            X = np.linspace(0, int(len(data_open)/self.cnct.cnct.sfreq), int(len(data_open)))
            print("Len of data_open: " + str(len(data_open)))
            plt.plot(X, data_open)
            plt.title("Eyes Open")
            plt.show()

            # set up epoch info
            epoch_label = "alpha-open"

            # calculate fft of data
            timestep = 1/self.cnct.cnct.sfreq
            fft = df()
            exp = 1
            while 2**exp < len(data_open):
                NFFT = 2**exp
                exp += 1
            # fft['Frequency'] = np.fft.fftfreq(NFFT)
            # fft['Frequency'] = np.fft.fftshift(fft['Frequency'])
            # fft = fft.query('Frequency>=0').mul(self.cnct.cnct.sfreq)
            fft['Eyes Open Alpha PSD'] = (np.real(np.fft.fft(data_open, n=NFFT))**2)[8:13] # analyzing channel 0 for now

            #   # Get average FFT between 8 and 13 Hz
            avg_alpha_power_open = np.mean(fft['Eyes Open Alpha PSD']) # alpha-band: 8 to 13 Hz

            # Get user to confirm that alpha waves appear correct
            print("Eyes Open (Alpha): " + str(avg_alpha_power_open))


        # Instruction Sets #####################################################

        if set == "pre-exp":
                instrctsTxt_1 = """As you go through this experiment you
                will answer yes or no to a simple question.
                You will see an elephant pop up on the screen.
                The elephant will either be inside of a box or not.
                """
                instrctsTxt_2 = """You will then be asked: 'Was the elephant
                in the box?' Please click the right arrow (→) to respond yes
                or the left arrow (←) to respond no.
                """
                instrctsTxt_3 = """Only after you have responded correctly will
                you respond again by following the instructions for indicating yes or no.
                """
                instrctsTxt_4 = """WARNING: This experimental protocol contains flashing lights that may pose a danger to individuals who suffer from epilepsy. If you are dangerously sensitive to rapidly flashing lights, please stop the experiment now by pressing the 'x' key.
                """

                instrct_stim_1 = visual.TextStim(self.psyPy_window, text=instrctsTxt_1)
                instrct_stim_2 = visual.TextStim(self.psyPy_window, text=instrctsTxt_2)
                instrct_stim_3 = visual.TextStim(self.psyPy_window, text=instrctsTxt_3)
                instrct_stim_4 = visual.TextStim(self.psyPy_window, text=instrctsTxt_4)

                instructions = [instrct_stim_1, instrct_stim_2, instrct_stim_3, instrct_stim_4]
                instructions[0].setAutoDraw(True)

                Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
                Continue_Instruct_Stim.setAutoDraw(True)
                self.psyPy_window.flip()

                i = 0
                while True:
                    # Check for right arrow key
                    keys = self.get_keypress()
                    # if right arrow is pressed
                    if 'right' in keys:
                        # unset autoDraw for current stim
                        instructions[i].setAutoDraw(False)

                        # if currentStim is not the last stim
                        if i < len(instructions) - 1:
                          # set autoDraw for next stim
                          instructions[i+1].setAutoDraw(True)
                          # flip window
                          self.psyPy_window.flip()
                          # increment counter
                          i += 1

                        # if currentStim is the last stim
                        else:
                          # unset autoDraw for Continue_Instruct_Stim
                          Continue_Instruct_Stim.setAutoDraw(False)
                          # flip window
                          self.psyPy_window.flip()
                          break

        if set == "pre-alpha-check-closed":
            instrctsTxt_1 = "In this section your EEG will be record with your eyes remaining closed."
            instrctsTxt_2 = "When you hear the first beep, close your eyes until you hear the second beep."

            instrct_stim_1 = visual.TextStim(self.psyPy_window, text=instrctsTxt_1)
            instrct_stim_2 = visual.TextStim(self.psyPy_window, text=instrctsTxt_2)

            instructions = [instrct_stim_1, instrct_stim_2]
            instructions[0].setAutoDraw(True)

            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)
            self.psyPy_window.flip()

            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

        if set == "pre-alpha-check-open":
            instrctsTxt_1 = "In this section your EEG will be record with your eyes remaining open."
            instrctsTxt_2 = "When you hear the first beep, do not blink or close your eyes until you hear the second beep."

            instrct_stim_1 = visual.TextStim(self.psyPy_window, text=instrctsTxt_1)
            instrct_stim_2 = visual.TextStim(self.psyPy_window, text=instrctsTxt_2)

            instructions = [instrct_stim_1, instrct_stim_2]
            instructions[0].setAutoDraw(True)

            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)
            self.psyPy_window.flip()

            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

        if set == "pre-alpha-check":
            instrctsTxt_1 = "In this section your EEG will be record with your eyes open, then closed."
            instrctsTxt_2 = "When you hear the first beep, close your eyes until you hear the second beep."
            instrctsTxt_3 = "When you hear the second beep, keep your eyes open until you hear the third beep"

            instrct_stim_1 = visual.TextStim(self.psyPy_window, text=instrctsTxt_1)
            instrct_stim_2 = visual.TextStim(self.psyPy_window, text=instrctsTxt_2)
            instrct_stim_3 = visual.TextStim(self.psyPy_window, text=instrctsTxt_3)

            instructions = [instrct_stim_1, instrct_stim_2, instrct_stim_3]
            instructions[0].setAutoDraw(True)

            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)
            self.psyPy_window.flip()

            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

        if set == "pre-SSVEP":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by focusing on one of two lights flashing on the screen"
            Instruction_2 = "Focus to the Right to answer Yes"
            Instruction_3 = "Focus to the Left to answer No"

            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        if set == "pre-Motor-Real":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by raising your right or left arm."
            Instruction_2 = "Raise your Right arm to answer Yes"
            Instruction_3 = "Raise your Left arm to answer No"
            Instruction_4 = "Remember to hold your arm raised until each trial is done"


            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)
            Instruct_Stim_4 = visual.TextStim(self.psyPy_window, text=Instruction_4)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3, Instruct_Stim_4]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        if set == "pre-Motor-Imagined":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by imagining raising your right or left arm."
            Instruction_2 = "Imagine raising your Right arm to answer Yes"
            Instruction_3 = "Imagine raising your Left arm to answer No"
            Instruction_4 = "Remember to imagine your arm raised until each trial is done"


            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)
            Instruct_Stim_4 = visual.TextStim(self.psyPy_window, text=Instruction_4)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3, Instruct_Stim_4]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        if set == "pre-Laryngeal-Activity-Real":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by humming or remaing silent."
            Instruction_2 = "Hum a constant sound to answer Yes"
            Instruction_3 = "Remain silent to answer No"
            Instruction_4 = "Remember to hum or remain silent until each trial is done"


            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)
            Instruct_Stim_4 = visual.TextStim(self.psyPy_window, text=Instruction_4)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3, Instruct_Stim_4]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        if set == "pre-Laryngeal-Activity-Imagined":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by imagining making a humming sound or remaing silent."
            Instruction_2 = "Imagine humming a constant sound to answer Yes"
            Instruction_3 = "Remain silent to answer No"
            Instruction_4 = "Remember to imgaine humming or remain silent until each trial is done"


            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)
            Instruct_Stim_4 = visual.TextStim(self.psyPy_window, text=Instruction_4)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3, Instruct_Stim_4]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        if set == "pre-Laryngeal-Modulation-Real":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by making a high-pitched humming sound or a low-pitched humming sound."
            Instruction_2 = "Make a high-pitched humming sound to answer Yes"
            Instruction_3 = "Make a low-pitched humming sound to answer No"
            Instruction_4 = "Remember to hum until each trial is done"


            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)
            Instruct_Stim_4 = visual.TextStim(self.psyPy_window, text=Instruction_4)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3, Instruct_Stim_4]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        if set == "Laryngeal-Modulation-Imagined":
            # make text instructions to present
            Instruction_1 = "In this section you will answer the Elephant-in-the-Box Question by imagining making a high-pitched humming sound or a low-pitched humming sound."
            Instruction_2 = "Imagine making a high-pitched humming sound to answer Yes"
            Instruction_3 = "Imagine making a low-pitched humming sound to answer No"
            Instruction_4 = "Remember to imagine humming until each trial is done"


            # convert text to TextStim's
            Instruct_Stim_1 = visual.TextStim(self.psyPy_window, text=Instruction_1)
            Instruct_Stim_2 = visual.TextStim(self.psyPy_window, text=Instruction_2)
            Instruct_Stim_3 = visual.TextStim(self.psyPy_window, text=Instruction_3)
            Instruct_Stim_4 = visual.TextStim(self.psyPy_window, text=Instruction_4)

            instructions = [Instruct_Stim_1, Instruct_Stim_2, Instruct_Stim_3, Instruct_Stim_4]
            instructions[0].setAutoDraw(True)

            # Add keyPress to continue feature
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)

            # show first instruction
            self.psyPy_window.flip()


            # present TextStim's in order
            # Loop through stimuli - pause each loop waiting for a keyPress to continue
            i = 0
            while True:
                # Check for right arrow key
                keys = self.get_keypress()
                # if right arrow is pressed
                if 'right' in keys:
                    # unset autoDraw for current stim
                    instructions[i].setAutoDraw(False)

                    # if currentStim is not the last stim
                    if i < len(instructions) - 1:
                      # set autoDraw for next stim
                      instructions[i+1].setAutoDraw(True)
                      # flip window
                      self.psyPy_window.flip()
                      # increment counter
                      i += 1

                    # if currentStim is the last stim
                    else:
                      # unset autoDraw for Continue_Instruct_Stim
                      instructions[i].setAutoDraw(False)
                      Continue_Instruct_Stim.setAutoDraw(False)
                      # flip window
                      self.psyPy_window.flip()
                      break

            self.psyPy_window.flip()

        # Trial Sets ###########################################################

        if set == "SSVEP":
            epoch_label = "ssvep"
            print("epoch_label: " + epoch_label)

            # Instructions
            # Add Autodrawn Stim explaing to press right-arrow to continue
            Continue_Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="Press \u25BA to Continue", pos=[0, -.6], height=.06)
            Continue_Instruct_Stim.setAutoDraw(True)
            Instruct_Stim = visual.TextStim(win=self.psyPy_window, text="For yes, focus on the right flashing box, and for no, focus on the left flashing box.")
            Instruct_Stim.setAutoDraw(True)
            self.psyPy_window.flip()
            while True:
                keys = self.get_keypress()
                if 'right' in keys:
                    Continue_Instruct_Stim.autoDraw = False
                    Instruct_Stim.autoDraw = False
                    self.psyPy_window.flip()
                    break


            frequency_Yes_Right = 12
            frequency_No_Left = 7
            stim_size = int(self.psyPy_window.size[0] / 3)
            SSVEP_Stim_Yes_Right = visual.MovieStim3(self.psyPy_window, f'media/{frequency_Yes_Right}Hz.avi', size=(stim_size, stim_size), pos=[stim_size * .80, 0])
            SSVEP_Stim_No_Left = visual.MovieStim3(self.psyPy_window, f'media/{frequency_No_Left}Hz.avi', size=(stim_size, stim_size), pos=[-stim_size * .80, 0])

            j = 0
            while (SSVEP_Stim_No_Left.status == 1 or SSVEP_Stim_Yes_Right.status == 1) or j == 0:
                SSVEP_Stim_No_Left.draw()
                SSVEP_Stim_Yes_Right.draw()
                if j==0:
                    start_time = time.time() - self.cnct.exp_start_time
                    print(start_time)
                self.psyPy_window.flip()
                j+=1
            duration = time.time() - start_time - self.cnct.exp_start_time

            Done_Text_Stim = visual.TextStim(win=self.psyPy_window, text="SSVEP Done")
            Done_Text_Stim.draw()
            self.psyPy_window.flip()

            time.sleep(1)

            #show SSVEP start time and duration

        if set == "Motor-Real":
            epoch_label = "mi-a" # motor imagery - actual
            print("epoch_label: " + epoch_label)

            Instruction_Stim = visual.TextStim(self.psyPy_window, text="Raise your right arm for Yes. Raise your left arm for No.")
            Instruction_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(3)

            Begin_Stim = visual.TextStim(self.psyPy_window, text="Begin")
            Begin_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            start_time = time.time() - self.cnct.exp_start_time

            self.psyPy_window.flip()
            time.sleep(not_ssvep_response_time)

            duration = time.time() - start_time - self.cnct.exp_start_time

        if set == "Motor-Imagined":
            epoch_label = "mi-i" # motor imagery - imagined
            print("epoch_label: " + epoch_label)

            Instruction_Stim = visual.TextStim(self.psyPy_window, text="Imagine raising your right arm for Yes. Imagine raising your left arm for No.")
            Instruction_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(3)

            Begin_Stim = visual.TextStim(self.psyPy_window, text="Begin")
            Begin_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            start_time = time.time() - self.cnct.exp_start_time

            self.psyPy_window.flip()
            time.sleep(not_ssvep_response_time)

            duration = time.time() - start_time - self.cnct.exp_start_time

        if set == "Laryngeal-Activity-Real":
            epoch_label = "lmi-a" # laryngeal motor imagery - actual
            print("epoch_label: " + epoch_label)

            Instruction_Stim = visual.TextStim(self.psyPy_window, text="Make a humming sound for Yes. Remain silent for No.")
            Instruction_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(3)

            Begin_Stim = visual.TextStim(self.psyPy_window, text="Begin")
            Begin_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            start_time = time.time() - self.cnct.exp_start_time

            self.psyPy_window.flip()
            time.sleep(not_ssvep_response_time)

            duration = time.time() - start_time - self.cnct.exp_start_time

        if set == "Laryngeal-Activity-Imagined":
            epoch_label = "lmi-i" # laryngeal motor imagery - imagined
            print("epoch_label: " + epoch_label)

            Instruction_Stim = visual.TextStim(self.psyPy_window, text="Imagine making a humming sound for Yes. Remain silent for No.")
            Instruction_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(3)

            Begin_Stim = visual.TextStim(self.psyPy_window, text="Begin")
            Begin_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            start_time = time.time() - self.cnct.exp_start_time

            self.psyPy_window.flip()
            time.sleep(not_ssvep_response_time)

            duration = time.time() - start_time - self.cnct.exp_start_time

        if set == "Laryngeal-Modulation-Real":
            epoch_label = "lmi-mod-a" # laryngeal motor imagery - modulation - actual
            print("epoch_label: " + epoch_label)

            Instruction_Stim = visual.TextStim(self.psyPy_window, text="Hum a high pitch sound for Yes. Hum a low pitch sound for No.")
            Instruction_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(3)

            Begin_Stim = visual.TextStim(self.psyPy_window, text="Begin")
            Begin_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            start_time = time.time() - self.cnct.exp_start_time

            self.psyPy_window.flip()
            time.sleep(not_ssvep_response_time)

            duration = time.time() - start_time - self.cnct.exp_start_time

        if set == "Laryngeal-Modulation-Imagined":
            epoch_label = "lmi-mod-i" # laryngeal motor imagery - modulation - imagined
            print("epoch_label: " + epoch_label)

            Instruction_Stim = visual.TextStim(self.psyPy_window, text="Imagine humming a high pitch sound for Yes. Imagine humming a low pitch sound for No.")
            Instruction_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(3)

            Begin_Stim = visual.TextStim(self.psyPy_window, text="Begin")
            Begin_Stim.draw()
            self.psyPy_window.flip()
            time.sleep(1)
            start_time = time.time() - self.cnct.exp_start_time

            self.psyPy_window.flip()
            time.sleep(not_ssvep_response_time)

            duration = time.time() - start_time - self.cnct.exp_start_time

        if set == "Elephant-Question":
            # make elephant stim
            Elephant_Stim = visual.ImageStim(self.psyPy_window, image=f'media/lemmling-2D-cartoon-elephant.jpg', mask=f'media/lemmling-2D-cartoon-elephant-transparency-mask.jpg', pos=((0, 0.25)), size=0.4)
            Elephant_Stim.draw()

            # make elephant question stim
            Question_Stim = visual.TextStim(self.psyPy_window, text="Is the Elephant in the box?", pos=((0, 0.75)), color="red")
            Question_Stim.draw()

            # make answering instructions stim
            Answering_Instructions_Stim = visual.TextStim(self.psyPy_window, text="Press Y for Yes and N for No", pos=((0, -0.75)), height=0.06)
            Answering_Instructions_Stim.draw()

            # make rect stim (pos based on elephant_ans)
            if elephant_ans == True:
                Ans_Box = visual.Rect(self.psyPy_window, pos=((0, 0.25)), lineColor="red")
                Ans_Box.draw()
                cor_ans = "y" # Y stands for Yes the Elephant is in the box
            elif elephant_ans == False:
                Ans_Box = visual.Rect(self.psyPy_window, pos=((0, -0.25)), lineColor="red")
                Ans_Box.draw()
                cor_ans = "n" # N stands for No the Elephant is not in the box
            else:
                print("WARNING: elephant_ans was not set")
            # render stimuli
            self.psyPy_window.flip()
            time.sleep(1)

            # check for correct response
            while True:
                keys = self.get_keypress()
                # incorrect response
                if ("y" in keys or "n" in keys) and (cor_ans not in keys):
                    Incorrect_Stim = visual.TextStim(self.psyPy_window, text="Incorrect: Press Y for in the box and N for not in the box", color="red")
                    Incorrect_Stim.draw()
                    self.psyPy_window.flip()
                    time.sleep(3)

                    Elephant_Stim.draw()
                    Question_Stim.draw()
                    Answering_Instructions_Stim.draw()
                    Ans_Box.draw()
                    # re-render the same elephant question
                    self.psyPy_window.flip()
                # correct response
                if cor_ans in keys:
                    # move forward to mock/real stimulus
                    Correct_Stim = visual.TextStim(self.psyPy_window, text="Correct")
                    Correct_Stim.draw()
                    self.psyPy_window.flip()
                    time.sleep(1)
                    break


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

        # Wait for keypress at end of slide set
        if wait_after:
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
                    self.psyPy_window.close()
                    self.cnct.end_connection(save=True)
                    sys.exit(0)
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

        if set in ["alpha-check-closed", "alpha-check-open", "SSVEP", "Motor-Real", "Motor-Imagined", "Laryngeal-Activity-Real", "Laryngeal-Activity-Imagined", "Laryngeal-Modulation-Real", "Laryngeal-Modulation-Imagined"]:
            self.cnct.cnct.metadata["slides"].append(epoch_label)

            epoch_info = {"condition_start_time": start_time,
                          "duration": duration,
                          "label": epoch_label}
            self.cnct.cnct.annotations.append(epoch_info)

            if set == "alpha-check-closed":
                return epoch_info, avg_alpha_power_closed

            if set == "alpha-check-open":
                return epoch_info, avg_alpha_power_open


        else:
            epoch_info = None

        return epoch_info
