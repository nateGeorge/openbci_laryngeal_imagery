import time
import datetime
import sys
import os
import pickle

import mne
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal
from psychopy import visual, core, event
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window
from psychopy import gui
from PyQt5 import QtCore


# elephant image and mask
EL_IMG = "media/lemmling-2D-cartoon-elephant.jpg"
EL_MASK = "media/lemmling-2D-cartoon-elephant-transparency-mask.jpg"

class trialData:
    """ This is a class that stores trial data.

    Attributes
    ----------
    onset : int
        The time the labeled data started being recorded.
    duration : int
        The duration of the trial data.
    Label : string
        A string corresponding to the type of data being recorded.
        Could be one of:
            S - ssvep
            T - traditional motor imagery
            L - laryngeal motor imagery
    """
    def __init__(self, onset, duration, description, label, flag=""):
        # self.startTime = startTime
        # self.stopTime = stopTime if stopTime != 0 else None
        # self.label = label
        self.onset = onset
        self.stopTime = 0
        self.duration = duration
        self.description = description
        self.label = label
        self.flag = flag


class expData:
    """ This is a class to store the important information about the experiment for when the experiment is over.

    Attributes
    ----------
    rawEEG : obj
        An mne object that stores the raw EEG data.
    expDate : obj
        A datetime.date object which stores the date.
    participantID : int
        An int containing the participant's.
    descriptions : bool
        A boolean to represent yes or no; True equals yes.
    label : str
        A string describing the type of trial.
        Could be one of:
            SSVEP - steady-state visually evoked potentials
            TMI - tradition motor imagery
            LMI - laryngeal motor imagery
    """
    def __init__(self):
        #create parameters required in the init function which record the following
        #important times
        #the eeg data
        #the date and time
        self.dataTrials = []
        self.frstOnset = None
        self.ID = None

    def addTrial(self, onset, duration, description, label):
        if hasattr(self, "dataTrials") != True:
            print("created first trial in dataTrials")
            self.dataTrials = [trialData(onset, duration, description, label)]
        else:
            print("appended dataTrials")
            self.dataTrials.append(trialData(onset, duration, description, label))

    def addFrstOnset(self, frstOnset):
        self.frstOnset = frstOnset

    def startBCI(self, brd, serialPort):
        """Starts the connection/stream of the openBCI headset

        Parameters
        ----------
        brd : str
            Type of board connection to be used.
            Could be one of:
                "Synthetic"
                "Bluetooth"
                "WiFi"
        serialPort : str
            The serial port for connecting to the headset via bluetooth.
            Could be one of:
                COM4
                COM3
                /dev/ttyUSB0
        """
        #connect to headset
        params = BrainFlowInputParams()

        # cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
        # bluetooth is 2
        if brd == "WiFi":
            params.ip_address = '10.0.0.220'
            params.ip_port = 6227
            board = BoardShim(6, params)
            self.sfreq = 1000
        elif brd == "Synthetic":
            board = BoardShim(-1, params)
            self.sfreq = 250
        elif brd == "Bluetooth":
            params.serial_port = serialPort
            board = BoardShim(2, params)
            self.sfreq = 125


        board.prepare_session()
        # by default stores 7.5 minutes of data; change num_samples higher for more
        # sampling rate of 1k/s, so 450k samples in buffer
        board.start_stream()
        time.sleep(3)
        self.board = board

    def stopBCI(self, sensor_locations='LMI1'):
        """Stops the openBCI datastream and disconnects the headset

            Parameters
            ----------
            sensor_locations : str
                Determines the sensor location dictionary to use. One of
                'default', 'LMI1'

        """
        # wait a few seconds to have extra data padded at the end for filtering
        time.sleep(3)
        rawData = self.board.get_board_data()
        self.board.stop_stream()
        # this is for disconnecting the headset
        self.board.release_session()

        if sensor_locations == 'default':
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
        elif sensor_locations == 'LMI1':
            number_to_1020 = {1: 'FC1',
                                2: 'FC2',
                                3: 'C3',
                                4: 'C4',
                                5: 'FC5',
                                6: 'FC6',
                                7: 'O1',
                                8: 'O2',
                                9: 'F7',
                                10: 'F8',
                                11: 'F3',
                                12: 'F4',
                                13: 'T3',
                                14: 'T4',
                                15: 'PO3',
                                16: 'PO4'}

        ch_types = ['eeg'] * 16
        ch_names = list(number_to_1020.values())

        info = mne.create_info(ch_names=ch_names,
                            sfreq=self.sfreq,
                            ch_types=ch_types)

        raw = mne.io.RawArray(rawData[1:17], info)

        # create annotations MNE object and attach to data
        onsets_list = [(t.onset - rawData[-1,0]) for t in self.dataTrials]
        durations_list = [t.duration for t in self.dataTrials]
        desc_list = ['-'.join([str(t.description), t.label, t.flag]) for t in self.dataTrials]
        annot = mne.Annotations(onsets_list, durations_list, desc_list)

        raw.set_annotations(annot)

        # set channel locations
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage)

        # save MNE fif file and raw data as pickle file
        raw.save(f"data/BCIproject_trial-{self.ID}_raw.fif.gz")
        with open(f"data/BCIproject_trial-{self.ID}.pk", "wb") as f:
            pickle.dump(rawData, f)


