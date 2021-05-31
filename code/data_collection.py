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
from psychopy import visual, core, event, sound
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
            "Alpha" - for alpha wave detection
            "S" - for SSVEP
            "TMI-a" - for motor activity (actual)
            "TMI-i" - for traditional motor imagery (imagined)
            "LMI-a" - for laryngeal activity (actual)
            "LMI-i" - for laryngeal motor imagery (imagined)
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
            "Alpha" - for alpha wave detection
            "S" - for SSVEP
            "TMI-a" - for motor activity (actual)
            "TMI-i" - for traditional motor imagery (imagined)
            "LMI-a" - for laryngeal activity (actual)
            "LMI-i" - for laryngeal motor imagery (imagined)
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
            params.ip_address = '192.168.4.1'#'10.0.0.220'
            params.ip_port = 6229
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

    def stopBCI(self, sensor_locations='LMI2'):
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
        elif sensor_locations == 'LMI2':
            number_to_1020 = {1: 'Fp1',
                                2: 'Fp2',
                                3: 'CP1',
                                4: 'CP2',
                                5: 'FC1', #change to FC1
                                6: 'FC2', #change to FC2
                                7: 'O1',
                                8: 'O2',
                                9: 'F7',
                                10: 'F8',
                                11: 'Fz',
                                12: 'Cz',
                                13: 'T3',
                                14: 'T4',
                                15: 'P3',
                                16: 'P4'}

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
    if data.dataTrials[iTrials].duration > 5 + threshold:
        status = "WARNING: The SSVEP was too long"
        data.dataTrials[iTrials].flag = "too long"
        print(data.dataTrials[iTrials].flag)
        return status
    elif data.dataTrials[iTrials].duration < 5 - threshold:
        status = "WARNING: The SSVEP was too short"
        data.dataTrials.flag = "too short"
        print(data.dataTrials.flag)
        return status


def showMIinstructions(window, miType, holdTime):
    """Presents instructions for the traditional motor imagery (TMI) response.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    miType : string
        Type of motor imagery which needs to be prompted
        Could be one of:
            m-i - motor imagery
            l-i - laryngeal imagery
            m-a - motor movement
            l-a - laryngeal actuation
    """
    if miType == 'm-i':
        responseInstr = ["imagine raising your right arm",
                    "rest and wait"]
    elif miType == 'l-i':
        responseInstr = ["imagine making a humming sound",
                        "rest and wait"]
    elif miType == 'm-a':
        responseInstr = ["raise your right arm",
                    "rest and wait"]
    elif miType == 'l-a':
        responseInstr = ["make a humming sound",
                        "rest and wait"]

    #present a prompt that asks the participant to think about raising their right arm for yes and left arm for no
    tmiPromptText_1 = f"For YES, {responseInstr[0]} for {str(holdTime)} seconds."
    tmiPromptStim_1 = visual.TextStim(win=window,
                                    text=tmiPromptText_1,
                                    pos=(0.5, 0),
                                    wrapWidth=0.5)
    tmiPromptText_2 = f"For NO, {responseInstr[1]} for {str(holdTime)} seconds."
    tmiPromptStim_2 = visual.TextStim(win=window,
                                    text=tmiPromptText_2,
                                    pos=(-0.5, 0),
                                    wrapWidth=0.5)

    tmiPromptStim_1.draw()
    tmiPromptStim_2.draw()


def miPrompt(window, miType, holdTime):
    """Presents the prompt for the traditional motor imagery (TMI) response.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    miType : string
        Type of motor imagery which needs to be prompted
        Could be one of:
            m-i - motor imagery
            l-i - laryngeal imagery
            m-a - motor movement
            l-a - laryngeal actuation

    Returns
    -------
    list of floats
        the times the TMI response started and time it ended
    """
    if miType == 'm-i':
        text = "Imagine raising right arm or rest."
    elif miType == 'l-i':
        text = "Imagine making a noise or rest."
    elif miType == 'm-a':
        text = "Raise right arm or rest."
    elif miType == 'l-a':
        text = "Make a humming sound or rest."

    tStim = visual.TextStim(window, text=text)
    tStim.draw()
    window.flip()

    start = time.time()
    time.sleep(holdTime)
    stop = time.time()

    window.flip()
    text = "Done."
    tStim = visual.TextStim(window, text=text)
    tStim.draw()
    window.flip()
    time.sleep(1)


    return start, stop


