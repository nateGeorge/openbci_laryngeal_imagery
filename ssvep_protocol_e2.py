import time
import datetime
import sys
import numpy as np
import pandas as pd
from psychopy import visual, core, event
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window

class timeData:
    """ This is a class that stores start times, stop times, and labels for time data.

    Attributes
    ----------
    startTime : int
        The time the labeled data started being recorded.
    stopTime : int
        The time the labeled data stopped being recorded.
    Label : string
        A string corresponding to the type of data being recorded.
        Could be one of:
            S - ssvep
            T - traditional motor imagery
            L - laryngeal motor imagery
    """
    def __init__(self, startTime, label, stopTime=None):
        self.startTime = startTime
        self.stopTime = stopTime if stopTime is not None else None
        self.label = label

class expData:
    """ This is a class to store the important information about the experiment for when the experiment is over.

    Attributes
    ----------
    allTimeData : array
        An array of timeData objects.
    rawEEG : obj
        An mne object that stores the raw EEG data.
    expDate : obj
        A datetime.date object which stores the date.
    participantID : int
        An int containing the participant's.
    descriptions : bool
        A boolean to represent yes or no; True equals yes.
    """
    #add a method to create an mne.annotations object
    #raw = mne.io.RawArray(data[:16, :])


    def __init__(self, allTimeData):
        #create parameters required in the init function which record the following
        #important times
        #the eeg data
        #the date and time
        self.onsets = []
        self.durations = []
        self.descriptions = []

    def startBCI(self, serialPort='COM4', wifi=False):
        """Starts the connection/stream of the openBCI headset

        Parameters
        ----------
        serialPort : str
            The serial port for connecting to the headset via bluetooth.
            Could be one of:
                COM4
                COM3
                /dev/ttyUSB0
        wifi : bool
            Whether to use wifi connection or not (bluetooth instead)
        """
        #connect to headset
        params = BrainFlowInputParams()

        # cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
        # bluetooth is 2
        if wifi:
            params.ip_address = '10.0.0.220'
            params.ip_port = 6227
            board = BoardShim(6, params)
        else:  # bluetooth
            params.serial_port = serialPort
            board = BoardShim(2, params)


        board.prepare_session()
        # by default stores 7.5 minutes of data; change num_samples higher for more
        # sampling rate of 1k/s, so 450k samples in buffer
        board.start_stream()
        time.sleep(3)

        self.board = board

    def stopBCI(self):
        """Stops the openBCI datastream and disconnects the headset

            Parameters
            ----------
            board : obj
                OpenBCI connection object.

        """

        time.sleep(3)
        rawData = self.board.get_board_data() #save this rawData object as a pickle file
        self.board.stop_stream()
        board.release_session() #this is for disconnecting the headset

        number_to_1020 = {1: 'Fp1',
                 2: 'Fp2',
                 3: 'C3',
                 4: 'C4',
                 5: 'T5',
                 6: 'T6',
                 7: 'O1',
                 8: 'O2',
                 9: 'F7',
                 10: 'F8',
                 11: 'F3',
                 12: 'F4',
                 13: 'T3',
                 14: 'T4',
                 15: 'P3',
                 16: 'P4'}

        ch_types = ['eeg'] * 16
        ch_names = list(number_to_1020.values())

        info = mne.create_info(ch_names=ch_names, sfreq=125, ch_types=ch_types)

        raw = mne.io.RawArray(rawData[1:17], info) #save this RawArray as a pickle file

        annot = mne.Annotations(self.onsets, self.durations, self.descriptions)

        raw.set_annotations(annot)

        montage = make_standard_montage('standard_1020')
        raw.set_montage(montage)

        raw.save()