def chkDur(window, data, iTrials, threshold=.1):
    """Checks to see if the duration of the ssvep stimulus is the correct length.
    Parameters
    ----------
        window : obj
            Visual window object.
        data : obj
            Object containing data about the experiment; particularly the duration of trials.
        threshold : flt
            A floating point number representing the displacement from 5 seconds that the trial should have.
    Returns
    -------
        status : str
            Returns status if the duration is not between 4.9 and 5 seconds long.
            Could be one of:
                - "WARNING: The SSVEP was too long"
                - "WARNING: The SSVEP was too short"
            OR
        int
            Returns 1 if the duration was between 4.9 seconds and 5 seconds long.
    """
    if data.dataTrials[iTrials - 1].duration > 5 + threshold:
        status = "WARNING: The SSVEP was too long"
        data.dataTrials[iTrials - 1].flag = "too long"
        print(data.dataTrials[iTrials - 1].flag)
        return status
    elif data.dataTrials[iTrials - 1].duration < 5 - threshold:
        status = "WARNING: The SSVEP was too short"
        data.dataTrials.flag = "too short"
        print(data.dataTrials.flag)
        return status


def miPrompt(window, miType):
    """Presents the prompt for the traditional motor imagery (TMI) response.

    Parameters
    ----------
    window : obj
        Psychopy window object.
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
        responseInstr = ["imagine raising your right arm",
                        "imagine raising your left arm"]
    elif miType == "l":
        responseInstr = ["imagine making a high-pitch sound",
                        "imagine making a low-pitch sound"]

    #present a prompt that asks the participant to think about raising their right arm for yes and left arm for no
    tmiPromptText_1 = f"For YES, {responseInstr[0]} for {str(holdTime)} seconds."
    tmiPromptStim_1 = visual.TextStim(win=window,
                                    text=tmiPromptText_1,
                                    pos=(0.5, 0.3),
                                    wrapWidth=.5)
    tmiPromptText_2 = f"For NO, {responseInstr[1]} for {str(holdTime)} seconds."
    tmiPromptStim_2 = visual.TextStim(win=window,
                                    text=tmiPromptText_2,
                                    pos=(-0.5, 0.3),
                                    wrapWidth=.5)

    tmiPromptStim_1.draw()
    tmiPromptStim_2.draw()
    window.flip()

    start = time.time()
    time.sleep(holdTime)
    stop = time.time()

    window.flip()

    return start, stop


def ssvepVideo(window, frequency_1=7, frequency_2=12):
    """Checks to see if the duration of the ssvep stimulus is the correct length.
    Parameters
    ----------
        window : obj
            Psychopy window object.
        frequency_1 : int
            The frequency of SSVEP which will be displayed on the right as the YES response.
        frequency_2 : int
            The frequency of SSVEP which will be displayed on the left as the NO response.
    Returns
    -------
        start : flt
            The start time of the SSVEP video.
        end : flt
            The end time of the SSVEP video
    """
    # 7 Hz is on the right so it represents yes
    win_size = window.size
    # size and location of movies
    dim = 0.5 * win_size[1]
    placement = 0.3 * win_size[0]

    ssvep_right = visual.MovieStim3(window,
                            f'media/f{str(frequency_1)}Hz.avi',
                            size=(dim, dim), 
                            pos=[placement, 0])
    ssvep_left = visual.MovieStim3(window,
                            f'media/f{str(frequency_2)}Hz.avi',
                            size=(dim, dim),
                            pos=[-placement, 0])

    start = time.time()
    while ssvep_left.status != -1:
        ssvep_left.draw()
        ssvep_right.draw()
        window.flip()

    end = time.time()

    return start, end


def ssvepStim(window):
    """Presents the SSVEP flashing stimuli

    Parameters
    ----------
    window : obj
        Psychopy window object.

    Returns
    -------
    list of floats
        the times the ssvep stimulus started and time it ended
    """
    # win_size = window.size
    square1 = visual.Rect(win=window,
                        size=(0.5, 0.5),
                        pos=(-0.6, 0),
                        fillColor='white',
                        opacity=0,
                        autoDraw=True)
    square2 = visual.Rect(win=window,
                        size=(0.5, 0.5),
                        pos=(0.6, 0),
                        fillColor='white',
                        opacity=0,
                        autoDraw=True)

    start, end = ssvepVideo(window)

    # square1.autoDraw = False
    # square2.autoDraw = False
    window.flip()
    return start, end


def checkAns(window, yes_nos, iTrials):
    """Checks to see if the correct answer was given to the primary stage of the experimental trial.
    Parameters
    ----------
    window : obj
        Psychopy window object.
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