def ssvepVideo(window, frequency_1=10, frequency_2=15, ansWinOnly=True, ansSide=None):
    """Checks to see if the duration of the ssvep stimulus is the correct length.
    Parameters
    ----------
        window : obj
            Psychopy window object.
        frequency_1 : int
            The frequency of SSVEP which will be displayed on the right as the YES response.
        frequency_2 : int
            The frequency of SSVEP which will be displayed on the left as the NO response.
        ansWinOnly : bool
            If true, only the correct answer flashing window shows.
        ansSide : str
            If ansSide is left, the left video is displayed. If ansSide is right, the right video is displayed
    Returns
    -------
        start : flt
            The start time of the SSVEP video.
        end : flt
            The end time of the SSVEP video
    """
    # 10 Hz (used to be 7 Hz) is on the right so it represents yes or True
    # 15Hz on the left (used to be 12 Hz)
    win_size = window.size
    # size and location of movies
    dim = 0.5 * win_size[1]
    placement = 0.3 * win_size[0]

    ssvep_right = visual.MovieStim3(window,
                            f'media/{frequency_1}Hz.avi',
                            size=(dim, dim),
                            pos=[placement, 0])
    ssvep_left = visual.MovieStim3(window,
                            f'media/{frequency_2}Hz.avi',
                            size=(dim, dim),
                            pos=[-placement, 0])

    start = time.time()

    if ansSide == 'left':
        while ssvep_left.status != -1:
            ssvep_left.draw()
            window.flip()

    if ansSide == 'right':
        while ssvep_right.status != -1:
            ssvep_right.draw()
            window.flip()

    if ansSide == None:
        while ssvep_left.status != -1:
            ssvep_left.draw()
            ssvep_right.draw()
            window.flip() #this is a potential source of error in the frequency of the SSVEP signal

    end = time.time()

    return start, end


