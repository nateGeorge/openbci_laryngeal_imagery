import time
import sys
import numpy as np
import pandas as pd
from psychopy import visual, core, event
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal
from psychopy.event import Mouse, getKeys
from psychopy.visual import Window

def checkAns():
    """Checks to see if the correct answer was given to the primary stage of the experimental trial.

    Returns
    -------
    bool
        Returns true if the answer was correct and false if the answer was incorrect
    """

    #present instructions for keypress responses: -> for yes and <- for no
    #while loop for getting keys
        #
    while True:
        keys = getKeys()

        if 'right' in keys:
            return True
        if 'left' in keys:
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
    print(yes_nos)

    return yes_nos


def trialByType(window, type):
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
    """

    if type == "S":
        #present the stimulus
        elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
        boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))

        elephantStim.draw()
        boxStim.draw()
        window.flip()

        #ask/wait for the correct answer via the keyboard arrows
            #if the incorrect answer is given, represent the stimulus and ask for the correct answer via the keyboard again
            #if the correct answer is given, go on

        waitForArrow(window)

        #ask for the correct answer via SSVEP response

    if type == "TMI":
        print("hello " + type)
        #present the stimulus
        #ask for the correct answer via the keyboard arrows
            #if the incorrect answer is given, represent the stimulus and ask for the correct answer via the keyboard again
            #if the correct answer is given, go on
        #ask for the correct answer via TMI response

    if type == "LMI":
        print("hello " + type)
        #present the stimulus
        #ask for the correct answer via the keyboard arrows
            #if the incorrect answer is given, represent the stimulus and ask for the correct answer via the keyboard again
            #if the correct answer is given, go on
        #ask for the correct answer via LMI response


def waitForArrow(window):
    """Waits for input and flips the window when the arrow keys are pressed, or exits the program if X is pressed.

    Parameters
    ----------
    window : obj
        Visual window object.
    """

    #draw stimuli on the bottom of the page to prompt the participant to move forward
    moveFrwdText = "To move on press the right arrow or X to Exit"
    moveFrwdStim = visual.TextStim(win=window, text=moveFrwdText, pos=(0, -.9), color="black")
    moveFrwdStim.draw()
    window.flip(clearBuffer=False)

    while True:
        keys = getKeys()
        #if len(keys) > 0:
        #     print(keys)
        #     break
        if 'right' in keys:
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



def startBCI(serialPort='COM4', wifi=False):
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

    return board


def stopBCI(board):
    """Stops the openBCI datastream and disconnects the headset

        Parameters
        ----------
        board : obj
            OpenBCI connection object.

    """

    data = board.get_board_data()
    board.stop_stream()
    #board.release_session() #this is for disconnecting the headset



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
    iTrials = 1 #the current trial number intialized to 1

    #repeat the number of ssvep trials
    while iTrials <= nSsvepTrials:
        trialByType(window, "S")
        iTrials = iTrials + 1

    iTrials = 1
    #repeat the number of traditional MI trials
    while iTrials <= nMiTrials:
        trialByType(window, "TMI")
        iTrials = iTrials + 1

    iTrials = 1
    #repeat the number of laryngeal MI trials
    while iTrials <= nLmiTrials:
        trialByType(window, "LMI")
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
    instrctsTxt_1 = "As you go through this experiment you will answer yes or no to a simple question. You will see an elephant pop up on the screen. The elephant will either be inside of the box or not."

    instrctsTxt_2 = "You will then be asked: 'Was the elephant in the box?' Please click the right arrow (->) to respond yes or  the left arrow (<-) to respond no."

    instrctsTxt_3 = "After you have responded correctly you will respond again by looking at the flashing light on the right to respond yes, or the flashing light on the left to respond no."

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

    instructions(window)
    example(window)
    trials(window, 10, 10, 10)

    waitForArrow(window)
    window.close()

def main():
    """Main function for running the experimental protocol.
    """

    window = visual.Window()
    protocol(window)
    return 1

makeYesnos(3, 3)
main()
core.quit()