def makeYesnos(nYes, nNos):
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


def trialByType(window, yes_nos, type, iTrials, data):
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
        Psychopy window object.
    iTrials : int
        Current trial number.
    Notes
    -------
        Press q and p during the trial to exit
    """
    elephantStim = visual.ImageStim(win=window,
                                pos=((0, 0.25)),
                                image=EL_IMG,
                                mask=EL_MASK,
                                size=0.4)
    #show trial number
    if type == "S":
        fulType = "SSVEP"
    if type == "TMI":
        fulType = "Traditional Motor Imagery"
    if type == "LMI":
        fulType = "Laryngeal Motor Imagery"

    window.flip()
    text = f'{fulType} Trial #{str(iTrials)}: Is the Elephant in the box?'
    trialNumStim = visual.TextStim(win=window,
                                text=text,
                                pos=(-.3, .8))
    trialNumStim.draw()

    if type == "S":
        #present the stimulus
        if yes_nos[iTrials-1] == True:
            boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
        elif yes_nos[iTrials-1] == False:
            boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()
        window.flip()
        check = checkAns(window, yes_nos, iTrials)

        if check == True:
            window.flip()
            ssvepStart, ssvepStop = ssvepStim(window)
            data.trials = trialData(ssvepStart,
                                    ssvepStop - ssvepStart,
                                    yes_nos[iTrials-1],
                                    "SSVEP")
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            ssvepStart, ssvepStop = trialByType(window, yes_nos, "S", iTrials, data)

        return ssvepStart, ssvepStop

    if type == "TMI":
        #present the stimulus
        if yes_nos[iTrials-1] == True:
            boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor="red")
        elif yes_nos[iTrials-1] == False:
            boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()
        window.flip()
        check = checkAns(window, yes_nos, iTrials)

        if check == True:
            window.flip()
            tmiStart, tmiStop = miPrompt(window, "t")
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            tmiStart, tmiStop = trialByType(window, yes_nos, "TMI", iTrials, data)
            window.flip()

        return tmiStart, tmiStop

    if type == "LMI":
        #present the stimulus
        if yes_nos[iTrials-1] == True:
            boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor="red")
        if yes_nos[iTrials-1] == False:
            boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()
        window.flip()
        check = checkAns(window, yes_nos, iTrials)

        if check == True:
            window.flip()
            lmiStart, lmiStop = miPrompt(window, "l")
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            lmiStart, lmiStop = trialByType(window, yes_nos, "LMI", iTrials, data)
            window.flip()

        return lmiStart, lmiStop


def waitForArrow(window):
    """Waits for input and flips the window when the arrow keys are pressed,
    or exits the program if X is pressed.

    Parameters
    ----------
    window : obj
        Psychopy window object.
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
        Psychopy window object.
    """
    keys = event.getKeys()
    if keys:
        print(keys[0])
        return keys[0]
    else:
        print("not what I wanted")
        return None


def trials(window, nSsvepTrials, nMiTrials, nLmiTrials, data, debug=False):
    """Runs the experimental protocol for the trial section of the experiment.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    nSsvepTrials : int
        The number of SSVEP trials to repeat.
            * MUST BE EVEN
    nMiTrials : int
        The number of traditional MI trials to repeat.
            * MUST BE EVEN
    nLmiTrials : int
        The number of laryngeal MI trials to repeat.
            * MUST BE EVEN
    data : obj
        This is the expData class object which will hold the important
        data for the experiment.
    debug : bool
        True for printing debug statements.
    """
    yes_nos =  makeYesnos(nSsvepTrials//2, nSsvepTrials//2) + \
                makeYesnos(nMiTrials//2, nMiTrials//2) + \
                makeYesnos(nLmiTrials//2, nLmiTrials//2)
    iTrials = 1  # the current trial number intialized to 1

    # repeat the number of ssvep trials
    while iTrials <= nSsvepTrials:
        start, stop = trialByType(window, yes_nos, "S", iTrials, data)
        data.addTrial(start, (stop - start), yes_nos[iTrials - 1], "SSVEP")

        if debug:
            print("onset is: " + str(data.dataTrials[iTrials - 1].onset))
            print("duration is: " + str(data.dataTrials[iTrials - 1].duration))
            print("description is: " + str(data.dataTrials[iTrials - 1].description))
            print("label is: " + str(data.dataTrials[iTrials - 1].label))

        slowSsvepTxt = chkDur(window, data, iTrials)

        if type(slowSsvepTxt) == str:
            slowSsvepStim = visual.TextStim(win=window, text=slowSsvepTxt, color="red")
            slowSsvepStim.draw()
            window.flip()
            time.sleep(2)
        
        iTrials = iTrials + 1

    text = """
    We will now move to motor imagery.
    The same stimuli will be presented.
    If the elephant is in the box, press the right arrow key
    and imagine lifting your right arm until 'done' displays.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    # repeat the number of traditional MI trials
    while iTrials <= nSsvepTrials + nMiTrials:
        start, stop = trialByType(window, yes_nos, "TMI", iTrials, data)
        data.addTrial(start, (stop - start), yes_nos[iTrials - 1], "TMI")
        if debug:
            print("onset is: " + str(data.dataTrials[iTrials - 1].onset))
            print("duration is: " + str(data.dataTrials[iTrials - 1].duration))
            print("description is: " + str(data.dataTrials[iTrials - 1].description))
            print("label is: " + str(data.dataTrials[iTrials - 1].label))
        iTrials = iTrials + 1

    text = """
    We will now move to larnygeal imagery.
    The same stimuli will be presented.
    If the elephant is in the box, press the right arrow key
    and imagine making a humming sound until 'done' displays.
    If the elephant is not in the box, simply wait.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    # repeat the number of laryngeal MI trials
    while iTrials <= nSsvepTrials + nMiTrials + nLmiTrials:
        start, stop = trialByType(window, yes_nos, "LMI", iTrials, data)
        data.addTrial(start, (stop - start), yes_nos[iTrials - 1], "LMI")
        if debug:
            print("onset is: " + str(data.dataTrials[iTrials - 1].onset))
            print("duration is: " + str(data.dataTrials[iTrials - 1].duration))
            print("description is: " + str(data.dataTrials[iTrials - 1].description))
            print("label is: " + str(data.dataTrials[iTrials - 1].label))
        iTrials = iTrials + 1


def example(window):
    """Runs the experimental protocol for the example stimuli section of the experiment.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    """
    elephantStim = visual.ImageStim(win=window,
                                pos=((0, 0.25)),
                                image=EL_IMG,
                                mask=EL_MASK,
                                size=0.4)

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
    exText3_Stim.draw()    

    boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
    boxStim.draw()
    elephantStim.draw()

    corAns = "YES"
    corAns_Stim = visual.TextStim(win=window, text=corAns, pos=(0, -0.5))
    corAns_Stim.draw()

    waitForArrow(window)

    exText4 = "or this"
    exText4_Stim = visual.TextStim(win=window, text=exText4, pos=(0, 0.7))
    exText4_Stim.draw()

    boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")
    boxStim.draw()
    elephantStim.draw()
    
    corAns = "NO"
    corAns_Stim = visual.TextStim(win=window, text=corAns, pos=(0, -0.7))
    corAns_Stim.draw()

    waitForArrow(window)


def instructions(window):
    """Runs the experimental protocol for the instructions section of the experiment.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    """
    instrctsTxt_1 = """As you go through this experiment you
    will answer yes or no to a simple question.
    You will see an elephant pop up on the screen.
    The elephant will either be inside of a box or not.
    """
    instrctsTxt_2 = """You will then be asked: 'Was the elephant
    in the box?' Please click the right arrow (->) to respond yes
    or the left arrow (<-) to respond no.
    """
    instrctsTxt_3 = """Only after you have responded correctly will
    you respond again by looking at the flashing light on the right
    to respond yes, or the flashing light on the left to respond no.
    """
    instrct_stim = visual.TextStim(window, text=instrctsTxt_1)
    instrct_stim.draw()
    waitForArrow(window)
    instrct_stim.text = instrctsTxt_2
    instrct_stim.draw()
    waitForArrow(window)
    instrct_stim.text = instrctsTxt_3
    instrct_stim.draw()
    waitForArrow(window)


def run_experiment(debug=False):
    """
    Runs experiment for data collection.

    Parameters
    ----------
    debug : bool
        If True, prints debug statements and makes window non-fullscreen.
        If False, does not print debug statements and makes window fullscreen.
    """
    data = expData()

    while True:
        dlg = gui.Dlg(title="BCI Experiment")
        exp_id = dlg.addField('Experiment ID Number: ')
        dlg.addField('Board Type:', choices=["Bluetooth", "WiFi", "Synthetic"])
        dlg.addField('Serial Port (bluetooth only):', "COM4")
        # for Windows, this brings the dialogue to the front of the screen
        dlg.setWindowFlags(dlg.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        exp_id.setFocus()  # start with cursor on experiment ID field
        settings = dlg.show()  # show dialog and wait for OK or Cancel
        if dlg.OK:  # or if ok_data is not None
            data.ID = settings[0]
            if f"BCIproject_trial-{data.ID}.pk" in os.listdir('data'):
                dlg = gui.Dlg(title="Error")
                dlg.addText(f'Error: data with this trial number {data.ID} already exists.')
                dlg.setWindowFlags(dlg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                dlg.show()
                continue
            if settings[0] != '':
                break
            else:
                dlg = gui.Dlg(title="Error")
                dlg.addText('Please enter a valid number for the trial.')
                dlg.setWindowFlags(dlg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
                dlg.show()
        else:  # clicked cancel
            print('cancelling experiment')
            return

    data.startBCI(settings[1], settings[2])

    if debug:
        window = visual.Window()
    else:
        window = visual.Window(fullscr=True)
    
    instructions(window)
    example(window)
    trials(window, 2, 2, 2, data, debug=debug)
    window.close()
    data.stopBCI()


if __name__ == '__main__':
    run_experiment()
    core.quit()