def miPrompt(window, miType):
    """Presents the prompt for the traditional motor imagery (TMI) response.

    Parameters
    ----------
    window : obj
        Visual window object.
    miType : string
        Type of motor imagery which needs to be prompted
        Could be one of:
            t - Traditional
            l - Laryngeal

    Returns
    -------
    list of floats
        the times the TMI response started and time it ended
    """
    window.flip()

    holdTime = 5 #how long the participant should imainge for

    if miType == "t":
        responseInstr = ["imagine raising your right arm", "imagine raising your left arm"]
    elif miType == "l":
        responseInstr = ["imagine making a high-pitch sound", "imagine making a low-pitch sound"]

    #present a prompt that asks the participant to think about raising their right arm for yes and left arm for no
    tmiPromptText_1 = "For YES, "+ responseInstr[0] +" for "+ str(holdTime) +" seconds."
    tmiPromptStim_1 = visual.TextStim(win=window, text=tmiPromptText_1, pos=(0.5, 0.3), wrapWidth=.5)
    tmiPromptText_2 = "For NO, "+ responseInstr[1] +" for "+ str(holdTime) +" seconds."
    tmiPromptStim_2 = visual.TextStim(win=window, text=tmiPromptText_2, pos=(-0.5, 0.3), wrapWidth=.5)

    tmiPromptStim_1.draw()
    tmiPromptStim_2.draw()
    window.flip()

    clock = core.Clock()

    start = clock.getTime()
    time.sleep(holdTime)
    stop = clock.getTime()

    window.flip()

    return start, stop

def ssvepStim(window):
    """Presents the SSVEP flashing stimuli

    Parameters
    ----------
    window : obj
        Visual window object.

    Returns
    -------
    list of floats
        the times the ssvep stimulus started and time it ended
    """
    ssvep_frequencies: list=[7.5, 15]
    ssvep_time: int=5
    square1 = visual.Rect(win=window, size=(0.5, 0.5), pos=(-0.6, 0), fillColor='white', opacity=0, autoDraw=True)
    square2 = visual.Rect(win=window, size=(0.5, 0.5), pos=(0.6, 0), fillColor='white', opacity=0, autoDraw=True)

    clock = core.Clock()
    frequency1, frequency2 = ssvep_frequencies  # in Hz
    time_on1 = 1 / (frequency1 * 2)  # should be on for have a cycle, off for half a cycle
    time_on2 = 1 / (frequency2 * 2)

    start = clock.getTime()
    start1 = start
    start2 = start1  # copies it; changing start1 does not change start2
    epoch_start = time.time()
    while True:
        timenow = clock.getTime()
        if timenow - start1 >= time_on1:
            square1.opacity = not square1.opacity
            start1 = timenow
            window.update()

        if timenow - start2 >= time_on2:
            square2.opacity = not square2.opacity
            start2 = timenow
            window.update()

        if timenow - start > ssvep_time:
            break

    epoch_end = time.time()
    square1.autoDraw = False
    square2.autoDraw = False
    window.flip()
    return epoch_start, epoch_end

def checkAns(window, yes_nos, iTrials):
    """Checks to see if the correct answer was given to the primary stage of the experimental trial.

    Parameters
    ----------
    window : obj
        Visual window object.
    yes_nos : array
        Array of true's and false's corresponding to the correct answers to each trial; zero-indexed.
    iTrials : int
        Number corresponding to the current trial which needs to be checked.
    Returns
    -------
    bool
        Returns True if the answer was correct and False if the answer was incorrect
    """
    #set the correct answer to a variable called corAns
    corAns = yes_nos[iTrials - 1]
    thrAns = None

    #present instructions for keypress responses: -> for yes and <- for no

    #while loop for getting keys
        #
    while True:
        keys = getKeys()

        if 'right' in keys:
            thrAns = True
        if 'left' in keys:
            thrAns = False

        if 'q' and 'p' in keys:
            window.close()
            sys.exit(0)

        if thrAns != None:
            if thrAns == corAns:
                event.clearEvents()
                return True
            if thrAns != corAns:
                event.clearEvents()
                return False

def makeYesnos(nYes=10, nNos=10):
    """Creates a randomly shuffled array of True and False values.

    Parameters
    ----------
    nYes : int
        Number of True's in the array
    nNos : int
        Number of False's in the array
    """

    yes_nos = [True] * nYes + [False] * nNos
    np.random.shuffle(yes_nos)

    return yes_nos