def ssvepStim(window, corAnsSide=None):
    """Presents the SSVEP flashing stimuli

    Parameters
    ----------
    window : obj
        Psychopy window object.
    corAnsSide: str
        The side the correct answer response is on.

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

    if corAnsSide != None:
        start, end = ssvepVideo(window, ansSide=corAnsSide)
    else:
        start, end = ssvepVideo(window)

    # square1.autoDraw = False
    # square2.autoDraw = False
    window.flip()
    return start, end


def checkAns(window, yes):
    """Checks to see if the correct answer was given to the primary stage of the experimental trial.
    Parameters
    ----------
    window : obj
        Psychopy window object.
    yes : Boolean
        T or F if response to stimulus should be yes or no
    Returns
    -------
    bool
        Returns True if the answer was correct and False if the answer was incorrect
    """
    users_answer = None

    #present instructions for keypress responses: -> for yes and <- for no

    #while loop for getting keys
        #
    while True:
        keys = getKeys()

        if 'right' in keys:
            users_answer = True
        if 'left' in keys:
            users_answer = False

        if 'q' and 'p' in keys:
            window.close()
            sys.exit(0)

        if users_answer != None:
            if users_answer == yes:
                event.clearEvents()
                return True
            else:
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


def eyes_closed(holdTime):
    """
    Parameters
    ----------
    holdTime : int or float
        number of seconds to wait

    Plays a sound, then waits for holdTime, then plays another sound.
    Returns the start time and end time (floats) in seconds UTC since the epoch.
    """
    g = sound.Sound('C', 1)
    g.play()
    start = time.time()
    time.sleep(holdTime)
    g = sound.Sound('G', 1)
    end = time.time()
    g.play()
    return start, end


def trialByType(window, yes, type, holdTime=5, SSVEP_one_win=False):
    """Depending on the type argument given, runs the correct type of experimental trial.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    yes : boolean
        True or false, whether the repsone/stimulus should be yes or no (T or F)
    type : string
        What type of experimental trial is this
        Could be one of:
            "Alpha" - for alpha wave detection
            "S" - for SSVEP
            "TMI-a" - for motor activity (actual)
            "TMI-i" - for traditional motor imagery (imagined)
            "LMI-a" - for laryngeal activity (actual)
            "LMI-i" - for laryngeal motor imagery (imagined)

    holdTime : float or int
        Number of seconds for the time the stimulus is shown.

    Notes
    -------
        Press q and p during the trial to exit
    """
    elephantStim = visual.ImageStim(win=window,
                                pos=((0, 0.25)),
                                image=EL_IMG,
                                mask=EL_MASK,
                                size=0.4)
    # for debug
    if type == "S":
        fulType = "SSVEP"
    elif type == "TMI-a":
        fulType = "Actual Motor Movement"
    elif type == "LMI-i":
        fulType = "Laryngeal Motor Imagery"
    elif type == "TMI-i":
        fulType = "Traditional Motor Imagery"
    elif type == "LMI-i":
        fulType = "Laryngeal Motor Imagery"


    if type == "alpha":
        start, end = eyes_closed(holdTime)
        return start, end


    text = f'Is the Elephant in the box?'

    window.flip()
    trialNumStim = visual.TextStim(win=window,
                                text=text,
                                pos=(-.3, .8))
    trialNumStim.draw()


    if type == "S":
        #present the stimulus
        if yes:
            boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
            corAnsSide = 'right'
        else:
            boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")
            corAnsSide = 'left'

        elephantStim.draw()
        boxStim.draw()
        window.flip()
        check = checkAns(window, yes)

        if check == True:
            window.flip()
            if SSVEP_one_win == True:
                print(SSVEP_one_win)
                ssvepStart, ssvepStop = ssvepStim(window, corAnsSide) # here is wehre I need a parameter for one window view
            else:
                ssvepStart, ssvepStop = ssvepStim(window) # this is where the none on SSVEP_one_win is coming from
            window.flip()
            return ssvepStart, ssvepStop
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            ssvepStart, ssvepStop = trialByType(window, yes, "S", SSVEP_one_win=SSVEP_one_win)


    if type == "TMI-a":
        #present the stimulus
        if yes:
            boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
        else:
            boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()

        showMIinstructions(window, 'm-a', holdTime)

        window.flip()
        check = checkAns(window, yes)

        if check == True:
            window.flip()
            tmiStart, tmiStop = miPrompt(window, "m-a", holdTime)
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            tmiStart, tmiStop = trialByType(window, yes, "TMI-a")
            window.flip()

        return tmiStart, tmiStop


    if type == "TMI-i":
        #present the stimulus
        if yes:
            boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
        else:
            boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()

        showMIinstructions(window, "m-i", holdTime)

        window.flip()
        check = checkAns(window, yes)

        if check == True:
            window.flip()
            tmiStart, tmiStop = miPrompt(window, "m-i", holdTime)
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            tmiStart, tmiStop = trialByType(window, yes, "TMI-i")
            window.flip()

        return tmiStart, tmiStop


    if type == "LMI-a":
        #present the stimulus
        if yes:
            boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
        else:
            boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()

        showMIinstructions(window, "l-a", holdTime)

        window.flip()
        check = checkAns(window, yes)

        if check == True:
            window.flip()
            lmiStart, lmiStop = miPrompt(window, "l-a", holdTime)
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            lmiStart, lmiStop = trialByType(window, yes, "LMI-a")
            window.flip()

        return lmiStart, lmiStop


    if type == "LMI-i":
        #present the stimulus
        if yes:
            boxStim = visual.Rect(win=window, pos=((0, 0.25)), lineColor="red")
        else:
            boxStim = visual.Rect(win=window, pos=((0, -0.25)), lineColor="red")

        elephantStim.draw()
        boxStim.draw()

        showMIinstructions(window, "l-i", holdTime,)

        window.flip()
        check = checkAns(window, yes)

        if check == True:
            window.flip()
            lmiStart, lmiStop = miPrompt(window, "l-i", holdTime)
            window.flip()
        else:
            retryText = "Please enter the correct answer before continuing"
            retryStim = visual.TextStim(win=window, text=retryText, color="red")
            retryStim.draw()
            window.flip()
            time.sleep(2)
            window.flip()
            event.clearEvents()
            lmiStart, lmiStop = trialByType(window, yes, "LMI-i")
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


def trials(window,
            nAlphaTrials,
            nSsvepTrials,
            nMiTrials_a,
            nMiTrials_i,
            nLmiTrials_a,
            nLmiTrials_i,
            data,
            holdTime=5,
            debug=False,
            SSVEP_one_win=False):
    """Runs the experimental protocol for the trial section of the experiment.

    Parameters
    ----------
    window : obj
        Psychopy window object.
    nAlphaTrials : int
        The number of alpha wave (eyes closed) trials to repeat.
    nSsvepTrials : int
        The number of SSVEP trials to repeat.
            * MUST BE EVEN
    nMiTrials_a : int
        The number of motor movement trials to repeat.
            * MUST BE EVEN
    nMiTrials_i : int
        The number of traditional motor imagery trials to repeat.
            * MUST BE EVEN
    nLmiTrials_a : int
        The number of laryngeal engagement trials to repeat.
            * MUST BE EVEN
    nLmiTrials_i : int
        The number of laryngeal motor imagery trials to repeat.
            * MUST BE EVEN
    data : obj
        This is the expData class object which will hold the important
        data for the experiment.
    holdTime : int or float
        time to collect data for each exp
    debug : bool
        True for printing debug statements.
    """
    text = f"""
    In the first part of the experiment, you should close your eyes when you hear the first low-pitched sound.
    When you hear the higher-pitched sound, open your eyes. This will repeat {nAlphaTrials} times.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    for i in range(nAlphaTrials):
        text = f"""Close your eyes for {holdTime} seconds when you hear the low-pitched sound,
        then open them when you hear the high-pitched sound."""
        textstim = visual.TextStim(win=window,
                                    text=text)

        textstim.draw()
        window.flip()
        eyes_open_start = time.time()
        time.sleep(holdTime)
        eyes_open_stop = time.time()
        start, stop = trialByType(window, yes=True, type='alpha')
        data.addTrial(start, (stop - start), True, 'alpha')
        data.addTrial(eyes_open_start, (eyes_open_stop - eyes_open_start), False, 'alpha')

    time.sleep(2)


    yes_nos =  makeYesnos(nSsvepTrials//2, nSsvepTrials//2) + \
                makeYesnos(nMiTrials_a//2, nMiTrials_a//2) + \
                makeYesnos(nLmiTrials_a//2, nLmiTrials_a//2) + \
                makeYesnos(nMiTrials_i//2, nMiTrials_i//2) + \
                makeYesnos(nLmiTrials_i//2, nLmiTrials_i//2)
    iTrials = i  # the current trial number intialized to 1


    text = """
    We will now move to SSVEP.
    The elephant stimuli will be presented.
    If the elephant is in the box, press the right arrow key
    and look at the flashing box on the right.
    If the elephant is out of the box, press the left arrow key,
    then look at the flashing box on the left.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    # repeat the number of ssvep trials
    for iTrial in range(nSsvepTrials):
        yes = yes_nos[iTrial]
        start, stop = trialByType(window, yes, "S", SSVEP_one_win=SSVEP_one_win)
        data.addTrial(start, (stop - start), yes, "SSVEP")

        if debug:
            print("onset is: " + str(data.dataTrials[iTrials].onset))
            print("duration is: " + str(data.dataTrials[iTrials].duration))
            print("description is: " + str(data.dataTrials[iTrials].description))
            print("label is: " + str(data.dataTrials[iTrials].label))

        slowSsvepTxt = chkDur(window, data, iTrials)

        if type(slowSsvepTxt) == str:
            slowSsvepStim = visual.TextStim(win=window, text=slowSsvepTxt, color="red")
            slowSsvepStim.draw()
            window.flip()
            time.sleep(2)

        iTrials += 1

    text = """
    We will now move to motor activity.
    The same stimuli will be presented.
    If the elephant is in the box, press the right arrow key
    and lift up your right arm until 'done' displays.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    # repeat the number of traditional motor activity trials
    for iTrial in range(nMiTrials_a):
        yes = yes_nos[iTrial]
        start, stop = trialByType(window, yes, "TMI-a")
        data.addTrial(start, (stop - start), yes, "TMI-a")
        if debug:
            print("onset is: " + str(data.dataTrials[iTrials].onset))
            print("duration is: " + str(data.dataTrials[iTrials].duration))
            print("description is: " + str(data.dataTrials[iTrials].description))
            print("label is: " + str(data.dataTrials[iTrials].label))
        iTrials += 1

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
    for iTrial in range(nMiTrials_i):
        yes = yes_nos[iTrial]
        start, stop = trialByType(window, yes, "TMI-i")
        data.addTrial(start, (stop - start), yes, "TMI-i")
        if debug:
            print("onset is: " + str(data.dataTrials[iTrials].onset))
            print("duration is: " + str(data.dataTrials[iTrials].duration))
            print("description is: " + str(data.dataTrials[iTrials].description))
            print("label is: " + str(data.dataTrials[iTrials].label))
        iTrials += 1

    text = """
    We will now move to larnygeal activity.
    The same stimuli will be presented.
    If the elephant is in the box, press the right arrow key
    and make an actual humming sound until 'done' displays.
    If the elephant is not in the box, simply rest.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    # repeat the number of laryngeal activity trials
    for iTrial in range(nLmiTrials_a):
        yes = yes_nos[iTrial]
        start, stop = trialByType(window, yes, "LMI-a")
        data.addTrial(start, (stop - start), yes, "LMI-a")
        if debug:
            print("onset is: " + str(data.dataTrials[iTrials].onset))
            print("duration is: " + str(data.dataTrials[iTrials].duration))
            print("description is: " + str(data.dataTrials[iTrials].description))
            print("label is: " + str(data.dataTrials[iTrials].label))
        iTrials = iTrials + 1

    text = """
    We will now move to larnygeal imagery.
    The same stimuli will be presented.
    If the elephant is in the box, press the right arrow key
    and imagine making a humming sound until 'done' displays.
    If the elephant is not in the box, simply rest.
    """
    text_Stim = visual.TextStim(win=window, text=text)
    text_Stim.draw()
    waitForArrow(window)

    # repeat the number of laryngeal MI trials
    for iTrial in range(nLmiTrials_i):
        yes = yes_nos[iTrial]
        start, stop = trialByType(window, yes, "LMI-i")
        data.addTrial(start, (stop - start), yes, "LMI-i")
        if debug:
            print("onset is: " + str(data.dataTrials[iTrials].onset))
            print("duration is: " + str(data.dataTrials[iTrials].duration))
            print("description is: " + str(data.dataTrials[iTrials].description))
            print("label is: " + str(data.dataTrials[iTrials].label))
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
    in the box?' Please click the right arrow (→) to respond yes
    or the left arrow (←) to respond no.
    """
    instrctsTxt_3 = """Only after you have responded correctly will
    you respond again by following the instructions for indicating yes or no.
    """
    instrctsTxt_4 = """WARNING: This experimental protocol contains flashing lights that may pose a danger to individuals who suffer from epilepsy. If you are dangerously sensitive to rapidly flashing lights, please stop the experiment now by pressing the 'x' key.
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
    instrct_stim.text = instrctsTxt_4
    instrct_stim.draw()
    waitForArrow(window)


def run_experiment(debug=True, SSVEP_one_win=False):
    """
    Runs experiment for data collection.

    Parameters
    ----------
    debug : bool
        If True, prints debug statements and makes window non-fullscreen.
        If False, does not print debug statements and makes window fullscreen.
    SSVEP_one_win : bool
        If False, both SSVEP stimuli windows show up in the SSVEP section.
        If True, only one SSVEP stimulus window shows up in the SSVEP section.
    """
    data = expData()

    while True:
        dlg = gui.Dlg(title="BCI Experiment")
        exp_id = dlg.addField('Experiment ID Number: ')
        dlg.addField('Board Type:', choices=["Bluetooth", "WiFi", "Synthetic"])
        dlg.addField('Serial Port (bluetooth only):', "COM4")
        # for Windows, this brings the dialogue to the front of the screen
        dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # potentially help bring window to the front on other OSs
        dlg.activateWindow()
        dlg.raise_()
        exp_id.setFocus()  # start with cursor on experiment ID field
        settings = dlg.show()  # show dialog and wait for OK or Cancel
        if dlg.OK:  # or if ok_data is not None
            data.ID = settings[0]
            if f"BCIproject_trial-{data.ID}.pk" in os.listdir('data'):
                dlg = gui.Dlg(title="Error")
                dlg.addText(f'Error: data with this trial number {data.ID} already exists.')
                dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                dlg.activateWindow()
                dlg.raise_()
                dlg.show()
                continue
            if settings[0] != '':
                break
            else:
                dlg = gui.Dlg(title="Error")
                dlg.addText('Please enter a valid number for the trial.')
                dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                dlg.activateWindow()
                dlg.raise_()
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
    n_trials = 2
    trials(window, n_trials, n_trials, n_trials, n_trials, n_trials, n_trials, data, debug=debug, SSVEP_one_win=SSVEP_one_win)
    # trials(window, 0, n_trials, 0, 0, 0, 0, data, debug=debug, SSVEP_one_win=SSVEP_one_win)
    window.close()
    data.stopBCI()


if __name__ == '__main__':
    run_experiment(debug=False, SSVEP_one_win=False)
    core.quit()