def trialByType(window, type, iTrials, data):
    """Depending on the type argument given, runs the correct type of experimental trial.

    Parameters
    ----------
    type : string
        What type of experimental trial is this
        Could be one of:
            "S" - for SSVEP
            "TMI" - for traditional motor imagery
            "LMI" - for laryngeal motor imagery
    window : obj
        Visual window object.
    iTrials : int
        Current trial number.
    Notes
    -------
        Press q and p during the trial to exit
    """
    global yes_nos

    #show trial number
    if type == "S":
        fulType = "SSVEP"
    if type == "TMI":
        fulType = "Traditional Motor Imagery"
    if type == "LMI":
        fulType = "Laryngeal Motor Imagery"

    window.flip()
    trialNumStim = visual.TextStim(win=window, text=fulType + " Trial #" + str(iTrials) + ": Is the Elephant in the box?", pos=(-.3, .8))
    trialNumStim.draw()
    trialNumStim.autoDraw = True

    window.flip()

    if type == "S":
        #present the stimulus
        if yes_nos[iTrials-1] == True:
            elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
            elephantStim.autoDraw = True
            boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))
            boxStim.autoDraw = True
        if yes_nos[iTrials-1] == False:
            elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
            elephantStim.autoDraw = True
            boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor=(252, 3, 32))
            boxStim.autoDraw = True

        elephantStim.draw()
        boxStim.draw()

        window.flip()

        check = checkAns(window, yes_nos, iTrials)

        if check == True:
            window.flip()
            start, stop = ssvepStim(window)
            data.onsets.append(start)
            data.durations.append(stop - start)
            data.descriptions.append(yes_nos[iTrials-1])
            elephantStim.autoDraw = False
            boxStim.autoDraw = False
            trialNumStim.autoDraw = False

            window.flip()

        if check == False:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(.5)
            window.flip()
            event.clearEvents()
            elephantStim.autoDraw = False
            boxStim.autoDraw = False
            window.flip()
            trialByType(window, "S", iTrials)


        #ask for the correct answer via SSVEP response
            #present the ssvep stimuli and record this time for annotations


    if type == "TMI":
        #present the stimulus
        if yes_nos[iTrials-1] == True:
            elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
            boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))
        if yes_nos[iTrials-1] == False:
            elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
            boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor=(252, 3, 32))

        elephantStim.draw()
        boxStim.draw()

        window.flip()

        check = checkAns(window, yes_nos, iTrials)

        if check == True:
            window.flip()
            tmiStart, tmiStop = miPrompt(window, "t")
            trialNumStim.autoDraw = False

        if check == False:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(.5)
            window.flip()
            event.clearEvents()
            trialByType(window, "TMI", iTrials)

        #ask for the correct answer via TMI response

    if type == "LMI":
        #present the stimulus
        if yes_nos[iTrials-1] == True:
            elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
            boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))
        if yes_nos[iTrials-1] == False:
            elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
            boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor=(252, 3, 32))

        elephantStim.draw()
        boxStim.draw()

        window.flip()

        check = checkAns(window, yes_nos, iTrials)

        if check == True:
            window.flip()
            lmiStart, lmiStop = miPrompt(window, "l")
            trialNumStim.autoDraw = False

        if check == False:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(.5)
            window.flip()
            event.clearEvents()
            trialByType(window, "LMI", iTrials)

        #ask for the correct answer via LMI response

def waitForArrow(window):
    """Waits for input and flips the window when the arrow keys are pressed, or exits the program if X is pressed.

    Parameters
    ----------
    window : obj
        Visual window object.
    """
    #draw stimuli on the bottom of the page to prompt the participant to move forward

    moveFrwdText = "To move on press the space bar or X to Exit"
    moveFrwdStim = visual.TextStim(win=window, text=moveFrwdText, pos=(0, -.9), color="black")
    moveFrwdStim.draw()
    window.flip(clearBuffer=False)

    while True:
        keys = getKeys()
        #if len(keys) > 0:
        #     print(keys)
        #     break
        if 'space' in keys:
            window.flip()
            break
        if 'x' in keys:
            window.close()
            sys.exit(0)

def getKeypress(window):
    """Gets keypresses from the keyboard.

    Parameters
    ----------
    window : obj
        Visual window object.
    """

    keys = event.getKeys()
    if keys:
        print(keys[0])
        return keys[0]
    else:
        print("not what I wanted")
        return None


def trials(window, nSsvepTrials, nMiTrials, nLmiTrials):
    """Runs the experimental protocol for the trial section of the experiment.

    Parameters
    ----------
    window : obj
        Visual window object.
    nSsvepTrials : int
        The number of SSVEP trials to repeat.
    nMiTrials : int
        The number of traditional MI trials to repeat.
    nLmiTrials : int
        The number of laryngeal MI trials to repeat.
    """
    global yes_nos
    yes_nos =  makeYesnos(5, 5) + makeYesnos(5, 5) + makeYesnos(5, 5)
    iTrials = 1 #the current trial number intialized to 1

    #repeat the number of ssvep trials
    while iTrials <= nSsvepTrials:
        #trialByType(window, "S", iTrials, data)######################################
        iTrials = iTrials + 1

    #iTrials = 1
    #repeat the number of traditional MI trials
    while iTrials <= iTrials + nMiTrials:
        #trialByType(window, "TMI", iTrials, data)######################################
        iTrials = iTrials + 1

    #repeat the number of laryngeal MI trials
    while iTrials <= iTrials + nLmiTrials:
        trialByType(window, "LMI", iTrials, data)######################################
        iTrials = iTrials + 1

    return 1

def example(window):
    """Runs the experimental protocol for the example stimuli section of the experiment.

    Parameters
    ----------
    window : obj
        Visual window object.
    """

    exText1 = "The following is an example of how a trial will run"

    exText1_Stim = visual.TextStim(win=window, text=exText1)
    exText1_Stim.draw()
    waitForArrow(window)

    exText2 = "At the beginning of each trial you will be shown a stimulus like..."

    exText2_Stim = visual.TextStim(win=window, text=exText2)
    exText2_Stim.draw()

    waitForArrow(window)

    exText3 = "this"
    exText3_Stim = visual.TextStim(win=window, text=exText3, pos=(0, .7))
    elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
    boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))
    corAns = "Yes"
    corAns_Stim = visual.TextStim(win=window, text=corAns, pos=(0, -.5))

    exText3_Stim.draw()
    corAns_Stim.draw()
    elephantStim.draw()
    boxStim.draw()

    waitForArrow(window)


    exText4 = "or this"
    exText4_Stim = visual.TextStim(win=window, text=exText4, pos=(0, .7))
    elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
    boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor=(252, 3, 32))
    corAns = "NO"
    corAns_Stim = visual.TextStim(win=window, text=corAns, pos=(0, -.7))

    exText4_Stim.draw()
    corAns_Stim.draw()
    elephantStim.draw()
    boxStim.draw()

    waitForArrow(window)

    return 1

def instructions(window):
    """Runs the experimental protocol for the instructions section of the experiment.

    Parameters
    ----------
    window : obj
        Visual window object.
    """
    instrctsTxt_1 = "As you go through this experiment you will answer yes or no to a simple question. You will see an elephant pop up on the screen. The elephant will either be inside of a box or not."

    instrctsTxt_2 = "You will then be asked: 'Was the elephant in the box?' Please click the right arrow (->) to respond yes or  the left arrow (<-) to respond no."

    instrctsTxt_3 = "Only after you have responded correctly will you respond again by looking at the flashing light on the right to respond yes, or the flashing light on the left to respond no."

    instrctsTxt = instrctsTxt_1 + instrctsTxt_2 + instrctsTxt_3

    instrct_stim = visual.TextStim(window, text=instrctsTxt_1)

    instrct_stim.draw()



    waitForArrow(window)

    instrct_stim.text = instrctsTxt_2

    instrct_stim.draw()

    waitForArrow(window)

    instrct_stim.text = instrctsTxt_3

    instrct_stim.draw()

    waitForArrow(window)


    return 1

def protocol(window):
    """Runs the modules in the experimental protocol.

    Parameters
    ----------
    window : obj
        Visual window object.
    """

    data = expData()

    instructions(window)
    example(window)
    trials(window, 10, 10, 10, data)

    waitForArrow(window)
    window.close()

def main():
    """Main function for running the experimental protocol.
    """
    #t = timeData()
    window = visual.Window()
    protocol(window)
    return 1




main()
core.quit()
